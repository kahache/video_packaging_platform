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
import random

# We declare variables
storage_dir = os.getcwd() + "/../storage/"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = storage_dir

# We define the table we're going to use
db_name = "video_files"
uploaded_videos = Table('uploaded_videos', metadata, autoload=True)


@app.route('/')
def index():
    return render_template("index.html")


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
        input_content_origin = (storage_dir + f.filename)
        result = Video_ops.video_ingest(path)
        if (result[-1]) == 1:
            uploaded_videos = Table('uploaded_videos', metadata, autoload=True)
            con = engine.connect()
            con.execute(uploaded_videos.insert(), input_content_origin=input_content_origin, status="Ingested",
                        video_track_number=result[1])
            input_content_id = \
                con.execute(
                    uploaded_videos.select(uploaded_videos.c.input_content_origin == input_content_origin)).fetchone()[
                    0]
            return render_template("success.html", name=f.filename, input_content_id=input_content_id)
        else:
            print(result)
            return "ERROR - Check command line"


@app.route('/packaged_content', methods=['POST'])
def package():
    if request.method == 'POST':
        #añadir condición para evitar duplicados
        uploaded_videos = Table('uploaded_videos', metadata, autoload=True)
        con = engine.connect()
        print(request.is_json)
        uploaded_json = request.get_json()
        input_content_id = uploaded_json['input_content_id']
        video_key = uploaded_json['key']
        kid = uploaded_json['kid']
        # First file needs to be fragmented
        file_for_fragment = \
        con.execute(uploaded_videos.select(uploaded_videos.c.input_content_id == input_content_id)).fetchone()[1]
        print(file_for_fragment)
        fragmentation = Video_ops.video_fragment(file_for_fragment)
        if (fragmentation[-1]) == 1:
            packaged_content_id = random.randint(0, 100)
            result = con.execute(
                uploaded_videos.update().where(uploaded_videos.c.input_content_id == input_content_id).values(
                    status='Fragmented', output_file_path=fragmentation[1], video_key=video_key, kid=kid,
                    packaged_content_id=packaged_content_id))
            # Now we encrypt
            video_track_number = \
            con.execute(uploaded_videos.select(uploaded_videos.c.input_content_id == input_content_id)).fetchone()[2]
            file_to_encrypt = \
            con.execute(uploaded_videos.select(uploaded_videos.c.input_content_id == input_content_id)).fetchone()[4]
            encryptation = Video_ops.video_encrypt(video_track_number, video_key, kid, file_to_encrypt)
            if (encryptation[-1]) == 1:
                result = con.execute(
                    uploaded_videos.update().where(uploaded_videos.c.input_content_id == input_content_id).values(
                        status='Encrypted', output_file_path=encryptation[1]))
                # Now we get the DASH
                dash_convert = Video_ops.video_dash(encryptation[1])
                if (dash_convert[-1]) == 1:
                    result = con.execute(uploaded_videos.update().where(uploaded_videos.c.input_content_id == input_content_id).values(status='Ready', url=dash_convert[1]))
                    return render_template("success_packaged.html", url=dash_convert[1], packaged_content_id=packaged_content_id)
                else:
                    return ("ERROR - Check command line")
            else:
                return ("ERROR - Check command line")
        else:
            return ("ERROR - Check command line")


@app.route('/packaged_content_id/<int:packaged_content_id>', methods=['GET'])
def consult_status(packaged_content_id):
    if request.method == 'GET':
        print("ESTE ES EL NUMERO:\n\n")
        print(packaged_content_id)
        uploaded_videos = Table('uploaded_videos', metadata, autoload=True)
        con = engine.connect()
        status = con.execute(uploaded_videos.select(uploaded_videos.c.packaged_content_id == packaged_content_id)).fetchone()[3]
        url = con.execute(uploaded_videos.select(uploaded_videos.c.packaged_content_id == packaged_content_id)).fetchone()[8]
        video_key = con.execute(uploaded_videos.select(uploaded_videos.c.packaged_content_id == packaged_content_id)).fetchone()[5]
        kid = con.execute(uploaded_videos.select(uploaded_videos.c.packaged_content_id == packaged_content_id)).fetchone()[6]
        print("RESULTADOS:\n\n")
        print(status)
        print(url)
        if status == 'Ready':
            data_set = {"url": [url], "key": [video_key], "kid": [kid]}
            return(data_set)
        else:
            output = ("The packaged_content_id with number" + packaged_content_id + "is currently with status" + status )
            return (output)

if __name__ == '__main__':
    app.run(host='0.0.0.0')
