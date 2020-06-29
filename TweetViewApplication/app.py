from flask import (Flask, render_template, request, redirect, url_for, session,
                   logging, flash)
from appForms import UserLoginForm, UserRegisterForm, CredentialRetreival
import smtplib

app = Flask(__name__)

app.config['SECRET_KEY'] = "Conspiracy" #Change to environment variable

@app.route('/login',methods=['POST','GET'])
def login():
    loginForm = UserLoginForm()
    if loginForm.validate_on_submit():
        # add checks by matching user inout to to the  information stored on pymongo

        session['user_name'] = form.user_name.data
        session['pass_word'] = form.pass_word.data

        return redirect(url_for('dashboard', user = session['user_name']))

    return render_template('login.html',form=loginForm)

@app.route('/register',methods=['POST','GET'])
def register():
    registerForm = UserRegisterForm()
    # make alter here then pass to the redirect login page to send a confirmation
    if registerForm.validate_on_submit():
        session['first_name'] = registerForm.first_name.data
        session['last_name'] = registerForm.first_name.data
        session['new_register_user_name'] = registerForm.new_register_user_name.data
        session['new_register_pass_word'] = registerForm.new_register_pass_word.data
        session['confirm'] = registerForm.confirm.data
        session['email'] = registerForm.email.data
        session['role'] = registerForm.role.data
        return redirect(url_for('login')) # pass in alert for confirmation
    return render_template('register.html', form=registerForm)

# IMPORTANT: FIND OUT THE SERVER PORT FOR ALBANY EDU EMAILS
# CREATE A EMAIL ACCOUNT SPECIFCALLY FOR TWEETVIEW USER SUPPORT
@app.route('/retreivecredentials', methods=['POST','GET'])
def retreive_creds():
    rememberCredsForm = CredentialRetreival()

    #tweetview_email = # get envioronment variable for tweetview email address
    #tweetview_pwd = # get envioronment variable for tweetview email password
    port = 587
    server = 'smtp.office365.com'
    type = rememberCredsForm.retreival_type.data

    if rememberCredsForm.retreival_type.data == 'pwd':

        forgot_user_name = request.args.get('forgot_user_name')
        user_name_exists = forgot_user_name in user_name_list # look for match in pymongo user_list
        if user_name_exists:

            #email =  # input some pymongo logic to search user and email contact and
            #password = # input some pymongo logic to return the password by user_email

            # Breakdown message to be professionally formatted and recognizable through
            # email delivary
            #message = "Hello, your request for your account information was received " + " PassWord: " + password + " Testing email automization "

            server = smtplib.SMTP(server, port=port)
            server.starttls() # start server
            server.login(tweetview_mail, tweetview_pwd) # login, remember to use environmental variables
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

@app.route('/profile/<user>')
def dashboard(user):

    return render_template('profile.html')

if __name__ == "__main__":
    app.run(debug=True)
