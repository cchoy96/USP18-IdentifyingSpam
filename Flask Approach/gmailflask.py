import json
import flask
import httplib2
import base64
import email

from apiclient import discovery, errors
from oauth2client import client
from flask.json import jsonify

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
        print 'HERE4'
        print flask.session
        flask.session['credentials'] = credentials.to_json()
        print 'HERE5'
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

            return jsonify({'data': messages}) # changed here
        except errors.HttpError, error:
            print 'An error occ`urred: %s' % error


if __name__ == '__main__':
    print 'MAIN'
    import uuid
    app.secret_key = str(uuid.uuid4())
    app.debug = True
    app.run()

# https://stackoverflow.com/questions/29386727/python-flask-google-api-integration
