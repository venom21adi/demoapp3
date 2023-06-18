


#-----------------------------------

from flask import *  
import fitz
import pandas as pd
import requests

from werkzeug.utils import secure_filename


import os

MASTER_USER = "test"
MASTER_PASSWORD = "test"

#-----------------------------------
app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config.from_pyfile('config.py')
account = app.config['ACCOUNT_NAME']   # Azure account name
key = app.config['ACCOUNT_KEY']      # Azure Storage account access key  
connect_str = app.config['CONNECTION_STRING']
allowed_ext = app.config['ALLOWED_EXTENSIONS'] # List of accepted extensions
max_length = app.config['MAX_CONTENT_LENGTH'] # Maximum size of the uploaded file



blob_service_client = BlobServiceClient.from_connection_string(connect_str)




    
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    
    





if __name__ == "__main__":
    app.run(port=8000)

           
