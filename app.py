


#-----------------------------------

from flask import *  
from werkzeug.utils import secure_filename


import os



#-----------------------------------
app = Flask(__name__)
app.secret_key = os.urandom(24)



    
@app.route('/login/', methods=['GET', 'POST'])
def login():
    return"Hello cruel world!"


if __name__ == "__main__":
    app.run()

           
