from typing import List, Dict
from flask import *
import mysql.connector
import json
from database import *
from video_ops import *
import os
import subprocess
import sys
import requests

#We declare variables
storage_dir=os.getcwd()+"/../storage/"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = storage_dir

#We define the table we're going to use
db_name="video_files"
table_name="movie_files"
#We modify here the MySQL config parameters
config = {
    'user': 'root',
    'password': 'root',
    'host': '127.0.0.1',
    'port': '3306',
    'database': 'video_files'
}
Database.__init__(db_name,table_name)

@app.route('/')
def index():
    result=str(Database.view_all(table_name))
    print(result)
    return result

@app.route('/upload_input_content')
def upload():
    return render_template("file_upload_form.html")

@app.route('/success', methods = ['POST'])
def success():
    if request.method == 'POST':
        app.config['UPLOAD_FOLDER'] = storage_dir
        f = request.files['file']
        #f.save(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
        #video_ingest(os.path.join(app.config['UPLOAD_FOLDER'], f.filename))
        f.save(f.filename)
        path=(os.getcwd()+"/"+f.filename)
        result=Video_ops.video_ingest(path)
        if (result[-1]) == 1:
            Database.insert_one_row(table_name,"input_content_origin",f.filename)
            input_content_id=(Database.view_one_value("input_content_id",table_name,"input_content_origin",f.filename))
            Database.update(table_name,"status","Ingested",str(input_content_id))
            return render_template("success.html", name = f.filename, input_content_id=input_content_id)
        else:
            print(result)
            return "ERROR - Check command line"

@app.route('/packaged_content', methods = ['POST'])
def package():
        if request.method == 'POST':
            print (request.is_json)
            uploaded_json = request.get_json()
            input_content_id=uploaded_json['input_content_id']
            video_key=uploaded_json['key']
            kid=uploaded_json['kid']
            #video_fragmentation
            file_for_fragment=(Database.view_one_value("input_content_origin",table_name,"input_content_id",input_content_id))
            fragmentation=Video_ops.video_fragment(file_for_fragment)
            if (fragmentation[-1]) == 1:
                Database.update(table_name,"status","Fragmented",str(input_content_id))
                Database.update(table_name,"output_file_path",fragmentation[1],str(input_content_id))
                Database.update(table_name,"video_key",video_key,str(input_content_id))
                Database.update(table_name,"kid",kid,str(input_content_id))
                #Now we encrypt
                video_track_number=(Database.view_one_value("video_track_number",table_name,"input_content_id",input_content_id))
                file_to_encrypt=(Database.view_one_value("output_file_path",table_name,"input_content_id",input_content_id))
                encryptation=Video_ops.video_encrypt(video_track_number,video_key,kid,file_to_encrypt)
                #updatear BBDD
            #    print(Database.view_one_value("input_content_id",table_name,"output_file_path",file))
                #Database.view_all(table_name)
            else:
                print(file_for_fragment)
            #print (input_content_id)
            #data = json.load(content)
            #item = data.get('input_content_id')
            #print(data)

            return 'JSON posted'

if __name__ == '__main__':
    app.run(host='0.0.0.0')
