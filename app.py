
from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions

import os
from datetime import datetime, timedelta

#-----------------------------------

from flask import *  

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
#container = app.config['CONTAINER'] # Container name
allowed_ext = app.config['ALLOWED_EXTENSIONS'] # List of accepted extensions
max_length = app.config['MAX_CONTENT_LENGTH'] # Maximum size of the uploaded file



blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    
def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in allowed_ext

def delete_container(blob_service_client, client):
    container_client = blob_service_client.get_container_client(container=client)
    container_client.delete_container()

def create_blob_container(blob_service_client,client):
    if session["flag"] =="survey":
        try:
            container_client = blob_service_client.create_container(name=client)
        except:
            pass
            # delete_container(blob_service_client, client)
            # container_client = blob_service_client.create_container(name=client)
    elif session["flag"] =="fi":
        try:
            container_client = blob_service_client.create_container(name=client)
        except:
            pass
            # delete_container(blob_service_client, client)
            # container_client = blob_service_client.create_container(name=client)
    elif session["flag"] =="HR":
        try:
            container_client = blob_service_client.create_container(name=client)
        except:
            pass
            # delete_container(blob_service_client, client)
            # container_client = blob_service_client.create_container(name=client)
    return "Container Created"

def delete_blob(blob_service_client):
    container = session["client"]
    container_client_analysis = blob_service_client.get_container_client(container=container)
    x = "test"
    blob_lst_delete =[]
    if session["flag"] == "survey" and session["type_i"] == "inclusivity": 
        for blob_i in container_client_analysis.list_blobs():
            blob_lst_delete.append(blob_i['name'])
        TYPE = "analysed_file"
        blob_lst_delete = [k for k in blob_lst_delete if TYPE in k]
        if len(blob_lst_delete)!=0:
            blob_client = blob_service_client.get_blob_client(container=container,blob =blob_lst_delete[0])
            blob_client.delete_blob()
    elif session["flag"] == "fi" and session["type_i"] == "focus":
        for blob_i in container_client_analysis.list_blobs():
            blob_lst_delete.append(blob_i['name'])
        TYPE = "analysed_file"
        blob_lst_delete = [k for k in blob_lst_delete if TYPE in k]
        for blob_i in blob_lst_delete:
                blob_client = blob_service_client.get_blob_client(container=container,blob =blob_i)
                blob_client.delete_blob()
    return None
                

def upload_file():
    x = delete_blob(blob_service_client)
    client = session["client"]
    if request.method == 'POST':
        img = request.files['file']
        if img and allowed_file(img.filename):
            filename = secure_filename(img.filename)
            img.save(filename)
            if session["flag"] == "survey":
                blob_client = blob_service_client.get_blob_client(container = client, blob = "inclusivity_analysis_survey/"+filename)
            elif session["flag"] == "fi" and session["type_i"]== "focus":
                blob_client = blob_service_client.get_blob_client(container = client, blob = "analysis_fi/focus/"+filename)
            elif session["flag"] == "fi" and session["type_i"]== "individual":
                blob_client = blob_service_client.get_blob_client(container = client, blob = "analysis_fi/individual/"+filename)
            elif session["flag"] == "HR" and session["type_i"]== "HR_Doc":
                blob_client = blob_service_client.get_blob_client(container = client, blob = "analysis_HR/HR/HR_Doc/"+filename)
            session["Analysis_file"] =  img.filename
            with open(filename, "rb") as data:
                try:
                    blob_client.upload_blob(data, overwrite=True)
                    msg = "Upload Done ! "
                except:
                    pass
            os.remove(filename)     
    return msg

