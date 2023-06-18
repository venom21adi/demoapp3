


#-----------------------------------

from flask import *  
import fitz
import pandas as pd
import requests

from werkzeug.utils import secure_filename


import os



#-----------------------------------
app = Flask(__name__)
app.secret_key = os.urandom(24)



    
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')


if __name__ == "__main__":
    app.run()

           
