import sys
sys.path.append("../")
from pprint import pprint
from os.path import abspath, join
from os import listdir, remove
import pandas as pd
import mongo_config
from mongo_config import get_tweet_html, UPLOAD_FOLDER, ALLOWED_EXTENSIONS, allowed_file
from werkzeug.utils import secure_filename
from assign_analyst import add_analyst_to_project
import smtplib
from email.mime.text import MIMEText as text
import gmail_controller
from admin_authentication import TVAdminAuthorizedCreationControls
from pymongo import MongoClient
from flask import (Flask, render_template, request, redirect, url_for, session,
                   logging, flash, g, send_from_directory, abort)
from appForms import (UserLoginForm, UserRegisterForm, CredentialRetreival, ChangeLoginInfo, AssignUserButton,
                      ProjectModifyer)

# Connect to database
Client = MongoClient(host = mongo_config.host, port = mongo_config.port,
         username = mongo_config.tv_admin, password = mongo_config.tv_admin_pwd,
         authSource=mongo_config.amdin_database)
DB = Client.TV_ADMIN
USERS = DB.USERS
# connect to authenticating controls
controls = TVAdminAuthorizedCreationControls(auth_user_name=mongo_config.tv_admin,
                                          auth_password=mongo_config.tv_admin_pwd)

app = Flask(__name__)
app.config['SECRET_KEY'] = "Conspiracy" #Change to environment variable
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# global variable to be used across the web site,
# g. can be anything or any object that might be useful in app.py or html
@app.before_request
def before_request():
    g.user = None

    if 'user' in session:
        g.user = session['user']
        g.user_projects = session['assignemnts']

@app.route('/retrievecredentials', methods=['POST','GET'])
def retrieve_cred():

    rememberCredsForm = CredentialRetreival()

    if 'forgot_user_name' in request.form:
        session['retrieval_data_type'] = 'pwd'
        session['retrieved_data_user_name'] = rememberCredsForm.forgot_user_name.data
        session['retrieved_data_email'] = rememberCredsForm.user_email.data
        return redirect(url_for('credentialConfirmation'))
    elif 'user_email' in request.form:
        session['retrieval_data_type'] = 'usr'
        session['retrieved_data'] = rememberCredsForm.user_email.data
        return redirect(url_for('credentialConfirmation'))

    return render_template('chooseCredentials.html', form=rememberCredsForm, type=rememberCredsForm.retrieval_type.data)

@app.route('/credentials-received', methods=['GET', 'POST'])
def credentialConfirmation():
    # add checks to see if the user is logged in by using sessions dict instead of plain variables
    # this will help against someone just using a username in browser to have access USE SESSIONS INSTEAD

    retrieval_data_type = session['retrieval_data_type']
    if retrieval_data_type == 'pwd':
        forgot_user_name = session['retrieved_data_user_name']
        forgot_user_email = session['retrieved_data_email']
        user_name_exists = forgot_user_name in controls.system_user_list
        if user_name_exists:
            email = DB.USERS.find_one({'USER': forgot_user_name,
                                       'CONTACT EMAIL': forgot_user_email})
            if email != None:
                email = email['CONTACT EMAIL']
                message = 'We received your request to change your password for you Tweet View account. Please follow click the link provided and ' \
                          'follow the instructions: icehc1.arcc.albany.edu:2020:/credentials-received/' + forgot_user_name + '/reset-password'

                message = gmail_controller.create_message(mongo_config.tv_email, email, "Password Reset",
                                                          message)

                service = gmail_controller.build_service()
                gmail_controller.send_message(service, mongo_config.tv_email, message)

                g.user = forgot_user_name

                return redirect(url_for('login'))

            else:
                flash("The credentials you entered does not match any records in Tweet Views database")
                return redirect(url_for('retrieve_cred'))
        else:
            flash("The credentials you entered does not match any records in Tweet Views database")
            return redirect(url_for('retrieve_cred'))

    elif retrieval_data_type == 'usr':

        user_email = session['retrieved_data']
        forgotten_name_list = list(USERS.find({'CONTACT EMAIL': user_email}))
        if len(forgotten_name_list) > 0:
            if len(forgotten_name_list) > 1:
                message = "Hello, your request for your account information was received, multiple user names found: "
                for user_doc in forgotten_name_list:
                    message = message + ' ' + user_doc['USER'] + '.'

                message = gmail_controller.create_message(mongo_config.tv_email, user_email, "Account Credentials",
                                                          message)

                service = gmail_controller.build_service()
                gmail_controller.send_message(service, mongo_config.tv_email, message)

            else:
                message = "Hello, your request for your account information was received " + " User Name: " + \
                          forgotten_name_list[0]['USER']

                message = gmail_controller.create_message(mongo_config.tv_email, user_email, 'Account Credentials',
                                                          message)
                service = gmail_controller.build_service()
                gmail_controller.send_message(service, mongo_config.tv_email, message)

        else:
            # show a flash message that the email entered does not exists
            flash("The credentials you entered does not match any records in Tweet Views database")
            return redirect(url_for('retrieve_cred'))

    return render_template('credConfirmation.html')

