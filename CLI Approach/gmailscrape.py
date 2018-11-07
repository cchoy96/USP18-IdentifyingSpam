# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from random import randint
import os, json, base64

credFile = 'storedcredentials.json'
mailFile = 'storedEmail_ids.txt'

# Setup the Gmail API
def authenticate ():
    SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
    store = file.Storage(credFile)
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    gmail_service = build('gmail', 'v1', http=creds.authorize(Http()))
    return gmail_service


# Pretty print a json object. For decoding purposes.
def jprint (parsed_json):
    print (json.dumps(parsed_json, indent=4, sort_keys=True), '\n')


# Make a GET query to retrieve a msg based on its id
def getMsg (GMAIL, m_id):
    return GMAIL.users().messages().get(userId='me', id=m_id).execute()


# Print relevant information from the message json
def printMsgDetails (message):
    hdrs = message['payload']['headers']
    subj = sender = target = cc = '[none]'
    for entry in hdrs:
        key = entry['name'].encode('utf-8')
        val = entry['value'].encode('utf-8')
        if key == 'Subject':
            subj = val
        if key == 'From':
            sender = val
        if key == 'To':
            target = val
        if key == 'CC':
            cc = val
    snippet = message['snippet'].encode('utf-8')
    print('Subject: {s}\nFrom: {f}\nTo: {t}\tCC: {c}\n{snip}\n=========\n'
          .format (s=subj, f=sender, t=target, c=cc, snip=snippet))


# Extract relevant information from the message json
def extractMsgDetails (message):
    hdrs = message['payload']['headers']
    subj = sender = target = cc = '[none]'
    for entry in hdrs:
        key = entry['name'].encode('utf-8')
        val = entry['value'].encode('utf-8')
        if key == 'Subject':
            subj = val
        if key == 'From':
            sender = val
        if key == 'To':
            target = val
        if key == 'CC':
            cc = val
    snippet = message['snippet'].encode('utf-8')


# Call the Gmail API
def getMessages (GMAIL, query):
    result = GMAIL.users().messages().list(userId='me', q=query).execute()
    msgs = result.get('messages', [])
    if not msgs:
        print('\tNo msgs found. Exiting...')
        exit(1)

    # for m in msgs:
    #     printMsgDetails(getMsg(GMAIL, m['id']))

    return msgs


# Extract n random, unique emails from the given set of emails
def extractRandomUnique (GMAIL, file, msgs, n):
    id_list = []
    for m in msgs:
        id_list.append(m['id'])
    i = 0
    max_idx = len(id_list) - 1
    while i < n:
        surveyMail = []
        surveyMail_ids = []
        surveyMail_snd = []
        for line in file:
            surveyMail.append(json.loads(line))
        for mail in surveyMail:
            surveyMail_ids.append(mail['id'])
        for mail in surveyMail:
            for entry in mail['payload']['headers']:
                if entry['name'].encode('utf-8') == 'Sender':
                    surveyMail_snd.append(entry['value']).encode('utf-8')
                    break

        # Randomize Email Selection. Don't select same email twice
        rand_idx = randint(0, max_idx)
        if id_list[rand_idx] in surveyMail_ids:
            print ('Duplicate mail id!')
            continue

        # Filter out duplicate senders
        target_msg = getMsg(GMAIL, id_list[rand_idx])
        for entry in target_msg['payload']['headers']:
            if entry['name'] == 'Sender':
                if entry['value'] in surveyMail_snd:
                    print('Duplicate Sender!')
                    continue
                else:
                    break

        file.write(str(id_list[rand_idx]) + '\n')
        i += 1


# Print out the email at IDX line in FILE
def printSurveyMail (GMAIL, file, idx):
    f = open(file, 'r')
    ids = []
    for line in f:
		ids.append(line[:-1])
    printMsgDetails(getMsg(GMAIL, ids[idx]))
    f.close()

# Remove Stored Credentials
def cleanup ():
    os.remove(credFile)
    os.remove(mailFile)
    print('Removed stored credentials and emails!')


def main ():
    print('Authenticating...')
    serv = authenticate()
    print('Authentication Complete!')

    print('Building 10 Survey Emails...')
    inboxMail = getMessages(serv, 'is:inbox')
    spamMail = getMessages(serv, 'is:spam')

    f = open(mailFile, 'w+')
    extractRandomUnique(serv, f, inboxMail, 5)
    extractRandomUnique(serv, f, spamMail, 5)
    f.close()

    print('Printing Emails...\n')
    for i in range(0,10):
        printSurveyMail(serv, mailFile, i)

    cleanup()
    print('\n---------\nScript Complete!')


main ()

# [END gmail_quickstart]
