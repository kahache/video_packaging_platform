__author__ = "The One & Only Javi"
__version__ = "1.0.0"
__start_date__ = "25th July 2020"
__end_date__ = "5th August 2020"
__maintainer__ = "me"
__email__ = "little_kh@hotmail.com"
__requirements__ = "SQL-Alchemy, MySQL, Flask-SQLAlchemy, database.py, models.py, video_ops.py"
__status__ = "Production"
__description__ = """
This is the main Flask-App for the project. It will start running at
http://0.0.0.0:5000
This App is an API that lets the user process video files and prepare them into
encrypted MPEG-DASH ready to stream.
"""

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
uploaded_videos = Table('uploaded_videos', metadata, autoload=True)


@app.route('/')
def index():
    """Main API documentation as main Webpage"""
    return redirect("https://app.swaggerhub.com/apis-docs/kahache/VideoPackagingPlatform/1.0.0", code=302)


@app.route('/upload_input_content')
def upload():
    """Main website where users upload the video"""
    return render_template("file_upload_form.html")


@app.route('/success', methods=['POST'])
def success():
    """This method is called after a video is successfully uploaded"""
    if request.method == 'POST':
        """First, move file into storage and generate outputs"""
        app.config['UPLOAD_FOLDER'] = storage_dir
        f = request.files['file']
        f.save(f.filename)
        path = (os.getcwd() + "/" + f.filename)
        input_content_origin = (storage_dir + f.filename)
        """We call the video_ingest method to extract metadata and store the video"""
        result = Video_ops.video_ingest(path)
        """Return includes a '1' at the end if successful"""
        if (result[-1]) == 1:
            """As successful, we need to update the SQL database"""
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
    """When called with JSON, it will generate background operations with video files inside internal storage
    It works with nested operations, if one operation is successful, then starts the next.
    """
    if request.method == 'POST':
        # Consider for the future if we need to add operations to avoid duplicates
        """First extract metadata from JSON into variables """
        uploaded_videos = Table('uploaded_videos', metadata, autoload=True)
        con = engine.connect()
        print(request.is_json)
        uploaded_json = request.get_json()
        input_content_id = uploaded_json['input_content_id']
        video_key = uploaded_json['key']
        kid = uploaded_json['kid']
        """First file needs to be fragmented"""
        file_for_fragment = \
            con.execute(uploaded_videos.select(uploaded_videos.c.input_content_id == input_content_id)).fetchone()[1]
        print(file_for_fragment)
        fragmentation = Video_ops.video_fragment(file_for_fragment)
        """Return includes a '1' at the end if successful"""
        if (fragmentation[-1]) == 1:
            """As successful, we need to update the SQL database"""
            packaged_content_id = random.randint(0, 100)
            # Consider for the future if we need to add operations to avoid duplicates or detect already packaged files
            result = con.execute(
                uploaded_videos.update().where(uploaded_videos.c.input_content_id == input_content_id).values(
                    status='Fragmented', output_file_path=fragmentation[1], video_key=video_key, kid=kid,
                    packaged_content_id=packaged_content_id))
            """Once updated, we extract info from database and we launch the encryption """
            video_track_number = \
                con.execute(uploaded_videos.select(uploaded_videos.c.input_content_id == input_content_id)).fetchone()[
                    2]
            file_to_encrypt = \
                con.execute(uploaded_videos.select(uploaded_videos.c.input_content_id == input_content_id)).fetchone()[
                    4]
            encryptation = Video_ops.video_encrypt(video_track_number, video_key, kid, file_to_encrypt)
            """Return includes a '1' at the end if successful"""
            if (encryptation[-1]) == 1:
                """As successful, we need to update the SQL database"""
                result = con.execute(
                    uploaded_videos.update().where(uploaded_videos.c.input_content_id == input_content_id).values(
                        status='Encrypted', output_file_path=encryptation[1]))
                """Once updated, we finally transcode into MPEG-Dash """
                dash_convert = Video_ops.video_dash(encryptation[1])
                """Return includes a '1' at the end if successful"""
                if (dash_convert[-1]) == 1:
                    result = con.execute(
                        uploaded_videos.update().where(uploaded_videos.c.input_content_id == input_content_id).values(
                            status='Ready', url=dash_convert[1]))
                    return render_template("success_packaged.html", url=dash_convert[1],
                                           packaged_content_id=packaged_content_id)
                else:
                    return ("ERROR - Check command line")
            else:
                return ("ERROR - Check command line")
        else:
            return ("ERROR - Check command line")


@app.route('/packaged_content_id/<int:packaged_content_id>', methods=['GET'])
def consult_status(packaged_content_id):
    """
    This method is called for big video files, to check the status of the operations.
    As the video files' operations update the Database with the status of the file, by knowing that status
    value we can know at which stage point of the process we are
    """
    if request.method == 'GET':
        """First we generate variables by consulting the database"""
        uploaded_videos = Table('uploaded_videos', metadata, autoload=True)
        con = engine.connect()
        status = \
        con.execute(uploaded_videos.select(uploaded_videos.c.packaged_content_id == packaged_content_id)).fetchone()[3]
        url = \
        con.execute(uploaded_videos.select(uploaded_videos.c.packaged_content_id == packaged_content_id)).fetchone()[8]
        video_key = \
        con.execute(uploaded_videos.select(uploaded_videos.c.packaged_content_id == packaged_content_id)).fetchone()[5]
        kid = \
        con.execute(uploaded_videos.select(uploaded_videos.c.packaged_content_id == packaged_content_id)).fetchone()[6]
        """
        If the status is 'Ready', process should be finished.
        In our code, when it's finished it should have generated a URL value.
        If it's not ready, we'll return the current point of the operations.
        """
        if status == 'Ready':
            data_set = {"url": [url], "key": [video_key], "kid": [kid]}
            return (data_set)
        else:
            output = ("The packaged_content_id with number" + packaged_content_id + "is currently with status" + status)
            return (output)


""" Flask App main launcher """
if __name__ == '__main__':
    app.run(host='0.0.0.0')
