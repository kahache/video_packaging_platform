__author__ = "The One & Only Javi"
__version__ = "1.0.0"
__start_date__ = "25th July 2020"
__end_date__ = "5th August 2020"
__maintainer__ = "me"
__email__ = "little_kh@hotmail.com"
__requirements__ = "SQL-Alchemy, MySQL," \
                   " Flask-SQLAlchemy, database.py, " \
                   "models.py, video_ops.py"
__status__ = "Production"
__description__ = """
This is the main background operations script.
It is meant to be used with app.py, which should call the methods
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
from datetime import datetime
from update_database import Update_DB

# We declare variables
storage_dir = os.getcwd() + "/../storage/"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = storage_dir

# We define the table we're going to use
uploaded_videos = Table('uploaded_videos', metadata, autoload=True)


class Main_ops:

    def success():
        """First, move file into storage and generate outputs"""
        output_string = ("\n\n" +
                         datetime.now().strftime("%d/%m/%Y %H:%M:%S") +
                         " - File received")
        print(output_string, file=sys.stdout)
        app.config['UPLOAD_FOLDER'] = storage_dir
        f = request.files['file']
        f.save(f.filename)
        path = (os.getcwd() + "/" + f.filename)
        input_content_origin = (storage_dir + f.filename)
        """We call the video_ingest method to extract
        metadata and store the video"""
        result = Video_ops.video_ingest(path)
        """Return includes a '1' at the end if successful"""
        if (result[-1]) == 1:
            """As successful, we need to update the SQL database"""
            output_string = ("\n\n" + datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S") +
                             " - File analyzed, storing values into DB")
            print(output_string, file=sys.stdout)
            uploaded_videos = Table('uploaded_videos', metadata, autoload=True)
            con = engine.connect()
            con.execute(uploaded_videos.insert(),
                        input_content_origin=input_content_origin,
                        status="Ingested",
                        video_track_number=result[1])
            input_content_id = \
                con.execute(
                    uploaded_videos.select(
                        uploaded_videos.c.input_content_origin
                        == input_content_origin)
                ).fetchone()[0]
            output_string = ("\n\n" + datetime.now().strftime(
                "%d/%m/%Y %H:%M:%S") + " - Redirecting to output website with "
                                       "the result")
            print(output_string, file=sys.stdout)
            output = (1, f.filename, input_content_id)
            return output
        else:
            print(result)
            return "ERROR - Check command line"

    def package():
        """When called with JSON, it will generate background
        operations with video files inside internal storage
        It works with nested operations, if one operation is
        successful, then starts the next.
        """
        # Consider for the future if we need to add
        # operations to avoid duplicates
        """First extract metadata from JSON into variables """
        output_string = ("\n\n" +
                         datetime.now().strftime("%d/%m/%Y %H:%M:%S") +
                         " - Starting to package")
        print(output_string, file=sys.stdout)
        uploaded_videos = Table('uploaded_videos', metadata, autoload=True)
        con = engine.connect()
        print(request.is_json)
        uploaded_json = request.get_json()
        input_content_id = uploaded_json['input_content_id']
        video_key = uploaded_json['key']
        kid = uploaded_json['kid']
        """First file needs to be fragmented"""
        file_for_fragment = \
            con.execute(uploaded_videos.select(
                uploaded_videos.c.input_content_id
                == input_content_id)).fetchone()[1]
        print(file_for_fragment)
        output_string = ("\n\n" +
                         datetime.now().strftime("%d/%m/%Y %H:%M:%S") +
                         " - Starting video fragmentation")
        print(output_string, file=sys.stdout)
        fragmentation = Video_ops.video_fragment(file_for_fragment)
        """Return includes a '1' at the end if successful"""
        if (fragmentation[-1]) == 1:
            """As successful, we need to update the SQL database"""
            packaged_content_id = Update_DB.update_after_fragment(
                con, input_content_id, fragmentation[1], video_key, kid)
            """Once updated, we extract info from
            database and we launch the encryption """
            video_track_number = \
                con.execute(uploaded_videos.select(
                    uploaded_videos.c.input_content_id
                    == input_content_id)).fetchone()[2]
            file_to_encrypt = \
                con.execute(uploaded_videos.select(
                    uploaded_videos.c.input_content_id
                    == input_content_id)).fetchone()[4]
            encryptation = Video_ops.video_encrypt(
                video_track_number, video_key, kid, file_to_encrypt)
            """Return includes a '1' at the end if successful"""
            if (encryptation[-1]) == 1:
                """As successful, we need to update the SQL database"""
                Update_DB.update_after_encrypt(
                    con, input_content_id, encryptation[1])
                """Once updated, we finally transcode into MPEG-Dash """
                dash_convert = Video_ops.video_dash(encryptation[1])
                if (dash_convert[-1]) == 1:
                    return Update_DB.update_after_dash(
                        con, input_content_id, dash_convert[2],
                        packaged_content_id)
                else:
                    return ("ERROR - Check command line")
            else:
                return ("ERROR - Check command line")
        else:
            return ("ERROR - Check command line")

    def consult_status(packaged_content_id):
        """
        This method is called for big video files,
        to check the status of the operations.
        As the video files' operations update the Database
        with the status of the file, by knowing that status
        value we can know at which stage point of the
        process we are
        """
        """First we generate variables by consulting the database"""
        uploaded_videos = Table('uploaded_videos', metadata, autoload=True)
        con = engine.connect()
        status = \
            con.execute(uploaded_videos.select(
                uploaded_videos.c.packaged_content_id
                == packaged_content_id)).fetchone()[3]
        url = \
            con.execute(uploaded_videos.select(
                uploaded_videos.c.packaged_content_id
                == packaged_content_id)).fetchone()[8]
        video_key = \
            con.execute(uploaded_videos.select(
                uploaded_videos.c.packaged_content_id
                == packaged_content_id)).fetchone()[5]
        kid = \
            con.execute(uploaded_videos.select(
                uploaded_videos.c.packaged_content_id
                == packaged_content_id)).fetchone()[6]
        """
        If the status is 'Ready', process should be finished.
        In our code, when it's finished it should have generated a URL value.
        If it's not ready, we'll return the current point of the operations.
        """
        if status == 'Ready':
            data_set = {"url": [url], "key": [video_key], "kid": [kid]}
            return (data_set)
        else:
            output = ("The packaged_content_id with number" +
                      packaged_content_id + "is currently with status" +
                      status)
            return (output)