def upload_survey_key2():

    client = session["client"]
    if request.method == 'POST':
        img = request.files['file1']
        if img and allowed_file(img.filename):
            filename = secure_filename(img.filename)
            img.save(filename)
            blob_client = blob_service_client.get_blob_client(container = client, blob = "inclusivity_surveykey/"+filename)
            session["Survey_key"] =  img.filename
            with open(filename, "rb") as data:
                try:
                    blob_client.upload_blob(data, overwrite=True)
                    msg = "Upload Done ! "
                except:
                    msg ="Effort failed!"
            os.remove(filename)
    return msg


def generate_SAS():
    blob_list = []
    df_lst = []
    container = session["client"]
    # analysis = "analysis"
    # survey_key = "surveykey"
    container_client_analysis = blob_service_client.get_container_client(container=container)
    #container_client_survey_key = blob_service_client.get_container_client(container=container)
    
    blob_list = []
    for blob_i in container_client_analysis.list_blobs():
        blob_list.append(blob_i.name)
    
    TYPE = session["type_i"]
    blob_list = [k for k in blob_list if TYPE in k]
    
    sas_url_lst = []
    
    for j in range(len(blob_list)):
        sas_analysis = generate_blob_sas(account_name = account,
                        container_name = container,
                        blob_name = blob_list[j],
                        account_key=key,
                        permission=BlobSasPermissions(read=True),
                        expiry=datetime.utcnow() + timedelta(hours=1))
        sas_url = 'https://' + account+'.blob.core.windows.net/' + container + '/' + blob_list[j] + '?' + sas_analysis
        sas_url_lst.append(sas_url)
        if session["flag"] == "survey":
            df = pd.ExcelFile(sas_url)
        elif session["flag"] == "HR":
            pass
        else:
            df = pd.read_csv(sas_url,encoding = "utf-8")
        df_lst.append(df)    
    
    return df_lst
    #return blob_list

