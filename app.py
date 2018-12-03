from flask import Flask, render_template, flash, request, redirect, url_for
from flask_uploads import UploadSet, configure_uploads, patch_request_class, TEXT, DATA
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_wtf import FlaskForm
import os
from wtforms import SubmitField
import tweepy
from twitter_auth import *
import pandas as pd

DATA_DIR = os.path.join(os.getcwd(),'uploads')

app = Flask(__name__)
app.config['UPLOADED_TWEETIDS_DEST'] = DATA_DIR
app.config['SECRET_KEY']='tweeterviewer'

## --------- Image Uploading Block --------- ##
tweetids = UploadSet(
    'tweetids',
    TEXT + DATA,
)
configure_uploads(app,tweetids)
patch_request_class(app)

class UploadForm(FlaskForm):
    tweetids = FileField(
        validators=[
            FileAllowed(tweetids, u'must be .txt or .csv'),
            FileRequired(u'File was empty!')
        ]
    )
    submit = SubmitField(u'Upload')

@app.route('/', methods=['GET', 'POST'])
def upload_file():

    form = UploadForm()

    if form.validate_on_submit():
        filename = tweetids.save(form.tweetids.data)
        file_url = tweetids.url(filename)
    else:
        file_url = None

    # Authenticate twitter
    auth = tweepy.OAuthHandler(CONS_TOK, CONS_SEC)
    auth.set_access_token(APP_TOK,APP_SEC)
    api = tweepy.API(auth)
    tweets = []

    if file_url is not None:
        # Read file from the drive to avoid issues with MAC
        file_url = os.path.join(DATA_DIR,file_url.split('/')[-1])
        print(file_url)
        df = pd.read_csv(file_url)
        for r,i in df.iterrows():
            if 'ID_' in i.tweet_id_str:
                i = i.tweet_id_str.replace('ID_',"")

            tmp = api.get_oembed(id=i,omit_script=False)
            tweets.append(
                tmp
            )
    return render_template('render_tweets.html',form=form, file_url=file_url,tweets=tweets)

## --------- ##

if __name__ == '__main__':
    app.run(debug=True)
