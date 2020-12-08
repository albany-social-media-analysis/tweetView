import sys
sys.path.append("../")
from pprint import pprint
import mongo_config
from mongo_config import get_tweet_html
from assign_analyst import add_analyst_to_project
import smtplib
from email.mime.text import MIMEText as text
from admin_authentication import TVAdminAuthorizedCreationControls
from pymongo import MongoClient
from flask import (Flask, render_template, request, redirect, url_for, session,
                   logging, flash, g)
from appForms import UserLoginForm, UserRegisterForm, CredentialRetreival, ChangeLoginInfo, AssignUserButton

# Connect to database
Client =  MongoClient(host = mongo_config.host, port = mongo_config.port,
          username = mongo_config.tv_admin, password = mongo_config.tv_admin_pwd,
          authSource=mongo_config.amdin_database)
DB = Client.TV_ADMIN
USERS = DB.USERS
# connect to authenticating controls
controls = TVAdminAuthorizedCreationControls(auth_user_name=mongo_config.tv_admin,
                                          auth_password=mongo_config.tv_admin_pwd)

app = Flask(__name__)
app.config['SECRET_KEY'] = "Conspiracy" #Change to environment variable

# global variable to be used across the web site,
# g. can be anything or any object that might be useful in app.py or html
@app.before_request
def before_request():
    g.user = None

    if 'user' in session:
        g.user = session['user']
        g.user_projects = session['assignemnts']

@app.route('/retreivecredentials', methods=['POST','GET'])
def retreive_creds():
    rememberCredsForm = CredentialRetreival()

    type = rememberCredsForm.retreival_type.data

    if rememberCredsForm.retreival_type.data == 'pwd':

        forgot_user_name = request.args.get('forgot_user_name')
        user_name_exists = forgot_user_name in controls.system_user_list
        if user_name_exists:

            email = DB.USERS.find_one({'USER': forgot_user_name})['CONTACT EMAIL']
            DB.USERS.command('userInfo')['users']

            #password = # input some pymongo logic to return the password by user_email

            # Breakdown message to be professionally formatted and recognizable through
            # email delivary OR USE TXT FILE
            #message = "Hello, your request for your account information was received " + " PassWord: " + password + " Testing email automization "

            server = smtplib.SMTP()
            server.starttls()
            server.login() # login, remember to use environmental variables for server
            server.sendmail(tweetview_mail, email, message)
            return redirect(url_for('credentialConfirmation'))

        else:
            # show flash message stating that the credentials entered was not found
            pass
    elif rememberCredsForm.retreival_type.data == 'usr':

        user_email = request.args.get('user_email')

        #user_name = # place pymongo logic to match user name by the email used
        #user_email_exists = user_name_exists[forgot_user_name]['CONTACT EMAIL'] is user_email
        if user_name_exists :

            message = "Hello, your request for your account information was received " + " User Name: " + user_name + " Testing email automization "

            server = smtplib.SMTP(server, port=port)
            server.starttls() # start server
            server.login(tweetview_mail, tweetview_pwd) # login, remember to use environmental variables
            server.sendmail(tweetview_mail, user_email, message)
            return redirect(url_for('credentialConfirmation'))

        else:
            # show a flash message taht the email entered does not exists
            pass

    return render_template('choosecredentials.html',form=rememberCredsForm,type=type)


@app.route('/credentials-received')
def credentialConfirmation():
    # add checks to see if the user is logged in by using sessions dict instead of plain variables
    # this will help against someone just using a username in browser to have access USE SEESIONS INSTEAD
    return render_template("credsconfirmation.html")

@app.route('/register',methods=['POST','GET'])
def register():
    registerForm = UserRegisterForm()

    errors = False
    invalid_username = "This username is already taken. Please input a different username"
    invalid_pwd_num = "Password must contain atleast one digit"
    invalid_pwd_caps = "Password must contain at least one capitalized character"
    invalid_pwd_legnth = "At least 7 characters are required for password"

    if request.method == 'POST':
        if registerForm.validate_on_submit():
            # Check username input
            # add checks for empty input
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
                message = text(mongo_config.account_registry_confirmation_message)
                message['Subject'] = "Account Confirmation"
                message['From'] = mongo_config.tv_email
                message['To'] = request.form.get('email')
                # Send Email confirmation to user
                server = smtplib.SMTP(mongo_config.tv_email_server, port=mongo_config.tv_email_port)
                server.starttls()# start server
                server.login(mongo_config.tv_email,mongo_config.tv_email_pwd)# login, remember to use environmental variables for server
                server.sendmail(message['From'],message['To'],message.as_string())
                server.quit()
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