def write_files(lst_write):
    container = session["client"]
    if session["flag"]== "survey":
        blob_client = blob_service_client.get_blob_client(container=container, blob="inclusivity_analysedfile/"+container+"_analysed_file")
        blob_client.upload_blob(lst_write, blob_type="BlockBlob", overwrite=True)
    elif session["flag"] == "fi" and session["type_i"]== "focus":
        lst_write2 = ["focus","summary","wordcloud.jpg"]
        for i in range(len(lst_write)):
            blob_client = blob_service_client.get_blob_client(container=container, blob="focus_analysedfile/"+container+"_focus_analysed_file"+lst_write2[i])
            blob_client.upload_blob(lst_write[i], blob_type="BlockBlob", overwrite=True)
            # if i<2:
            #     blob_client = blob_service_client.get_blob_client(container=container, blob="analysedfile/"+container+"_focus_analysed_file"+lst_write2[i])
            #     blob_client.upload_blob(lst_write[i], blob_type="BlockBlob", overwrite=True)
            # else:
            #     blob_client = blob_service_client.get_blob_client(container=container, blob="analysedfile/"+container+"_focus_analysed_file"+lst_write2[i])
            #     blob_client.upload_blob(lst_write[i], blob_type="BlockBlob", overwrite=True)
    elif session["flag"] == "fi" and session["type_i"]== "individual":
        lst_write2 = ["focus","summary","wordcloud.jpg"]
        for i in range(len(lst_write)):
            blob_client = blob_service_client.get_blob_client(container=container, blob="individual_analysedfile/"+container+"_focus_analysed_file"+lst_write2[i])
            blob_client.upload_blob(lst_write[i], blob_type="BlockBlob", overwrite=True)
            # if i<2:
            #     blob_client = blob_service_client.get_blob_client(container=container, blob="analysedfile/"+container+"_focus_analysed_file"+lst_write2[i])
            #     blob_client.upload_blob(lst_write[i], blob_type="BlockBlob", overwrite=True)
            # else:
            #     blob_client =  blob_service_client.create_blob_from_bytes(container, blob = "analysedfile/"+container+"_focus_analysed_file"+lst_write2[i])
            #     blob_client.upload_blob(lst_write[i], blob_type="BlockBlob", overwrite=True)
    elif session["flag"] == "not_survey" and session["type_stage"]== "dashboard":
        #lst_write2 = ["focus","summary","wordcloud.jpg"]
        for i in range(len(lst_write)):
            lst_write2 = ["Complete Scored Table.csv","Main_Table_Leadership_Level.csv",
                          "Main_Table_Organisational_level.csv","most_inclusive_params.csv",
                          "least_inclusive_params.csv","most_and_least_represented.csv"]
            blob_client = blob_service_client.get_blob_client(container=container, blob="dashboard_inclusivity_analysedfile/"+lst_write2[i])
            blob_client.upload_blob(lst_write[i], blob_type="BlockBlob", overwrite=True)
            # if i<2:
            #     blob_client = blob_service_client.get_blob_client(container=container, blob="analysedfile/"+container+"_focus_analysed_file"+lst_write2[i])
            #     blob_client.upload_blob(lst_write[i], blob_type="BlockBlob", overwrite=True)
            # else:
            #     blob_client =  blob_service_client.create_blob_from_bytes(container, blob = "analysedfile/"+container+"_focus_analysed_file"+lst_write2[i])
            #     blob_client.upload_blob(lst_write[i], blob_type="BlockBlob", overwrite=True)
    elif session["flag"] == "HR" and session["type_i"]== "HR_Doc":
        lst_write2 = [lst_write[0],lst_write[0]+"_analysed",lst_write[0]+"_wordcloud.jpg"]
        keyword = lst_write[0]
        lst_write = lst_write[1:]
        for i in range(len(lst_write)):
            blob_client = blob_service_client.get_blob_client(container=container, blob="analysed_HR"+"//"+keyword+"//"+lst_write2[i]+"_"+container++"_HR_Doc_analysed_file")
            blob_client.upload_blob(lst_write[i], blob_type="BlockBlob", overwrite=True)
            # if i<2:
            #     blob_client = blob_service_client.get_blob_client(container=container, blob="analysedfile/"+container+"_focus_analysed_file"+lst_write2[i])
            #     blob_client.upload_blob(lst_write[i], blob_type="BlockBlob", overwrite=True)
            # else:
            #     blob_client =  blob_service_client.create_blob_from_bytes(container, blob = "analysedfile/"+container+"_focus_analysed_file"+lst_write2[i])
            #     blob_client.upload_blob(lst_write[i], blob_type="BlockBlob", overwrite=True)

    return None
    
def download_blob_to_file():
    container = session["client"]
    blob_list_download = []
    container_client_analysis = blob_service_client.get_container_client(container=container)
    
    for blob_i in container_client_analysis.list_blobs():
        blob_list_download.append(blob_i.name)
    
    TYPE = session["type_i"]    
    blob_list_download = [k for k in blob_list_download if TYPE in k]
    if session["flag"]== "survey":
        for blob_i in container_client_analysis.list_blobs():
            blob_list_download.append(blob_i.name)
        blob=blob_list_download[0]
    elif session["flag"] == "fi":
        for blob_i in container_client_analysis.list_blobs():
            blob_list_download.append(blob_i.name)
    for blob_i in blob_list_download:
        file_data = "C:\\EDI\\"
        blob_client = blob_service_client.get_blob_client(container=container, blob=blob_i)
        with open(file =filedata, mode="wb") as download_file:
              download_file.write(container_client_analysis.download_blob(blob_i).readall())
    return file_data
    # return blob_list_download
    # return blob_list_download[0]


    
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



#-------------------------------------------------------------------
@app.route('/path')
def path_options():
    option = request.args.get("options2")
    if option == "Perform Analysis":
        return redirect("/choice_pre")  
    elif option == "View Dashboard":
        return redirect("/dashboard")  
#-------------------------------------------------------------------

#-------------------------------------------------------------------
@app.route('/dashboard')
def dashboard():
    return render_template("dashboard.html")

@app.route('/choice_pre')
def choice_pre():
    return render_template("choice.html") 

