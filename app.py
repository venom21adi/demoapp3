
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions

import os
from datetime import datetime, timedelta

#-----------------------------------

from flask import *  
from flask import Flask, request, session 
#from flask_sqlalchemy import SQLAlchemy
from  flask_login import *

from  flask_login import LoginManager
import fitz
import pandas as pd
import requests
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




    
@app.route('/', methods=['GET'])
def index():
    if session.get('logged_in'):
        return render_template('path.html')
    elif request.method == "GET":
        return redirect("/login")



@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        u = request.form['username']
        p = request.form['password']
        if u == MASTER_USER and p == MASTER_PASSWORD:
            session['logged_in'] = "Value"
            return redirect(url_for('index'))
        return render_template('index.html', message="Incorrect Login Credentials")
    
    
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    return redirect(url_for('index'))





if __name__ == "__main__":
    app.run()

           