@app.route('/credentials-received/<user>/reset-password', methods=['POST', 'GET'])
def reset_password(user):
    rememberCredsForm = ChangeLoginInfo()

    if request.method == 'POST':
        errors = False
        password = request.form.get('changed_pass_word')

        if not any(letter.isdigit() for letter in password):
            flash(invalid_pwd_num, 'warning')
            errors = True
        if len(password) < 7:
            flash(invalid_pwd_legnth, 'warning')
            errors = True
        if not any(letter.isupper() for letter in password):
            flash(invalid_pwd_caps, 'warning')
            errors = True
        if errors:  # redirect user to same page
            return redirect(url_for('register'))
        else:
            report = controls.change_user_password(user, password)
            session.clear()
            flash(report)
            return redirect(url_for('login'))

    return render_template('passwordReset.html', user=g.user, form=rememberCredsForm)

@app.route('/register', methods=['POST','GET'])
def register():
    registerForm = UserRegisterForm()

    errors = False
    invalid_username = "This username is already taken. Please input a different username"
    invalid_pwd_num = "Password must contain at least one digit"
    invalid_pwd_caps = "Password must contain at least one capitalized character"
    invalid_pwd_legnth = "At least 7 characters are required for password"
    if request.method == 'POST':
        # Check username input
        # add checks for empty input
        user_name = request.form.get('user_name')
        if request.form.get('user_name') in controls.system_user_list:
            invalid_username = controls.create_tv_user(
            user_name=request.form.get('new_register_user_name'),
            pwd=request.form.get('new_register_pass_word'),
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            email=request.form.get('email'))
            flash(invalid_username, 'warning')
            errors = True
        # Check password input
        password = request.form.get('new_register_pass_word')

        if not any(letter.isdigit() for letter in password):
            flash(invalid_pwd_num, 'warning')
            errors = True
        if len(password) < 7:
            flash(invalid_pwd_legnth, 'warning')
            errors = True
        if not any(letter.isupper() for letter in password):
            flash(invalid_pwd_caps, 'warning')
            errors = True

        if errors: # rediect user to same page
            return redirect(url_for('register'))
        else:

            # Submit new user to TweetView database
            approved_message = controls.create_tv_user(
            user_name=request.form.get('new_register_user_name'),
            pwd=request.form.get('new_register_pass_word'),
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            email=request.form.get('email'))

            # construct Email message
            message = gmail_controller.create_message(mongo_config.tv_email, request.form.get('email'),
                                            "Account Confirmation", mongo_config.account_registry_confirmation_message)
            service = gmail_controller.build_service()
            gmail_controller.send_message(service, mongo_config.tv_email,
                                          message)

            # redirect user to login page with success message
            flash(approved_message, 'success')
            return redirect(url_for('login'))
                ################################################
                #### LASTLY ADD HTML TO RENDER FLASH ALERTS ####
                ################################################

    return render_template('register.html', form=registerForm)