@app.route('/choice')
def options():
  client = request.args.get("client")
  session["client"] = client

  option = request.args.get("options")
  if option == "Inclusivity Survey Assessment":
    session["flag"] = "survey"
    session["type_i"]= "inclusivity"
    container_flag = create_blob_container(blob_service_client,client)
    if container_flag == "Container Created":
        return redirect("/upload")  
  elif option == "Focus Group Interview Analysis":
    session["flag"] = "fi"
    session["type_i"]= "focus"
    container_flag = create_blob_container(blob_service_client,client)
    if container_flag == "Container Created":
        return redirect("/upload_fi")  
  elif option == "Individual Interview Analysis":
    session["flag"] = "fi"
    session["type_i"]= "individual"
    container_flag = create_blob_container(blob_service_client,client)
    if container_flag == "Container Created":
        return redirect("/upload_fi")
  elif option == "HR Document Analysis":
    session["flag"] = "HR"
    session["type_i"]= "HR_Doc"
    container_flag = create_blob_container(blob_service_client,client)
    if container_flag == "Container Created":
        return redirect("/upload_fi_HR") 
  else:
      return "Something is wrong"

#-------------------------------------------------------------------
@app.route('/upload')  
def upload():
    return render_template("upload.html",client = session["client"])  

@app.route('/upload_survey_key',methods = ['POST'])  
def upload_survey_key():
    message = upload_file()
    return render_template("upload_survey_key.html")  

@app.route('/upload_fi')  
def upload_fi():
    return render_template("upload_fi.html") 

@app.route('/upload_fi_HR')  
def upload_fi_HR():
    return render_template("upload_fi_HR.html") 
#-------------------------------------------------------------------
#-------------------------------------------------------------------


@app.route('/success',methods = ['POST'])  
def success():
    message2 = upload_survey_key2()
    analysis_file_name = session["Analysis_file"]
    survey_key_file_name = session["Survey_key"] 
    client_name = session["client"]
    return render_template("success.html", name = analysis_file_name,survey_key = survey_key_file_name,clientname = client_name)

@app.route('/success_fi',methods = ['POST'])  
def success_fi():
    message = upload_file()
    analysis_file_name = session["Analysis_file"]
    return render_template("success_fi.html", name = analysis_file_name) 

@app.route('/success_fi_HR',methods = ['POST'])  
def success_fi_HR():
    message = upload_file()
    analysis_file_name = session["Analysis_file"]
    return render_template("success_fi_HR.html", name = analysis_file_name) 

#-------------------------------------------------------------------

@app.route('/analysis',methods = ['POST'])  
def analysis():
    analysis_file_name = session["Analysis_file"]
    survey_key_file_name = session["Survey_key"] 
    client_name = session["client"]
    return render_template("analysis.html", analysis_file_name = analysis_file_name,survey_key_file_name = survey_key_file_name,client_name = client_name) 

@app.route('/analysis_fi',methods = ['POST'])  
def analysis_fi():
    client_name = session["client"]
    analysis_file_name = session["Analysis_file"]
    return render_template("analysis_fi.html",client_name=client_name,analysis_file_name=analysis_file_name) 

@app.route('/analysis_HR',methods = ['POST'])  
def analysis_HR():
    client_name = session["client"]
    analysis_file_name = session["Analysis_file"]
    return render_template("analysis_HR.html",client_name=client_name,analysis_file_name=analysis_file_name) 

#-------------------------------------------------------------------


@app.route('/analysis_process',methods = ['GET','POST'])  
def analysis_p():
    x = generate_SAS()
    from script.Inclusivity_survey_asessment_script import survey_key
    z = survey_key(x[1],x[0])
    op = z.to_csv(encoding= "utf-8")
    write_files(op)
    return render_template("analysis_process.html")
    # return x
    


    
