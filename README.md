# tweetView
**Updating in progress**

tweetView is a tool for labeling tweets for research projects. It uses Twitter's oembed API and Google Sheets to create an interactive labeling environment that allows labelers to see tweets as they appear on Twitter.  
tweetView does not collect data. To use it, you should already have a collection of tweets that you want to label.

### External requirements
* A [Google developer account](https://console.developers.google.com/) (for the data administrator, not necessary for the data labelers). 
    * Under normal academic research uses, usage should fall into the free tier.
       
No Twitter account required! The oembed API is a non-authenticated API.

## Installation  
tweetView should be installed on a server or VM that has consistent uptime and access to the internet. To label data, users will navigate to a web client that communicates with the installation of tweetView on that server or VM.  
To install:
1) Clone the repo (`git clone https://github.com/nschiraldi/tweetView.git`).
2) Create the environment in tweetView/environment/environment.yml.  
    * If you use anaconda or miniconda, you can do this by running `conda env create -f environment/environment.yml` in the shell from the main tweetView directory.

To set up the Google developer account:
1) Turn on the Google Sheets API for your Google Developer Account (see https://developers.google.com/sheets/api/quickstart/python).
2) [Create service account credentials](https://gspread.readthedocs.io/en/latest/oauth2.html) for the Sheets API. Make sure you create the key for the service account credentials, which should download a client_secret json file. You'll need this file for tweetView. 

To run the tweetView service:  
* Note: tweetView runs in the foreground. Use tmux or screen to create a virtual terminal window so you can exit your SSH session without terminating tweetView. 
1) Activate the tweetView environment.
    * If you use anaconda or miniconda, do this by running `conda activate {environment name}`
2) CD to the tweetView directory
3) Run tweetView with `gunicorn -b 0.0.0.0:8091 app:app`
    * Note: you might need to open the firewall on your server or VM to allow users to access tweetView via browser.  
4) Access tweetView by navigating to http://{server or VM URL}:8091
