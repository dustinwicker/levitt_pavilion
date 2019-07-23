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
import pandas as pd
from datetime import datetime as dt, timedelta
from selenium import webdriver
import re
from collections import OrderedDict
from itertools import repeat
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options

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

#### Get free events off Levitt Pavilion page #####

# # Get webdriver to work in the background (without popping up)
# options = Options()
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')
# options.add_argument("javascript.enabled")

# Define Chrome webdriver
driver = webdriver.Chrome()
# Supply url
driver.get(url="https://www.levittdenver.org/")

my_href = driver.find_element_by_xpath('//div[@class="Header-inner Header-inner--top"]//div[@data-nc-container="top-right"]//'
  'nav[@class="Header-nav Header-nav--primary"]//div[@class="Header-nav-inner"]//'
  'span[@class="Header-nav-item Header-nav-item--folder"]//a[@href="/events-page"]').get_attribute(name='href')

driver.execute_script("window.open('" + my_href +"');")

# Obtain position of current window handle in window handles list
current_window_handle_index = driver.window_handles.index(driver.current_window_handle)
# Obtain position of newly opened tab
new_window_handle_index = current_window_handle_index + 1
driver.switch_to.window(driver.window_handles[new_window_handle_index])

# Check to see if on the correct page (i.e., the free events page)
if 'free-events' in driver.current_url:
    print("Currently on the free events page for Levitt Pavilion. Okay to proceed.")
else:
    print("Not on the correct page (need to be on the free events page).")

# Obtain all concert-information
all_concerts = driver.find_elements_by_xpath('//div[@class="summary-content sqs-gallery-meta-container"]')

# Create list of lists of each event with date and event
all_concerts_list = []
for i in range(0, len(all_concerts)):
    concert = all_concerts[i].text.split('\n')
    if '2019' in concert[1]:
        concert = concert[::-1]
    all_concerts_list.append(concert)
# Create DataFrame from list of lists
all_concerts_df = pd.DataFrame(all_concerts_list, columns=['date', 'event'])

# Convert object column to datetime
all_concerts_df['date'] = pd.to_datetime(all_concerts_df['date'])

for i in range(0, len(all_concerts_df)):
    if all_concerts_df['date'][i].date() - dt.today().date() == timedelta(2):
        print("The following concert is happening in two days. Email user(s) to inform them.\n")
        print(all_concerts_df.iloc[i])
        concert_two_days_ahead = all_concerts_df.iloc[i]
        break

SENDER = sender_email
RECIPIENT = input("Type recipient's email address.")
SUBJECT = concert_two_days_ahead[1] + " at the Levitt Pavilion on " + concert_two_days_ahead[0].date().strftime("%B") +\
          " " + concert_two_days_ahead[0].date().strftime("%d") + ", " + concert_two_days_ahead[0].date().strftime("%Y")
CONTENT = "Hi (user)! " + concert_two_days_ahead[1] + " is playing at the Levitt Pavilion for free in two days on " +\
          concert_two_days_ahead[0].date().strftime("%B") + " " + concert_two_days_ahead[0].date().strftime("%d") +\
          ", " + concert_two_days_ahead[0].date().strftime("%Y") + "!\n\n" + "Hope to see you there!\n\n" +\
          "For more information, such as the event location and time, visit: " \
          "https://www.levittdenver.org/free-events"

raw_msg = create_message(SENDER, RECIPIENT, SUBJECT, CONTENT)
send_message(service_levitt, "me", raw_msg)