@app.route('/home/<user>', methods=['POST', 'GET'])
def landing_page(user):

    assignForm = AssignUserButton()

    total_projects = len(g.user_projects)
    # Get all project that user is a lead for
    list_lead_of_projects = [project['PROJECT_NAME'] for project in g.user_projects if project['ROLE'] == 'Project Lead']
    # Get all users in database
    open_analyst_candidates = []
    for user in controls.system_user_list:
        for user_doc in DB.USERS.find():
            # Cross check user name
            if (user == user_doc['USER']) & (user != g.user) & (user != 'TV_default_admin'):
                if len(user_doc['ASSIGNMENTS']) >= 1:
                    for assigned_project_doc in user_doc['ASSIGNMENTS']:
                        if (assigned_project_doc['ROLE'] != 'Project Lead') & (assigned_project_doc['PROJECT_NAME'] not in list_lead_of_projects):
                           open_analyst_candidates.append({
                               'user': user,
                               'assignments': len(USERS.find_one({'USER': user})['ASSIGNMENTS'])
                           })
                else:
                    open_analyst_candidates.append({
                        'user': user,
                        'assignments': 'No Projects Currently Assigned'
                    })

    # Check if the current user is a lead and if there are any possible candidates
    if len(list_lead_of_projects) > 0:
        is_a_lead = True
    if len(open_analyst_candidates) > 0:
        has_possible_candidates = True


    # check which button was selected to submit
    if request.method == 'POST':
        if assignForm.request_type.data == 'force':

            # Get key information for task
            selected_analyst = request.form['analyst']
            selected_project = request.form['selected_project']
            lead_email = USERS.find_one({"USER": g.user})['CONTACT EMAIL']
            # get proper flash and email message
            assigned_message, assign_email = mongo_config.generate_assignment_message(selected_analyst, True,
                                                                              selected_project, g.user, lead_email)
            # Assign user
            role, doc = add_analyst_to_project(selected_analyst, selected_project)
            # create a query collection for the selected user by transferring project data to the new collection
            # NOTE: it's best to have data in a project master data collection before assigning new users to a project
            # This block will check if there is any data in the selected project's collection before creating a query collection
            # CHANGE TEST_DATA TO MASTER
            if 'test_data' in Client[selected_project].list_collection_names():
                # check if the there is any data in the collection
                if Client[selected_project]['test_data'].count_documents() > 0:
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
            message = text(assign_email)
            message['Subject'] = selected_project + ": Project Assignment Notification"
            message['From'] = mongo_config.tv_email
            message['To'] = USERS.find_one({"USER": selected_analyst})['CONTACT EMAIL']
            # Send assignment email to selected user
            server = smtplib.SMTP(mongo_config.tv_email_server, port=mongo_config.tv_email_port)
            server.starttls()  # start server
            server.login(mongo_config.tv_email,
                         mongo_config.tv_email_pwd)
            server.sendmail(message['From'], message['To'], message.as_string())
            server.quit()
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
            message = text(notify_email)
            message['Subject'] = selected_project + ": Project Inquiry Notification"
            message['From'] = mongo_config.tv_email
            message['To'] = USERS.find_one({"USER": selected_analyst})['CONTACT EMAIL']
            # Send assignment email to selected user
            server = smtplib.SMTP(mongo_config.tv_email_server, port=mongo_config.tv_email_port)
            server.starttls()  # start server
            server.login(mongo_config.tv_email,
                         mongo_config.tv_email_pwd)
            server.sendmail(message['From'], message['To'], message.as_string())
            server.quit()
            # redirect to landing page with flash message
            flash(notify_message)
            return redirect(url_for('landing_page', user=session['user']))

    return render_template('landing_page.html', sum=total_projects, request_candidates=open_analyst_candidates,
                           is_a_lead=is_a_lead, has_possible_candidates=has_possible_candidates, form=assignForm)


# NOT to be confused with any individual project dashboard
@app.route('/<user>/projects', methods=['POST', 'GET'])
def user_dashboard(user):
    if not g.user:
        return redirect(url_for('login'))
    else:
        return render_template('projects.html', Client=Client)


@app.route('/<user>/projects/<project>', methods=['POST','GET'])
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
        'completion_rate': None # Must consult dr.J for how labeling completed tweets
    }
    if request.method == 'POST':
        if request.form['start_labeling'] == "Assist in Labeling" or request.form['start_labeling'] == "Begin Labeling":
            # check if there is a validation Schema
            project_db = Client[project]
            project_collections_info_list = project_db.command('listCollections')['cursor']['firstBatch']
            # rename the collection where the tweet data is stored to simply data instead of test_data
            labeled_data_col_info = [collection_info for collection_info in project_collections_info_list if
                                     collection_info['name'] == 'test_data'][0]
            if 'validator' in labeled_data_col_info['options'].keys():
                session['project_labels'] = labeled_data_col_info['options']['validator']['$jsonSchema']['properties']
                if not Client[project].test_data.count_documents({}) > 0:
                    # return something to HTML notifying user there is no documents uploaded to this project
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


@app.route('/LabelProject/<user>/<project>', methods=['POST', 'GET'])
def label_project_data(user, project):
    user_query_collection = g.user + '_' + 'query'
    user_labeled_collection = g.user + '_' + 'labeled_data'
    # Switch to root user
    root_client = MongoClient(host=mongo_config.host, port=mongo_config.port,
                              username=mongo_config.user, password=mongo_config.pwd)

    print(session['current tweet index'])
    print(session['batch iteration'])
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
                # delete all tweets from teh previous batch
                for tweet_id in session['deletion_batch']:
                    tweet_id = 'ID_' + tweet_id
                    Client[project][user_query_collection].remove({'tweet_id': tweet_id})
                # create an empty list for another use
                session['deletion_batch'] = []
        elif (session['current tweet index'] == 9) and (session['on final batch'] == False):
            flash('WARNING: THIS IS THE FINAL ATTACHMENT OF THE CURRENT BATCH'\
                  'MAKE SURE YOU DATA IS PROPERLY LABELED BEFORE CONTINUING TO THE NEXT BATCH'\
                  'ONCE "NEXT" IS SELECTED, YOU WILL BE UNABLE TO REVIEW THE PREVIOUS BATCH OF DATA', 'warning')

    elif (session['on final batch']) and (session['current tweet index'] == session['remainder amount']):
        # delete all tweets from teh previous batch
        for tweet_id in session['deletion_batch']:
            tweet_id = 'ID_' + tweet_id
            Client[project][user_query_collection].remove({'tweet_id': tweet_id})
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
            session['deletion_batch'].apped(tweet_id)
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

@app.route('/<project>/modify', methods=['POST', 'GET'])
def modify(project):

    return render_template('modify.html')

if __name__ == "__main__":
    app.run(debug=True)
