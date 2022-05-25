import logging
from sys import exc_info
import json
import requests
import os
from flask import Flask, render_template, request, redirect
from opencensus.ext.azure.log_exporter import AzureLogHandler
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Setup up a Flask instance
app = Flask(__name__)

# Setup logging mechanism
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string=os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING'))
)

# Get the time from a public API on the Internet
def get_time():
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
    
# Get Key Vault secret
def get_secret():

    VAULT_NAME = os.getenv('KEY_VAULT_NAME')
    KEY_VAULT_SECRET_NAME = os.getenv('KEY_VAULT_SECRET_NAME')
    try:
        if 'MSI_CLIENT_ID':
            credential = DefaultAzureCredential(
                managed_identity_client_id=os.getenv('MSI_CLIENT_ID')
            )
        else:
            raise Exception
    except Exception:
        return "Unable to obtain access token"
        logger.error('Failed to obtain access token', exc_info=True)
    try:
        secret_client = SecretClient(
            vault_url=f"https://{VAULT_NAME}.vault.azure.net/", credential=credential)
        secret = secret_client.get_secret(f"{KEY_VAULT_SECRET_NAME}")
        return secret.value
    except Exception:
        return "Unable to obtain the secret"
        logger.error('Failed to get secret', exc_info=True)

# Render the template
@app.route("/")
def index():
    return render_template('index.html')

# Make functions available to web template
app.jinja_env.globals.update(get_time=get_time)
app.jinja_env.globals.update(get_secret=get_secret)
