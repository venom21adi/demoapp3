


#-----------------------------------

from flask import *  
from werkzeug.utils import secure_filename


import os
import pandas as pd




#-----------------------------------
app = Flask(__name__)
app.secret_key = os.urandom(24)



    
@app.route('/', methods=['GET', 'POST'])
def login():
    return render_template("login.html")
    


if __name__ == "__main__":
    app.run()

           