@app.route('/login', methods=['POST','GET'])
def login():
    loginForm = UserLoginForm()
    # May have to move back
    session.pop('user', None)
    if request.method == 'POST':
        try:
            # This block validates password & user name
            current_user = MongoClient(host = mongo_config.host,
            port = mongo_config.port, authSource=mongo_config.amdin_database,
            username = request.form.get('user_name'),
            password = request.form.get('pass_word'))
            current_user.list_database_names() # check for any traceback errors
        except:
            flash("Invalid Login Information", "warning")
            return redirect(url_for('login'))
        else:
            session['user'] = request.form.get('user_name')
            session['password'] = request.form.get('pass_word')
            session['assignemnts'] = USERS.find({"USER": session['user']})[0]['ASSIGNMENTS']
            flash('Hello ' + session['user'], 'success')

            return redirect(url_for('landing_page', user=session['user']))

    return render_template('login.html', form=loginForm)


@app.route('/', methods=['POST', 'GET'])
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/home/<user>', methods=['POST', 'GET'])
def landing_page(user):
    return render_template('landing_page.html')


# NOT to be confused with any individual project dashboard
@app.route('/<user>/projects', methods=['POST', 'GET'])
def user_dashboard(user):
    if not g.user:
        return redirect(url_for('login'))
    else:
        return render_template('projects.html', Client=Client)


@app.route('/<user>/projects/<project>', methods=['POST', 'GET'])
def project_dashboard(user, project):
    project = project
    session['selected project'] = project

    leads = Client[project]['PROJECT_INFO'].find_one()['lead']
    lead_contact_dict = {}
    [lead_contact_dict.update({lead_name : USERS.find_one({'USER' : lead_name})['CONTACT EMAIL']}) for lead_name in leads]
    # throw all information collected into dictionary
    project_details = {
        'current user role': [assignment['ROLE'] for assignment in USERS.find_one({'USER' : g.user})['ASSIGNMENTS'] if assignment['PROJECT_NAME'] == project][0],
        'project leads':  Client[project]['PROJECT_INFO'].find_one()['lead'],
        'contact info': lead_contact_dict,
        'analysts': Client[project]['PROJECT_INFO'].find_one()['Assigned'],
        'summary': Client[project]['PROJECT_INFO'].find_one()['Summary'],
        'scheme': Client[project]['PROJECT_INFO'].find_one()['Scheme'],
        'total': Client[project]['test_data'].count(), # Change test_data collection call to data before deployment
        'completion_rate': None # Must consult dr.J for how labeling completed tweets will function
    }
    if request.method == 'POST':
        if request.form['start_labeling'] == "Assist in Labeling" or request.form['start_labeling'] == "Begin Labeling":
            # check if there is a validation Schema
            project_db = Client[project]
            project_collections_info_list = project_db.command('listCollections')['cursor']['firstBatch']
            # rename the collection where the tweet data is stored to be data (or master data) instead of test_data
            labeled_data_col_info = [collection_info for collection_info in project_collections_info_list if
                                     collection_info['name'] == 'test_data'][0]
            if 'validator' in labeled_data_col_info['options'].keys():
                session['project_labels'] = labeled_data_col_info['options']['validator']['$jsonSchema']['properties']
                if not Client[project].test_data.count_documents({}) > 0:
                    # return something to HTML notifying user there is no documents uploaded to this project
                    flash("There are currently no data uploaded to be label within this project")
                    return redirect(url_for('label_project_data', project=session['selected project'], user=g.user))
                else:
                    # check if there is a query collection for user
                    if g.user + '_' + 'query' not in Client[project].list_collection_names():
                        # add all docs into new collection
                        user_query_collection = g.user + '_' + 'query'
                        Client[project][user_query_collection].insert_many(
                            list(Client[project]['test_data'].find())
                        )
                    else:
                        user_query_collection = g.user + '_' + 'query'

                    session['batch limit'] = 10
                    session['skip count'] = 0
                    session['remainder amount'] = Client[project][user_query_collection].count_documents({}) % session['batch limit']
                    session['complete batches amount'] = int(Client[project][user_query_collection].count_documents({}) / session['batch limit'])
                    session['batch iteration'] = 1
                    session['deletion_batch'] = []
                    # add conditions to only find tweets that have not been labeled yet
                    id_str = list(Client[project][user_query_collection].find({}, {"id_str": 1}).skip(session['skip count']).limit(session['batch limit']))
                    session['current batch'] = [doc['id_str'] for doc in id_str]
                    session['current tweet index'] = 0
                    session['on final batch'] = False
                    return redirect(url_for('label_project_data', project=session['selected project'], user=g.user))
            else:
                # return a message stating that the project has not been set up requiring validation and return later or inform project lead
                return redirect(url_for('label_project_data', project=session['selected project'], user=g.user))

    return render_template('project_dash.html', project=project, details=project_details)


