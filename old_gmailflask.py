from __future__ import print_function
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
def index():
	return 'Index Page'

@app.route('/hello')
def hello():
	return 'Hello World!'

@app.route('/user/<int:userid>')
def show_userid(userid):
	# print userid for that person
	return 'User %d' % userid

@app.route('/user/<username>')
def show_username(username):
	return "Hello, %s" % username

@app.route('/auth')
def auth():
	SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
	store = file.Storage('static/storedcredentials.json')
	creds = store.get()
	if not creds or creds.invalid:
	    flow = client.flow_from_clientsecrets('static/client_secret.json', SCOPES)
	    creds = tools.run_flow(flow, store)
	service = build('gmail', 'v1', http=creds.authorize(Http()))
	return 'DONE'
