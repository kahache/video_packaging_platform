__author__ = "The One & Only Javi"
__version__ = "1.0.0"
__start_date__ = "25th July 2020"
__end_date__ = "5th August 2020"
__maintainer__ = "me"
__email__ = "little_kh@hotmail.com"
__requirements__ = "SQL-Alchemy, MySQL, Flask-SQLAlchemy, database.py, models.py, video_ops.py, main_ops.py"
__status__ = "Production"
__description__ = """
This is the main Flask-App for the project. It will start running at
http://0.0.0.0:5000
This App is an API that lets the user process video files and prepare them into
encrypted MPEG-DASH ready to stream.
"""

import mysql.connector
import json
import os
import subprocess
import sys
import requests
import random
from flask import *
from database import *
from video_ops import *
from models import *
from main_ops import *
from sqlalchemy import *
from sqlalchemy.sql import *
from typing import List, Dict

# We declare variables
storage_dir = os.getcwd() + "/../storage/"
upload_dir = os.getcwd() + "/../output/"
working_dir = os.getcwd()
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
def file_received():
    """File processing when video received"""
    file_operation = Main_ops.success()
    if file_operation[0] == 1:
        return render_template("success.html", name=file_operation[1], input_content_id=file_operation[2])
    else:
        return ("ERROR - Check command line")


@app.route('/packaged_content', methods=['POST'])
def background_package():
    """When called with JSON, it will generate background operations with video files inside internal storage
    It works with nested operations, if one operation is successful, then starts the next.
    """
    file_packaging = Main_ops.package()
    if file_packaging[0] == 1:
        data_set = {"packaged_content_id": [file_packaging[2]], "url": [file_packaging[1]]}
        return (data_set)
    else:
        return ("ERROR - Check command line")


@app.route('/packaged_content_id/<int:packaged_content_id>', methods=['GET'])
def consult_status(packaged_content_id):
    """
    This method is called for big video files, to check the status of the operations.
    As the video files' operations update the Database with the status of the file, by knowing that status
    value we can know at which stage point of the process we are
    """
    status_consult = Main_ops.consult_status(packaged_content_id)
    return status_consult

@app.route('/videos/')
def get_videos():
    """
    This method is to start serving files in the same server. It's just a quick way to access
    Needs to be called to start running
    Files will appear later on http://0.0.0.0:8080/
    """
    os.chdir(upload_dir)
    p = subprocess.run(['python3 -m http.server 8080'], shell=True)
    os.chdir(working_dir)


""" Flask App main launcher """
if __name__ == '__main__':
    app.run(host='0.0.0.0')
