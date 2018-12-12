import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import numpy as np 

scope = ['https://www.googleapis.com/auth/spreadsheets']

creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
gc = gspread.authorize(creds)

def get_sheet_id(spreadsheet,sheet_name):
    for w in spreadsheet.worksheets():
        if w.title == sheet_name:
            return w.id
    return None

def initialize_header(worksheet):
    if worksheet.cell(1,2).value != 'user':
        worksheet.update_cell(1,2,'user')

    if worksheet.cell(1,3).value != 'comments':
        worksheet.update_cell(1,3,'comments')

def get_worksheet(url,sheet_name='Sheet1'):

    spreadsheet=gc.open_by_url(url)
    ws_id = get_sheet_id(spreadsheet,sheet_name)
    worksheet=spreadsheet.get_worksheet(ws_id)

    return worksheet

def get_last_commented_row(worksheet):
    df=pd.DataFrame(worksheet.get_all_values())
    return np.nonzero(df.loc[:,1] == '')[0][0]+1

