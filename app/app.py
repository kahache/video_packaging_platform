from typing import List, Dict
from flask import *
import mysql.connector
import json
from database import *
from video_ops import *
from models import *
import os
import subprocess
import sys
import requests
# from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy.sql import *

# We declare variables
storage_dir = os.getcwd() + "/../storage/"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = storage_dir

# We define the table we're going to use
db_name = "video_files"
uploaded_videos = Table('uploaded_videos', metadata, autoload=True)


@app.route('/')
def index():
    result = engine.execute('select * from uploaded_videos where input_content_id = 1').first()
    print(result)
    return result


@app.route('/upload_input_content')
def upload():
    return render_template("file_upload_form.html")


@app.route('/success', methods=['POST'])
def success():
    if request.method == 'POST':
        app.config['UPLOAD_FOLDER'] = storage_dir
        f = request.files['file']
        f.save(f.filename)
        path = (os.getcwd() + "/" + f.filename)
        input_content_origin=(storage_dir + f.filename)
        result = Video_ops.video_ingest(path)
        if (result[-1]) == 1:
            print(result)
            print(result[1])
            uploaded_videos = Table('uploaded_videos', metadata, autoload=True)
            con = engine.connect()
            con.execute(uploaded_videos.insert(), input_content_origin=input_content_origin, status="Ingested", video_track_number=result[1])
            input_content_id = \
            con.execute(uploaded_videos.select(uploaded_videos.c.input_content_origin == input_content_origin)).fetchone()[0]
            return render_template("success.html", name=f.filename, input_content_id=input_content_id)
        else:
            print(result)
            return "ERROR - Check command line"


@app.route('/packaged_content', methods=['POST'])
def package():
    if request.method == 'POST':
        uploaded_videos = Table('uploaded_videos', metadata, autoload=True)
        con = engine.connect()
        print(request.is_json)
        uploaded_json = request.get_json()
        input_content_id = uploaded_json['input_content_id']
        video_key = uploaded_json['key']
        kid = uploaded_json['kid']
        # video_fragmentation
        file_for_fragment = con.execute(uploaded_videos.select(uploaded_videos.c.input_content_id == input_content_id)).fetchone()[1]
       # print(file_for_fragment)
        fragmentation = Video_ops.video_fragment(file_for_fragment)
        if (fragmentation[-1]) == 1:
            result = con.execute(
                uploaded_videos.update().where(uploaded_videos.c.input_content_id == input_content_id).values(
                    status='Fragmented', output_file_path=fragmentation[1], video_key=video_key, kid=kid))
        #   Database.update(table_name, "status", "Fragmented", str(input_content_id))
        #  Database.update(table_name, "output_file_path", fragmentation[1], str(input_content_id))
        # Database.update(table_name, "video_key", video_key, str(input_content_id))
        # Database.update(table_name, "kid", kid, str(input_content_id))
        # Now we encrypt
        # video_track_number = (
        #   Database.view_one_value("video_track_number", table_name, "input_content_id", input_content_id))
        # file_to_encrypt = (
        #   Database.view_one_value("output_file_path", table_name, "input_content_id", input_content_id))
        # encryptation = Video_ops.video_encrypt(video_track_number, video_key, kid, file_to_encrypt)
        # updatear BBDD
        #    print(Database.view_one_value("input_content_id",table_name,"output_file_path",file))
        # Database.view_all(table_name)
        else:
            print(file_for_fragment)
            print (input_content_id)
            #data = json.load(content)
            #item = data.get('input_content_id')
            #print(data)

        return 'JSON posted'


if __name__ == '__main__':
    app.run(host='0.0.0.0')