@app.route('/<user>/<project>/modify/manage-analyst', methods=['POST', 'GET'])
def analyst_modification(project, user):

    assignForm = AssignUserButton()

    # Check if the current user is a lead of current project and if there are any possible candidates
    current_user_assignments = USERS.find_one({'USER': g.user})['ASSIGNMENTS']
    open_analyst_candidates = []

    for assignment in current_user_assignments:
        if (assignment['PROJECT_NAME'] == project) and (assignment['ROLE'] == 'Project Lead'):

            # Get all users in database
            for user in controls.system_user_list:
                for user_doc in DB.USERS.find():
                    # Cross check user name
                    if (user == user_doc['USER']) & (user != g.user) & (user != 'TV_default_admin'):
                        if len(user_doc['ASSIGNMENTS']) >= 1:
                            for assigned_project_doc in user_doc['ASSIGNMENTS']:
                                if (assigned_project_doc['ROLE'] != 'Project Lead') & (
                                        assigned_project_doc['PROJECT_NAME'] != project):
                                    open_analyst_candidates.append({
                                        'user': user,
                                        'assignments': len(USERS.find_one({'USER': user})['ASSIGNMENTS'])
                                    })
                        else:
                            open_analyst_candidates.append({
                                'user': user,
                                'assignments': 'No Projects Currently Assigned'
                            })

                        break

    if len(open_analyst_candidates) > 0:
        has_possible_candidates = True
    else:
        has_possible_candidates = False

    # check which button was selected to submit
    if request.method == 'POST':
        if assignForm.request_type.data == 'force':

            # Get key information for task
            selected_analyst = request.form['analyst']
            selected_project = request.form['selected_project']
            lead_email = USERS.find_one({"USER": g.user})['CONTACT EMAIL']
            # get proper flash and email message
            assigned_message, assign_email = mongo_config.generate_assignment_message(selected_analyst, True,
                                                                                      selected_project, g.user,
                                                                                      lead_email)
            # Assign user
            role, doc = add_analyst_to_project(selected_analyst, selected_project)
            # create a query collection for the selected user by transferring project data to the new collection
            # NOTE: it's best to have data in a project master data collection before assigning new users to a project
            # This block will check if there is any data in the selected project's collection before creating a query collection
            # CHANGE TEST_DATA TO MASTER
            if 'test_data' in Client[selected_project].list_collection_names():
                # check if the there is any data in the collection
                if Client[selected_project]['test_data'].count_documents({}) > 0:
                    # add all docs into new collection
                    user_query_collection = selected_analyst + '_' + 'query'
                    Client[selected_project][user_query_collection].insert_many(
                        list(Client[selected_project]['test_data'].find())
                    )
                else:
                    # have a flash message or email project lead that no query doc was created for user since there is no data in master data
                    pass
            else:
                # email the project lead that master data has not been initialized
                pass

            # Construct Email
            message = gmail_controller.create_message(mongo_config.tv_email,
                                                      USERS.find_one({"USER": selected_analyst})['CONTACT EMAIL'],
                                                      selected_project + ": Project Assignment Notification",
                                                      assign_email)
            service = gmail_controller.build_service()
            gmail_controller.send_message(service, mongo_config.tv_email,
                                          message)

            # redirect to landing page with flash message
            flash(assigned_message)
            flash(selected_analyst + ": " + role)
            return redirect(url_for('landing_page', user=session['user']))

        elif assignForm.request_type.data == 'notify':

            # Get key information for task
            selected_analyst = request.form['analyst']
            selected_project = request.form['selected_project']
            lead_email = USERS.find_one({"USER": g.user})['CONTACT EMAIL']
            # get proper flash and email message
            notify_message, notify_email = mongo_config.generate_assignment_message(selected_analyst, False,
                                                                                    selected_project, g.user,
                                                                                    lead_email)
            # Construct Email
            message = gmail_controller.create_message(mongo_config.tv_email,
                                                      USERS.find_one({"USER": selected_analyst})['CONTACT EMAIL'],
                                                      selected_project + ": Project Assignment Notification",
                                                      notify_email)
            service = gmail_controller.build_service()
            gmail_controller.send_message(service, mongo_config.tv_email,
                                          message)

            # redirect to landing page with flash message
            flash(notify_message)
            return redirect(url_for('project_modification'))

    return render_template('AnalystManager.html', request_candidates=open_analyst_candidates,
                           has_possible_candidates=has_possible_candidates, form=assignForm, project=project)


