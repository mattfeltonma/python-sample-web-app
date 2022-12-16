import logging
import json
import os
import requests
from sys import exc_info
from flask import Flask, render_template, request, redirect
from opencensus.ext.azure.log_exporter import AzureLogHandler
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Setup logging mechanism
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)
logger.addHandler(AzureLogHandler(
    connection_string=os.getenv('APPLICATIONINSIGHTS_CONNECTION_STRING'))
)


# Setup up a Flask instance
app = Flask(__name__)

# Obtain time from public api
def query_time():
    try:
        response = requests.get(
            url="http://worldtimeapi.org/api/timezone/america/new_york",
            timeout=5
        )

        if response.status_code == 200:
            time = (json.loads(response.text))['datetime']
            logger.info('Successfully queried public API')
            return time
        elif response.status_code != 200:
            logger.error(
                f"Error querying API.  Status code: {response.status_code}")
            return "Unavailable"
            
    except Exception:
        logger.error('Failed to contact public api', exc_info=True)
        return "Unavailable"

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
        logger.error('Failed to obtain access token', exc_info=True)
        raise Exception(
            'Failed to obtain access token'
        )

    try:
        secret_client = SecretClient(
            vault_url=f"https://{VAULT_NAME}.vault.azure.net/", credential=credential)
        secret = secret_client.get_secret(f"{KEY_VAULT_SECRET_NAME}")
        return secret.value
    except Exception:
        logger.error('Failed to get secret', exc_info=True)
        raise Exception(
            'Failed to get secret'
        )

def get_ip(web_request):
    if 'X-Forwarded-For' in web_request.headers:
        xforwardfor = web_request.headers['X-Forwarded-For']
        return web_request.remote_addr + f" and X-Forwarded-For header value of {xforwardfor}"
    else:
        return web_request.remote_addr

# Render the template
@app.route("/")
def index():
    ipinfo = get_ip(web_request=request)
    wordoftheday = get_secret()
    todaystime = query_time()
    return render_template('index.html', wordoftheday=wordoftheday, time=todaystime, ip=ipinfo)
