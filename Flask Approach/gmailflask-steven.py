import json
import flask
import httplib2
import base64
import email

from apiclient import discovery, errors
from oauth2client import client
from flask.json import jsonify
from random import randint

app = flask.Flask(__name__)


@app.route('/')
def index():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        gmail_service = discovery.build('gmail', 'v1', http_auth)
        threads = gmail_service.users().threads().list(userId='me').execute()
        return json.dumps(threads)


@app.route('/oauth2callback')
def oauth2callback():
    flow = client.flow_from_clientsecrets(
        'static/client_secret.json',
        scope='https://www.googleapis.com/auth/gmail.readonly',
        redirect_uri=flask.url_for('oauth2callback', _external=True)
    )
    if 'code' not in flask.request.args:
        auth_uri = flow.step1_get_authorize_url()
        return flask.redirect(auth_uri)
    else:
        auth_code = flask.request.args.get('code')
        credentials = flow.step2_exchange(auth_code)
        flask.session['credentials'] = credentials.to_json()
        return flask.redirect(flask.url_for('index'))

@app.route('/getmail')
def getmail():
    if 'credentials' not in flask.session:
        return flask.redirect(flask.url_for('oauth2callback'))
    credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
    if credentials.access_token_expired:
        return flask.redirect(flask.url_for('oauth2callback'))
    else:
        http_auth = credentials.authorize(httplib2.Http())
        gmail_service = discovery.build('gmail', 'v1', http_auth)
        query = 'is:inbox'
        """List all Messages of the user's mailbox matching the query.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        query: String used to filter messages returned.
        Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

        Returns:
        List of Messages that match the criteria of the query. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate ID to get the details of a Message.
        """
        try:
            response = gmail_service.users().messages().list(userId='me', q=query).execute()
            messages = []
            if 'messages' in response:
                print 'test %s' % response
                messages.extend(response['messages'])
            while 'nextPageToken' in response:
                page_token = response['nextPageToken']
                response = gmail_service.users().messages().list(userId='me', q=query, pageToken=page_token).execute()
                messages.extend(response['messages'])
            inbox_size = len(messages)
            count = 0
            uniq_msg_ids = []
            uniq_senders = []
            final_messages_list = []
            temp_dict = {}
            while count <= 10:
                random_index = randint(0, inbox_size)
                msg = messages[random_index]
                m_id = msg['id']
                if m_id not in uniq_msg_ids:
                    uniq_msg_ids.extend(m_id)
                    message = GMAIL.users().messages().get(userId='me', id=m_id).execute()
                    sender = message['from']
                    if sender not in uniq_senders:
                        uniq_senders.extend(sender)
                        payID = message['payload']
                        header = payID['headers']
                        for one in header:
                            if one['name'] == 'Subject':
                                msg_subject = one['value']
                                temp_dict['Subject'] = msg_subject
                            else:
                                pass
                        for two in header:
                            if two['name'] == 'Date':
                                msg_date = two['value']
                                date_parse = (parse.parse(msg_data))
                                m_date = (date_parse.date())
                                temp_dict['Date'] = str(m_date)
                            else:
                                pass
                        for three in header:
                            if three['name'] == 'From':
                                msg_from = three['value']
                                temp_dict['Sender'] = msg_from
                            else:
                                pass
                            temp_dict['Snippet'] = message['snippet']
                            try:
                               msg_parts = payID['parts']
                               part_one = msg_parts[0]
                               part_body = part_one['body']
                               part_data = part_body['data']
                               clean_one = part_data.replace('-', '+')
                               clean_one = clean_one.replace('_', '/')
                               clean_two = base64.b64decode (bytes(clean_one, 'UTF-8'))
                               soup = BeautifulSoup(clean_two, 'lxml')
                               msg_body = soup.body()
                               temp_dict['Messages_body'] = msg_body
                            except:
                               pass
                           #print(temp_dict)
                            final_messages_list.append(temp_dict)
                            count += 1
                return final_list
                print(final_list)

            #return jsonify({'data': messages}) # changed here
        except errors.HttpError, error:
            print 'An error occurred: %s' % error


if __name__ == '__main__':
    import uuid
    app.secret_key = str(uuid.uuid4())
    app.debug = True
    app.run()

# https://stackoverflow.com/questions/29386727/python-flask-google-api-integration
