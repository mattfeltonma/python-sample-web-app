import logging
import json
import requests
import os
from flask import Flask, render_template, request, redirect

# Setup up a Flask instance
app = Flask(__name__)

# Retrieve the time from an open API
def retrieve_time():
    try:
        response = requests.get(
            url="http://worldclockapi.com/api/json/utc/now"
        )
        if response.status_code == 200:
            time = (json.loads(response.text))['currentDateTime']
            return time
        else:
            logging.error(f"Error querying API.  Status code: {response.status_code}")
    except Exception:
        return "Retrieving time failed"

# Retrieve a Breaking Bad quote
def retrieve_quote():
    try:
        response = requests.get(
            url="https://breaking-bad-quotes.herokuapp.com/v1/quotes"
        )
        if response.status_code == 200:
            quote = (json.loads(response.text))[0]['quote']
            return quote
        else:
            logging.error(f"Error querying API.  Status code: {response.status_code}")
    except Exception:
        return "Retrieving quote failed"

# Render the template
@app.route("/")
def index():
    return render_template('index.html')

# Make functions available to web tempalte
app.jinja_env.globals.update(retrieve_time=retrieve_time)
app.jinja_env.globals.update(retrieve_quote=retrieve_quote)