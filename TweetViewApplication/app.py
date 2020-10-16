import sys
sys.path.append("../")
import mongo_config
import smtplib
from email.mime.text import MIMEText as text
from admin_authentication import TVAdminAuthorizedCreationControls
from pymongo import MongoClient
from flask import (Flask, render_template, request, redirect, url_for, session,
                   logging, flash, g)
from appForms import UserLoginForm, UserRegisterForm, CredentialRetreival, ChangeLoginInfo

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

    if request.method == 'POST':
        session.pop('user', None)
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

    return render_template('login.html',form=loginForm)

@app.route('/home/<user>', methods=['POST','GET'])
def landing_page(user):
    total_projects = len(g.user_projects)
    return render_template('landing_page.html', sum=total_projects)

@app.route('/<user>/account', methods=['POST','GET'])
def user_account(user):
    AccountForm = ChangeLoginInfo()
    option = AccountForm.account_option.data

    if AccountForm.account_option.data == 'usr':
        new_usr_name = request.args.get('usr')
        user_name_exists = new_usr_name in controls.system_user_list
        if user_name_exists:
            # return to this same page indicating that this user name already exits
            flash("The User Name:", new_usr_name ,"already exists")
        else:
            old_user_name = g.user
            print(g.user)
            print(session['user'])
            print(old_user_name)
            print(new_usr_name)
            USERS.update_one({"USER": g.user},
            {"$set": {"USER": new_usr_name}})
            session['user'] = new_usr_name
            flash(str("User Name has been updated from:" + old_user_name + "to" + session['user']))
            return redirect(url_for('landing_page',user=session['user']))

    elif AccountForm.account_option.data == 'pwd':
        # find out how to change pwd on mongo
        pass

    elif AccountForm.account_option.data == 'contact':
        new_contact = request.args.get('contact')
        # check User name
        #query email from user name
        # update email adress
        # redirect with flash message

    elif AccountForm.account_option.data == 'pj_request':
        # step 1: collect all projects in the database
        #step 2: After the user selects a designated project to be assigned to query for the project lead of the project
        #step 3: automate email to project lead
        #step 4: notify user that a request has been sent out
        pass

    return render_template('account_manager.html',form=AccountForm, option=option)

# NOT to be confused with any individual project dashboard
@app.route('/<user>/projects', methods=['POST','GET'])
def user_dashboard(user):
    if not g.user:
        return redirect(url_for('login'))
    else:
        return render_template('projects.html', Client=Client)

@app.route('/<user>/projects/<project>', methods=['POST','GET'])
def project_dashboard(user, project):
    project = project

    leads = Client[project]['PROJECT_INFO'].find_one()['lead']
    lead_contact_dict = {}
    [lead_contact_dict.update({lead_name : USERS.find_one({'USER' : lead_name})['CONTACT EMAIL']}) for lead_name in leads]
    # throw all information collected into dictionary
    project_details = {
        'current user role' : [assignment['ROLE'] for assignment in USERS.find_one({'USER' : g.user})['ASSIGNMENTS'] if assignment['PROJECT_NAME'] == project][0],
        'project leads' :  Client[project]['PROJECT_INFO'].find_one()['lead'],
        'contact info' : lead_contact_dict,
        'analysts': Client[project]['PROJECT_INFO'].find_one()['Assigned'],
        'summary' : Client[project]['PROJECT_INFO'].find_one()['Summary'],
        'scheme' : Client[project]['PROJECT_INFO'].find_one()['Scheme'],
        'total' : Client[project]['test_data'].count(), # Change test_data collection call to data before deployment
        'completion_rate': None # Must consult dr.J for how labeling completed tweets
    }

    return render_template('project_dash.html', project=project, details=project_details)

@app.route('/<project>/modify', methods=['POST', 'GET'])
def modify(project):

    return render_template('modify.html')

if __name__ == "__main__":
    app.run(debug=True)
