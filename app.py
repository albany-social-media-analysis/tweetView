from flask import Flask, render_template, request, session, redirect
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore
from flask_login import current_user
from flask_mail import Mail

from flask_wtf import FlaskForm
from wtforms import StringField, TextField
from wtforms.validators import DataRequired

from auth.database import db_session, init_db
from auth.models import User, Role

import sheets as sheets
from tweet_url import get_final_url, get_tweet_html
import gspread

# Create app
app = Flask(__name__)
app.config['DEBUG'] = False
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_PASSWORD_SALT'] = 'super-secret-salt'

app.config['SECURITY_REGISTERABLE']=True
app.config['SECURITY_TRACKABLE']=True
app.config['SECURITY_RECOVERABLE']=False
app.config['SECURITY_CHANGEABLE']=False

app.config['SECURITY_SEND_REGISTER_EMAIL']=False
app.config['SECURITY_SEND_PASSWORD_CHANGE_EMAIL']=False
app.config['SECURITY_SEND_PASSWORD_RESET_EMAIL']=False
app.config['SECURITY_SEND_PASSWORD_RESET_NOTICE_EMAIL']=False

# app.config['SECURITY_EMAIL_SENDER'] = ''
# app.config['MAIL_SERVER'] = ''
# app.config['MAIL_PORT'] = ''
# app.config['MAIL_USE_SSL']=''
# app.config['MAIL_DEFAULT_SENDER']=''
# mail = Mail(app)

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session,
                                                User, Role)
security = Security(app, user_datastore)



@app.before_first_request
def generate_db():
    init_db()

# Create a user to test with
@app.route('/', methods=['GET'])
def home():
    if current_user.is_authenticated:
        usr = security.datastore.find_user(email=current_user.email)
        if usr.gdrive_url:
            gc = gspread.authorize(sheets.creds)
            sheet=sheets.get_worksheet(gc,usr.gdrive_url,'Sheet1')

            idx=sheets.get_last_commented_row(sheet)
            tweet_id=sheet.cell(idx,1).value
            tweet_id=tweet_id.replace('ID_','')

            oembed=get_tweet_html(tweet_id)
            return render_template('index.html',gdrive_url=usr.gdrive_url,place_holder='Comments here ...',tweet_oembed=oembed,curr_id=idx)
        else:
            return render_template('index.html',place_holder='Comments here ...')
    else:
        return redirect('/login')

@app.route('/update_gdrive_url',methods=['GET','POST'])
def update_gdrive_url():
    # Get the active user and update the gdrive url
    usr = security.datastore.find_user(email=current_user.email)
    usr.gdrive_url=request.form['gDriveUrl']

    if usr.gdrive_url:
        gc = gspread.authorize(sheets.creds)
        sheet=sheets.get_worksheet(gc,usr.gdrive_url,'Sheet1')
        idx=sheets.get_last_commented_row(sheet)
        tweet_id=sheet.cell(idx,1).value
        tweet_id=tweet_id.replace('ID_','')
        #print(tweet_id)
    
    # Commit the change to the databse
    security.datastore.commit()

    # reaccess the user
    usr = security.datastore.find_user(email=current_user.email)
    oembed=get_tweet_html(tweet_id)

    return render_template('index.html',gdrive_url=usr.gdrive_url,place_holder='Comments here ...',curr_id=idx,tweet_oembed=oembed)

@app.route('/get_next_tweet',methods=['GET','POST'])
def get_next_tweet():
    usr = security.datastore.find_user(email=current_user.email)
    gc = gspread.authorize(sheets.creds)
    sheet=sheets.get_worksheet(gc,usr.gdrive_url,'Sheet1')

    #print(request.form)

    form=dict()
    for k,v in request.form.items():
        if k=='comment':
            form[k]=v
        else:
            form[v]=k

    # update the row indexer for the next tweet
    if 'next' in form.keys():
        row=int(form['next'])
        
        # Post the comment
        if 'comment' in form.keys():
            if form['comment'] != '':
                sheet.update_cell(row,3,form['comment'])
            sheet.update_cell(row,2,usr.email)
        else:
            sheet.update_cell(row,2,usr.email)
        row+=1
    
    if 'previous' in form.keys():
        row=int(form['previous'])

        if 'comment' in form.keys():
            sheet.update_cell(row,3,form['comment'])
            sheet.update_cell(row,2,usr.email)
        else:
            sheet.update_cell(row,2,usr.email)

        if row != 2:
            row-=1
    
    tweetid=sheet.cell(row,1).value
    if tweetid != '':
        oembed=get_tweet_html(tweetid.replace('ID_',''))
    else:
        oembed='<div> There are no more tweet ids!!</div>'
    
    return render_template('index.html',gdrive_url=usr.gdrive_url,place_holder='Comments here ...',tweet_oembed=oembed,curr_id=row)

if __name__ == '__main__':
    app.run()
