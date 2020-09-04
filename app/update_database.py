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


class Update_DB:
    
    def update_after_fragment(con, input_content_id, output_file_path, video_key, kid):
        packaged_content_id = random.randint(0, 100)
        result = con.execute(
            uploaded_videos.update().where(
                uploaded_videos.c.input_content_id
                == input_content_id).values(
                status='Fragmented', output_file_path=output_file_path,
                video_key=video_key, kid=kid,
                packaged_content_id=packaged_content_id))
        output_string = ("\n\n" + datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S") +
                         " - Starting video encryptation with" +
                         " the following packaged_content_id:")
        print(output_string, file=sys.stdout)
        print(packaged_content_id, file=sys.stdout)
        return packaged_content_id

    def update_after_encrypt(con, input_content_id, output_file_path):
        output_string = (
                "\n\n" +
                datetime.now().strftime("%d/%m/%Y %H:%M:%S") +
                " - Starting MPEG-DASH transcoding")
        print(output_string, file=sys.stdout)
        result = con.execute(
            uploaded_videos.update().where(
                uploaded_videos.c.input_content_id
                == input_content_id).values(
                status='Encrypted', output_file_path=output_file_path))

    def update_after_dash(con, input_content_id,
                          dash_output, packaged_content_id):
        output_string = ("\n\n" + datetime.now().strftime(
            "%d/%m/%Y %H:%M:%S") +
                         " - Everything went successful. Returning JSON")
        print(output_string, file=sys.stdout)
        result = con.execute(
            uploaded_videos.update().where(
                uploaded_videos.c.input_content_id
                == input_content_id).values(
                status='Ready', url=dash_output))
        """We return 1 for successful, url address,
            and packaged_content_id"""
        output = (1, dash_output, packaged_content_id)
        return output
