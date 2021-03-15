import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
from googleapiclient import errors
import base64

SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

def build_service():
  creds = None
  # The file token.pickle stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
      creds = pickle.load(token)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
        'gmail_creds.json', SCOPES)
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    path = os.path.abspath('token.pickle')
    with open(path, 'wb') as token:
      pickle.dump(creds, token)
  service = build('gmail', 'v1', credentials=creds)
  return service

def create_message(sender, to, subject, message_text):
  """Create a message for an email.

  Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email message.
    message_text: The text of the email message.

  Returns:
    An object containing a base64url encoded email object.
  """
  message = MIMEText(message_text)
  message['to'] = to
  message['from'] = sender
  message['subject'] = subject
  return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

def send_message(service, user_id, message):
  """Send an email message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    message: Message to be sent.

  Returns:
    Sent Message.
  """
  try:
    message = (service.users().messages().send(userId=user_id, body=message)
               .execute())
    print('Message Id: %s' % message['id'])
    return message
  except Exception as error:
    print('An error occurred: %s' % error)

"""
After importing gmail_controller, use the following three lines as a model (the parameters passed to create_message, other than the first one (tweetview.Albany@gmail.com), need to change)  
service = build_service()
message = create_message('tweetview.Albany@gmail.com', 'sjacks26@gmail.com', 'Testing the Gmail API', 'Does this work a second time??')
sent_message = send_message(service, 'me', message)
"""