@app.route('/<user>/<project>/modify', methods=['POST', 'GET'])
def project_modification(project, user):
    return render_template('ModifyProject.html', project=project)


@app.route('/<user>/<project>/modify/manage-data', methods=['POST', 'GET'])
def data_modification(project, user):

    form = ProjectModifyer()
    action = form.data_modification_action.data
    if action != None: # may have to change to if data is here v
        action = form.data_modification_action.data
        session['action'] = action
        return redirect(url_for('omni_modifier', project=project, form=form, action=action))
    # elif 'file' in request.files:
    #     print('file is here')
    return render_template('DataManager.html', project=project, form=form, action=action)


@app.route('/<user>/<project>/modify/manage-labeling-schema', methods=['POST', 'GET'])
def labeling_modification(project, user):

    form = ProjectModifyer()

    if request.method == "POST":
        properties = {}
        required_fields = []

        #######################################
        ### check validator for enum option ###
        #######################################
        if request.form.get('enum_label') is not None:
            enum_property = {}
            enum_options = []
            enum_label = request.form.get('enum_label')
            option_1 = request.form.get('validator_option_1')
            option_2 = request.form.get('validator_option_2')
            option_3 = request.form.get('validator_option_3')
            enum_description = request.form.get('enum_description')

            if (option_1 is None) or (request.form.get('validator_option_1') == 'None'):
                enum_options.append(None)
            else:
                enum_options.append(option_1)

            if (option_2 is None) or (request.form.get('validator_option_1') == 'None'):
                enum_options.append(None)
            else:
                enum_options.append(option_2)

            if (option_3 is None) or (request.form.get('validator_option_1') == 'None'):
                enum_options.append(None)
            else:
                enum_options.append(option_3)

            if request.form.get('enum_required') == 'Required Field':
                required_fields.append(enum_label)

            # create property field for enum validator
            properties[enum_label] = {
                "enum": enum_options
            }
            if enum_description is None:
                enum_property[enum_label]['description'] = enum_description


        ##########################################
        ### check validator for integer option ###
        ##########################################
        if request.form.get('int_label') is not None:
            int_property = {'bsonType': 'int'}
            int_label = request.form.get('int_label')
            minimum = request.form['min']
            maximum = request.form['max']
            int_description = request.form.get('int_description')

            if minimum >= maximum:
                flash("minimum value is greater than maximum. minimum & maximum has been set to 0 & 100")
            else:
                int_property['minimum'] = int(minimum)
                int_property['maximum'] = int(maximum)

                if request.form.get('int_required') == 'Required Field':
                    required_fields.append(int_label)

                # create property field for int validator
                properties[int_label] = int_property
                if int_description is not None:
                    properties[int_label]['description'] = int_description


        #######################################
        ### check validator for bool option ###
        #######################################
        if request.form.get('bool_label') is not None:
            bool_label = request.form.get('bool_label')
            bool_description = request.form.get('bool_description')

            if request.form.get('bool_required') == 'Required Field':
                required_fields.append(bool_label)

            # create property field for bool validator
            properties[bool_label] = {"bsonType": "bool"}
            if bool_description is not None:
                properties[bool_label]['description'] = bool_description


        #######################################
        ### check validator for text option ###
        #######################################
        if request.form.get('text_label') is not None:
            text_label = request.form.get('text_label')
            text_description = request.form.get('text_description')

            if request.form.get('text_required') == 'Required Field':
                required_fields.append(text_label)

            # create property field for text validator
            properties[text_label] = {"bsonType": "string"}
            if text_description is not None:
                properties[text_label]['description'] = text_description

        Client[project].command({
            "collMod": "test_data",
            "validator": {"$jsonSchema": {
                "bsonType": "object",
                "required": required_fields,
                "properties": properties,
            }},
            "validationLevel": "strict",
            "validationAction": "error"
        })

        return redirect(url_for('project_modification', project=project, user=user))
    return render_template('LabelSchemaManager.html', project=project, form=form)


