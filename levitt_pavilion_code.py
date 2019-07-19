from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
import os
from httplib2 import Http
from oauth2client import file, client, tools
from email.mime.text import MIMEText
from base64 import urlsafe_b64encode
import yaml

# Change current working directory
if os.getcwd()[-6:] == 'Budget':
    os.chdir(os.getcwd()[0:-6] + 'levitt_pavilion')

# Load in .yml file to retrieve user information for appropriate user
info = yaml.load(open("email_information_retrieval.yml"), Loader=yaml.FullLoader)
# Retrieve username and email
current_directory, sender_email, client_secret_json, credentials_json, token_pickle = \
                                                  info['user']['current_directory'], \
                                                  info['user']['email'], \
                                                  info['user']['client_secret_json'], \
                                                  info['user']['credentials_json'],\
                                                  info['user']['token']

# Change to appropriate directory
os.chdir(current_directory)

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']  # Allows sending only, not reading
def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """

    global creds, service_levitt
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_pickle):
        with open(token_pickle, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    # Initialize the object for the Gmail API
    # https://developers.google.com/gmail/api/quickstart/python
    store = file.Storage(credentials_json)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets(client_secret_json, SCOPES)
        creds = tools.run_flow(flow, store, flags=tools.argparser.parse_args(args=[]))
        service_levitt = build('gmail', 'v1', http=creds.authorize(Http()))
    # if not creds or not creds.valid:
    #     if creds and creds.expired and creds.refresh_token:
    #         creds.refresh(Request())
    #     else:
    #         flow = InstalledAppFlow.from_client_secrets_file(
    #             'client_secret_two.json', SCOPES)
    #         creds = flow.run_local_server()
        # Save the credentials for the next run
        with open(token_pickle, 'wb') as token:
            pickle.dump(creds, token)
    #service_levitt = build('gmail', 'v1', credentials=creds)
    service_levitt = build('gmail', 'v1', http=creds.authorize(Http()))

if __name__ == '__main__':
    main()

SENDER = sender_email
RECIPIENT = input("Type recipient's email address.")
SUBJECT = 'i just sent you'
CONTENT = 'a test email from Python'

# https://developers.google.com/gmail/api/guides/sending
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
  encoded_message = urlsafe_b64encode(message.as_bytes())
  return {'raw': encoded_message.decode()}


# https://developers.google.com/gmail/api/guides/sending
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
    message = (service_levitt.users().messages().send(userId=user_id, body=message)
               .execute())
    print('Message Id: %s' % message['id'])
    return message
  #except errors.HttpError, error:
  except:
    print('An error occurred: %s' % error)

raw_msg = create_message(SENDER, RECIPIENT, SUBJECT, CONTENT)
send_message(service_levitt, "me", raw_msg)