@app.route('/analysis_process_fi',methods = ['POST'])  
def analysis_p_fi():
    x = generate_SAS()
    # from script.Combined_phrase_extraction_v8_dep import rating_gen
    # FILE = x[0]
    # ORG_NAME = session["client"]
    # TYPE = session["type_i"]
    # df,summary,PHRASES = rating_gen(FILE,ORG_NAME,TYPE)
    # op1 = df.to_csv(encoding= "utf-8")
    # summary = pd.DataFrame(summary, index=[0])
    # op2 = summary.to_csv(encoding= "utf-8")
    # from script.word_cloud_v1 import wordcloud
    # op3 = wordcloud(PHRASES,ORG_NAME,TYPE)
    # lst_write = [op1,op2,op3]
    # write_files(lst_write)
    y = "Analysis is complete. You can download the file"

    return render_template("analysis_process_fi.html",data = y)

@app.route('/analysis_fi_HR1',methods = ['POST'])  
def analysis_fi_HR1():
    x = generate_SAS()
    #x = [x]
    #from script.HR_extraction_v6 import master_func
    FILE = x[0]
    ORG_NAME = session["client"]
    TYPE = session["type_i"]
    KEYWORD_LIST = ["diversity","equity"]
    OP_LIST = master_func(FILE,KEYWORD_LIST)
    for j in range(len(OP_LIST)):
        op1 = OP_LIST[j][0]
        op2 = OP_LIST[j][1]
        op3 = OP_LIST[j][2]
        lst_write = [op1,op2,op3]
        write_files(lst_write)
        
    # op1 = df.to_csv(encoding= "utf-8")
    # summary = pd.DataFrame(summary, index=[0])
    # op2 = summary.to_csv(encoding= "utf-8")
    # from script.word_cloud_v1 import wordcloud
    # op3 = wordcloud(PHRASES,ORG_NAME,TYPE)
    # lst_write = [op1,op2,op3]
    # write_files(lst_write)
    # y = "Analysis is complete. You can download the file"

    # return render_template("analysis_process_fi.html",data = y)
    # return x
    return "test"

@app.route('/dashboard_creation',methods = ['POST'])  
def dashboard_creation():
    blob_list = []
    container = session["client"]
    session["flag"]= "not_survey"
    session["type_stage"]= "dashboard"
    container_client_analysis = blob_service_client.get_container_client(container=container)
    
    blob_list = []
    for blob_i in container_client_analysis.list_blobs():
        blob_list.append(blob_i.name)
    
    TYPE = "analysed_file"
    blob_list = [k for k in blob_list if TYPE in k]
    
    sas_url_lst = []
    
    sas_analysis = generate_blob_sas(account_name = account,
                    container_name = container,
                    blob_name = blob_list[0],
                    account_key=key,
                    permission=BlobSasPermissions(read=True),
                    expiry=datetime.utcnow() + timedelta(hours=1))
    sas_url = 'https://' + account+'.blob.core.windows.net/' + container + '/' + blob_list[0] + '?' + sas_analysis
    sas_url_lst.append(sas_url)
    df = pd.read_csv(sas_url,encoding = "utf-8")
    
    #-----------------------------
    #from script.PowerBI_Pre_Prep_script_v15 import dashboard_creation
    op_master = dashboard_creation(df)
    lst_write = op_master
    write_files(lst_write)

    y = "Analysis is complete. You can download the file"

    #return render_template("analysis_process_fi.html",data = y)
    return "test"

#-------------------------------------------------------------------
@app.route('/download',methods = ['POST'])
def downloadFile ():
    #For windows you need to use drive name [ex: F:/Example.pdf]
    x  = download_blob_to_file()
    return x

@app.route('/download_fi',methods = ['POST'])
def downloadFile_fi ():
    #For windows you need to use drive name [ex: F:/Example.pdf]
    x  = download_blob_to_file()

    return x

#-------------------------------------------------------------------
if __name__ == "__main__":
    app.run()

           
