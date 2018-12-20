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
from xlsxwriter.utility import xl_col_to_name
import numpy as np 

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
        if usr.gdrive_url != '' and usr.gdrive_sheet != '':
            gc = gspread.authorize(sheets.creds)
            sheet=sheets.get_worksheet(gc,usr.gdrive_url,usr.gdrive_sheet)

            idx=sheets.get_last_commented_row(sheet)
            tweet_id=sheet.cell(idx,1).value
            tweet_id=tweet_id.replace('ID_','')

            oembed=get_tweet_html(tweet_id)

            # Get the columns. This will drive validation a few other things
            cols=sheet.row_values(1)

            # Get the validation data for each column
            validation_data = {}    
            if len(cols) > 2:
                for c in range(2,len(cols)):
                    validation_data[cols[c]]=sheets.get_validation_data(
                        sheets.CRED_PATH,
                        usr.gdrive_url,
                        usr.gdrive_sheet,
                        '{0}!{1}2'.format(usr.gdrive_sheet,xl_col_to_name(c))
                    )
            return render_template('index.html',
                gdrive_url=usr.gdrive_url,
                gdrive_sheet=usr.gdrive_sheet,
                tweet_oembed=oembed,
                curr_id=idx,
                validation=validation_data
            )
        else:
            return render_template('index.html',gdrive_url="Provide a Link to a Google Sheet",gdrive_sheet='Sheet1')
    else:
        return redirect('/login')

@app.route('/update_gdrive_url',methods=['GET','POST'])
def update_gdrive_url():
    # Get the active user and update the gdrive url
    usr = security.datastore.find_user(email=current_user.email)
   
    if request.form['gDriveUrl'] != '':
        usr.gdrive_url=request.form['gDriveUrl']

    if request.form['gDriveSheetName'] == '':
        usr.gdrive_sheet='Sheet1'
    else:
        usr.gdrive_sheet=request.form['gDriveSheetName']

    # print(usr.gdrive_url)
    # print(usr.gdrive_sheet)
    if usr.gdrive_url != '' and usr.gdrive_sheet != '':
        # print(True)
        gc = gspread.authorize(sheets.creds)
        sheet=sheets.get_worksheet(gc,usr.gdrive_url,usr.gdrive_sheet)
        idx=sheets.get_last_commented_row(sheet)
        tweet_id=sheet.cell(idx,1).value
        tweet_id=tweet_id.replace('ID_','')
        #print(tweet_id)
    
    # Commit the change to the databse
    security.datastore.commit()

    # reaccess the user
    usr = security.datastore.find_user(email=current_user.email)
    oembed=get_tweet_html(tweet_id)

    cols=sheet.row_values(1)

    # Get the validation data for each column
    validation_data = {}    
    if len(cols) > 2:
        for c in range(2,len(cols)):
            validation_data[cols[c]]=sheets.get_validation_data(
                sheets.CRED_PATH,
                usr.gdrive_url,
                usr.gdrive_sheet,
                '{0}!{1}2'.format(usr.gdrive_sheet,xl_col_to_name(c))
            )
    #print(validation_data)
    return render_template('index.html',gdrive_url=usr.gdrive_url,
                gdrive_sheet=usr.gdrive_sheet,validation=validation_data,
                curr_id=idx,tweet_oembed=oembed)

@app.route('/get_next_tweet',methods=['GET','POST'])
def get_next_tweet():
    usr = security.datastore.find_user(email=current_user.email)
    gc = gspread.authorize(sheets.creds)
    sheet=sheets.get_worksheet(gc,usr.gdrive_url,usr.gdrive_sheet)

    # Get column names
    cols=sheet.row_values(1)
    #print(cols)
    # Get the validation data for each column
    validation_data = {}    
    if len(cols) > 2:
        for c in range(2,len(cols)):
            validation_data[cols[c]]=sheets.get_validation_data(
                sheets.CRED_PATH,
                usr.gdrive_url,
                usr.gdrive_sheet,
                '{0}!{1}2'.format(usr.gdrive_sheet,xl_col_to_name(c))
            )
    #print(request.form)
    form=dict()
    for k,v in request.form.items():
        if 'textarea_' in k:
            form[k.replace('textarea_','')]=v
        elif v == 'next':
            form[v]=k
        elif v == 'previous':
            form[v]=k
        else:
            form[k]=v

    #print(form.keys())
    # update the row indexer for the next tweet
    if 'next' in form.keys():   
        row=int(form['next'])     
        if len(form.keys()) > 1:        
            for k,v in form.items():
                if k != 'next':
                    if v != '':
                        sheet.update_cell(row,cols.index(k)+1,v)
        sheet.update_cell(row,2,usr.email)
        row+=1
    
    if 'previous' in form.keys():
        row=int(form['previous'])
        if len(form.keys()) > 1:
            for k,v in form.items():
                if k != 'previous':
                    if v != '':
                        sheet.update_cell(row,cols.index(k)+1,v)
        sheet.update_cell(row,2,usr.email)
        row-=1

    tweetid=sheet.cell(row,1).value
    if tweetid != '':
        oembed=get_tweet_html(tweetid.replace('ID_',''))
    else:
        oembed='<div> There are no more tweet ids!!</div>'
    
    return render_template('index.html',gdrive_url=usr.gdrive_url,
                gdrive_sheet=usr.gdrive_sheet,validation=validation_data,
                tweet_oembed=oembed,curr_id=row)

if __name__ == '__main__':
    app.run()
