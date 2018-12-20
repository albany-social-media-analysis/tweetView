import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np 
from google.oauth2 import service_account
import googleapiclient.discovery

CRED_PATH='/network/rit/lab/schiraldilab/repos/tweetView/client_secret.json'
scope = ['https://www.googleapis.com/auth/spreadsheets']

creds = ServiceAccountCredentials.from_json_keyfile_name(
    'client_secret.json', scope
)

def url_to_id(spreadsheet_url):
    spreadsheet_url=spreadsheet_url.replace(
        'https://docs.google.com/spreadsheets/d/',''
    )
    return spreadsheet_url.split('/')[0]
  

# def initialize_header(worksheet):
#     if worksheet.cell(1,2).value != 'user':
#         worksheet.update_cell(1,2,'user')

#     if worksheet.cell(1,3).value != 'comments':
#         worksheet.update_cell(1,3,'comments')

def get_worksheet(gc,spreadsheet_url,sheet_name):

    spreadsheet=gc.open_by_url(spreadsheet_url)
    worksheets=spreadsheet.worksheets()
    for w in worksheets:
        if w.title == sheet_name:
            return w

def get_last_commented_row(worksheet):
    df=pd.DataFrame(worksheet.get_all_values())
    return np.nonzero(df.loc[:,1] == '')[0][0]+1

def get_validation_data(cred_path,spreadsheet_id,sheet_name,ranges):

    credentials = service_account.Credentials.from_service_account_file(
         cred_path, scopes=scope
        )
    service=googleapiclient.discovery.build(
        'sheets','v4',credentials=credentials
        )
    
    if 'docs.google.com' in spreadsheet_id:
        spreadsheet_id= url_to_id(spreadsheet_id)
    
    params={
        'spreadsheetId': spreadsheet_id,
        'ranges': ranges,
        'fields': 'sheets(data/rowData/values/dataValidation,properties(sheetId,title))'
    }
    request = service.spreadsheets().get(**params)
    response = request.execute()

    for r in response['sheets']:
        if r['properties']['title'] == sheet_name:
            return r['data'][0]