@app.route('/<user>/<project>/modify/project-manager/<action>', methods=['POST', 'GET'])
def omni_modifier(project, action, user):

    # You will need form object for later mod features
    form = ProjectModifyer()

    # This will account for upload action only
    if request.method == 'POST' and 'file' in request.files:

        if 'file' not in request.files:
            flash('No file part')
            return redirect(url_for('data_modification', project=project, form=form, action=action))

        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(url_for('data_modification', project=project, form=form, action=action))

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(join(app.config['UPLOAD_FOLDER'], filename))

            # open file from upload folder directory
            file_extension = filename.rsplit('.')[1]

        if file_extension == 'csv':
            imported_data = pd.read_csv(abspath(join(app.config['UPLOAD_FOLDER'], filename)), encoding='unicode_escape')
            for index, tweet in imported_data.iterrows():
                # add check to see if the tweet id already exists in datatset
                tweet_id_query = Client[project]['test_data'].find_one({'id_str': tweet['id_str']})
                if tweet_id_query is None:
                    # add tweet to project database
                    data = {
                        'id_str': tweet['id_str'],
                        'full_tweet_text': tweet['stack_vars.full_tweet_text'],
                        'screen_name': tweet['user.screen_name'],
                        'created_ts': tweet['created_ts']
                    }
                    # Client[project].insert_one(data)
            flash('Your file has been uploaded to ' + project + ' dataset', 'warning')
            return redirect(url_for('project_modification', project=project))

        elif file_extension == 'json':
            # proper directory
            imported_data = pd.read_json(abspath(join(app.config['UPLOAD_FOLDER'], filename)))
            for index, tweet in imported_data.iterrows():
                # add check to see if the tweet id already exists in datatset
                tweet_id_query = Client[project]['test_data'].find_one({'id_str': tweet['id_str']})

                if tweet_id_query is None:
                    # add tweet to project database
                    data = {
                        'id_str': tweet['id_str'],
                        'full_tweet_text': tweet['stack_vars.full_tweet_text'],
                        'screen_name': tweet['user.screen_name'],
                        'created_ts': tweet['created_ts']
                    }
                    # Client[project].insert_one(data)

            flash('Your file has been uploaded to ' + project + ' dataset', 'message')
            return redirect(url_for('project_modification', project=project))

        elif file_extension == 'txt':

            with open(abspath(join(app.config['UPLOAD_FOLDER'], filename)), 'r') as f:
                header = f.readline()
                header = header.split(',')
                if '' in header:
                    header.remove('')
                id_str_column = header[0]

                for row in f.readlines():
                    row = row.rstrip().split(',')
                    for value in row:

                        if "ID_" in value:
                            tweet_id_query = Client[project]['test_data'].find_one({'id_str': value[3:]})
                            if tweet_id_query is None:
                                data = {
                                    id_str_column: value.rstrip(),
                                    'full_tweet_text': None,
                                    'screen_name': None,
                                    'created_ts': None
                                }
                                # Client[project].insert_one(data)
            flash('Your file has been uploaded to ' + project + ' dataset', 'info')
            return redirect(url_for('project_modification', project=project))

    elif action == 'download':

        dataset_list = listdir(UPLOAD_FOLDER)
        if len(dataset_list) == 0:
            dataset_list = None

        if request.method == 'POST':
            selected_download_file = request.form.get('file')

            if selected_download_file is None:
                flash("NO FILE SELECTED", 'info')

            elif selected_download_file == 'All':

                # Grab all documents in project's database
                data = list(Client[project]['test_data'].find())
                data = pd.DataFrame(data)
                # save documents to CSV
                data.to_csv(join(app.config['UPLOAD_FOLDER'], selected_download_file + '.csv'))
                # Send file download
                return send_from_directory(app.config['UPLOAD_FOLDER'], selected_download_file + '.csv',
                                           as_attachment=True)

            else:
                file_path = join(app.config['UPLOAD_FOLDER'], selected_download_file)

                # Check if file is CSV
                file_extension = selected_download_file.split('.')[-1]

                if file_extension == 'csv':
                    return send_from_directory(app.config['UPLOAD_FOLDER'], selected_download_file, as_attachment=True)

                elif file_extension == 'json':

                    # Convert JSON to CSV
                    temporary_file_name = selected_download_file.split('.')[0]
                    data = pd.read_json(file_path)
                    data.to_csv(join(app.config['UPLOAD_FOLDER'], temporary_file_name + '.csv'))
                    # Send file download
                    return send_from_directory(app.config['UPLOAD_FOLDER'], temporary_file_name + '.csv', as_attachment=True)

                elif file_extension == 'txt':

                    with open(abspath(join(app.config['UPLOAD_FOLDER'], selected_download_file )), 'r') as f:
                        header = f.readline()
                        header = header.split(',')
                        if '' in header:
                            header.remove('')
                        id_str_column = header[0]

                        data = []
                        for row in f.readlines():
                            row = row.rstrip().split(',')
                            for value in row:
                                if "ID_" in value:

                                    data_point = {
                                        id_str_column: value.rstrip(),
                                        'full_tweet_text': None,
                                        'screen_name': None,
                                        'created_ts': None
                                    }

                                    data.append(data_point)

                        data = pd.DataFrame(data)

                        # Convert txt to CSV
                        temporary_file_name = selected_download_file.split('.')[0]
                        data.to_csv(join(app.config['UPLOAD_FOLDER'], temporary_file_name + '.csv'))
                        # Send file download
                        return send_from_directory(app.config['UPLOAD_FOLDER'], temporary_file_name + '.csv',
                                                   as_attachment=True)

                # Check for csv version of the selected file to delete, then overwrite
                if selected_download_file + '.csv' in listdir(app.config['UPLOAD_FOLDER']):
                    remove(join(app.config['UPLOAD_FOLDER'], selected_download_file + '.csv'))

        return render_template('OmniModifier.html', project=project, form=form, action=action, files=dataset_list)

    elif action == 'delete':
        pass

    return render_template('OmniModifier.html', project=project, form=form, action=action)


