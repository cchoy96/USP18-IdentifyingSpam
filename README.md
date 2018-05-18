# Identifying Spam Project

## Running a Flask Python File
First, enter your virtual environment with
$ . venv/bin/activate
(Type 'deactivate' to leave the virtual environment)

After you've created a Python file with your API routes:
$ export FLASK_APP=yourPythFile.py
$ flask run

Open a browser and go to 127.0.0.0 (or whatever the shell says the server is being hosted on.)

## Running the Python Script
Run $ python gmailscrapy.py

## Running the HTML/JS File
Navigate to the directory that holds the .html file (./templates/)
Run $ python -m SimpleHTTPServer 8000
Open a browser and go to:
localhost:8000/gmailscrape.html