@app.route('/<user>/<project>/LabelProject', methods=['POST', 'GET'])
def label_project_data(user, project):
    user_query_collection = g.user + '_' + 'query'
    user_labeled_collection = g.user + '_' + 'labeled_data'
    # Switch to root user
    root_client = MongoClient(host=mongo_config.host, port=mongo_config.port,
                              username=mongo_config.user, password=mongo_config.pwd)

    # make API query from Twitter, make sure to yield the next few tweets instead of returning
    if not session['on final batch']:
        if session['current tweet index'] > 9:
            # adjust batch iteration
            session['batch iteration'] += 1

            # check if the complete batch amount has been reached
            if session['batch iteration'] == session['complete batches amount']:
                # get the final batch
                id_str = list(Client[project][user_query_collection].find({}, {"id_str": 1}).skip(session['skip count']).limit(session['remainder amount']))
                final_batch = [doc['id_str'] for doc in id_str]
                session['current batch'] = final_batch
                session['on final batch'] = True

            else:
                # adjust skip size and reset iteration
                session['skip count'] += 10
                session['current tweet index'] = 0
                # get a new batch and reset index count
                id_str = list(Client[project][user_query_collection].find({}, {"id_str": 1}).skip(session['skip count']).limit(session['batch limit']))
                session['current batch'] = [doc['id_str'] for doc in id_str]
                # delete all tweets from the previous batch
                for tweet_id in session['deletion_batch']:
                    tweet_id = 'ID_' + tweet_id
                    deleted_tweet = Client[project][user_query_collection].delete_one({'id_str': tweet_id})
                # create an empty list for another use
                session['deletion_batch'] = []
        elif (session['current tweet index'] == 9) and (session['on final batch'] == False):
            flash('WARNING: THIS IS THE FINAL ATTACHMENT OF THE CURRENT BATCH '\
                  'MAKE SURE YOUR DATA IS PROPERLY LABELED BEFORE CONTINUING TO THE NEXT BATCH '\
                  'ONCE "NEXT" IS SELECTED, YOU WILL BE UNABLE TO REVIEW THE PREVIOUS BATCH OF DATA', 'warning')

    elif (session['on final batch']) and (session['current tweet index'] == session['remainder amount']):
        # delete all tweets from the previous batch
        for tweet_id in session['deletion_batch']:
            tweet_id = 'ID_' + tweet_id
            Client[project][user_query_collection].delete_one({'tweet_id': tweet_id})
        # create an empty list for another use
        session['deletion_batch'] = []
        # return a html stating the project's data has been fully completed
        return render_template('ProjectLabeling.html', user=user, project=project)

    tweet_obj, tweet_id, is_deprecated = get_tweet_html(session['current batch'][session['current tweet index']])
    if request.method == 'POST':
        if request.form['Tweet HTML Action'] == 'SUBMIT':
            # Collect labeled information
            labeled_doc = {
                'tweet_id': 'ID_' + tweet_obj['tweet_id'],
                'labels': {}
            }
            for label in session['project_labels'].keys():
                labeled_doc['labels'][label] = request.form[label]
            # submit labeled doc into user's labeled data collection
            root_client[project][user_labeled_collection].insert_one(labeled_doc)
            # logic for handling tweet batches
            session['current tweet index'] += 1
            # add tweet id to list for deletion
            session['deletion_batch'].append(tweet_id)
            return redirect(url_for('label_project_data', user=g.user, project=project))

        elif request.form['Tweet HTML Action'] == 'NEXT':
            session['current tweet index'] += 1
            return redirect(url_for('label_project_data', user=g.user, project=project))

        elif request.form['Tweet HTML Action'] == 'SKIP':
            session['current tweet index'] += 1
            return redirect(url_for('label_project_data', user=g.user, project=project))

        elif request.form['Tweet HTML Action'] == 'PREVIOUS':
            if not session['current tweet index'] == 0:
                session['current tweet index'] -= 1
                # remove the previously appended tweet data
                session['deletion_batch'].pop()
            return redirect(url_for('label_project_data', user=g.user, project=project))


    return render_template('ProjectLabeling.html', project=session['selected project'], user=g.user,
                           tweet_html_obj=tweet_obj, validation_obj=session['project_labels'],
                           dead=is_deprecated)


if __name__ == "__main__":
    app.run(debug=True)
