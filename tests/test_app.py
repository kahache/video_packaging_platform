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
from test_database import *
# from test_video_ops import *
from test_models import *
import os
import subprocess
import sys
import requests
# from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy import *
from sqlalchemy.sql import *
import random
import unittest
from sqlalchemy import create_engine, MetaData, Table

class test_functions(unittest.TestCase):
    def setUp(self):
        # We declare variables
        self.storage_dir = os.getcwd() + "/../storage/"
        self.app = Flask(__name__)
        self.app.config['UPLOAD_FOLDER'] = self.storage_dir
        self.input_file1 = os.getcwd() + "/TEST_VIDEOS/BigBuckBunny.mp4"
        self.filename = "BigBuckBunny.mp4"
        self.bin_dir = os.getcwd() + "/../bin"
        self.json = {"input_content_id": "1", "key": "hyN9IKGfWKdAwFaE5pm0qg", "kid": "oW5AK5BW43HzbTSKpiu3SQ"}
        # We define the table we're going to use
        self.test_uploaded_videos = Table('test_uploaded_videos', metadata, autoload=True)
        self.input_content_id = 1
        self.engine = create_engine('mysql://root:root@localhost:3306/test_video_files', convert_unicode=True,
                                    echo=True)
        self.status = "Fragmented"
        self.metadata = MetaData()
        self.db_session = scoped_session(sessionmaker(autocommit=False,
                                                      autoflush=False,
                                                      bind=engine))

    def test_success(self):
        metadata.create_all(bind=engine)
        path = (os.getcwd() + "/" + self.filename)
        input_content_origin = (self.storage_dir + self.filename)
        """Here we call the video_function in the main script; for test we give a basic result"""
        result = ("OK - File " + self.input_file1 +
                  " has been processed and moved to storage", 2, 1)
        """Return includes a '1' at the end if successful"""
        if (result[-1]) == 1:
            test_uploaded_videos = Table('test_uploaded_videos', metadata, autoload=True)
            con = engine.connect()
            con.execute(test_uploaded_videos.insert(), input_content_origin=input_content_origin, status="Ingested",
                        video_track_number=result[1])
            input_content_id = \
                con.execute(test_uploaded_videos.select(
                            test_uploaded_videos.c.input_content_origin == input_content_origin)).fetchone()[0]
            input_content_id_query = subprocess.check_output(
                "mysql -u root -proot -D test_video_files -s -N -e \"SELECT input_content_id FROM test_uploaded_videos WHERE input_content_origin = \'{}\'".format(
                    input_content_origin) + " LIMIT 1\"", shell=True)
            # TEST 1: We are going to ensure the data has been posted into the test Database
            self.assertEqual(str(input_content_id), input_content_id_query.decode('ascii').strip())

    def test_package(self):
        # Consider for the future if we need to add operations to avoid duplicates
        packaged_content_id = 1
        test_uploaded_videos = Table('test_uploaded_videos', metadata, autoload=True)
        con = engine.connect()
        uploaded_json = self.json
        input_content_id = uploaded_json['input_content_id']
        video_key = uploaded_json['key']
        kid = uploaded_json['kid']
        """First file needs to be fragmented"""
        file_for_fragment = \
            con.execute(
                test_uploaded_videos.select(test_uploaded_videos.c.input_content_id == input_content_id)).fetchone()[1]
        file_for_fragment_query = subprocess.check_output(
            "mysql -u root -proot -D test_video_files -s -N -e \"SELECT input_content_origin FROM test_uploaded_videos WHERE input_content_id = \'{}\'".format(
                input_content_id) + " LIMIT 1\"", shell=True)
        # TEST 1: We are going to ensure the data has been posted into the test Database
        self.assertEqual(str(file_for_fragment), file_for_fragment_query.decode('ascii').strip())
        fragmentation = ("OK - File " + self.input_file1 +
                      " has been fragmented and is ready to encrypt",
                      self.input_file1, 1)
        """Return includes a '1' at the end if successful"""
        if (fragmentation[-1]) == 1:
            """As successful, we need to update the SQL database"""
            result = con.execute(
                test_uploaded_videos.update().where(test_uploaded_videos.c.input_content_id == input_content_id).values(
                    status='Fragmented', output_file_path=fragmentation[1], video_key=video_key, kid=kid,
                    packaged_content_id=packaged_content_id))
           # Now we launch individual queries directly to Database to ensure the writting in DB has been competed successfully
            status_query = subprocess.check_output(
            "mysql -u root -proot -D test_video_files -s -N -e \"SELECT status FROM test_uploaded_videos WHERE input_content_id = \'{}\'\"".format(
                input_content_id), shell=True)
            output_file_path_query = subprocess.check_output(
                "mysql -u root -proot -D test_video_files -s -N -e \"SELECT output_file_path FROM test_uploaded_videos WHERE input_content_id = \'{}\'\"".format(
                    input_content_id), shell=True)
            video_key_query = subprocess.check_output(
                "mysql -u root -proot -D test_video_files -s -N -e \"SELECT video_key FROM test_uploaded_videos WHERE input_content_id = \'{}\'\"".format(
                    input_content_id), shell=True)
            kid_query = subprocess.check_output(
                "mysql -u root -proot -D test_video_files -s -N -e \"SELECT kid FROM test_uploaded_videos WHERE input_content_id = \'{}\'\"".format(
                    input_content_id), shell=True)
            # TEST - confirm values in DB are the ones we expected
            output_file_path = fragmentation[1]
            self.assertEqual(self.status, status_query.decode('ascii').strip())
            self.assertEqual(output_file_path, output_file_path_query.decode('ascii').strip())
            self.assertEqual(video_key, video_key_query.decode('ascii').strip())
            self.assertEqual(kid, kid_query.decode('ascii').strip())
            """Once updated, we extract info from database and we launch the encryption """
            video_track_number = \
                con.execute(test_uploaded_videos.select(
                                            test_uploaded_videos.c.input_content_id == input_content_id)).fetchone()[2]
            video_track_number_query = subprocess.check_output(
                "mysql -u root -proot -D test_video_files -s -N -e \"SELECT video_track_number FROM test_uploaded_videos WHERE input_content_id = \'{}\'".format(
                    input_content_id) + " LIMIT 1\"", shell=True)
            # TEST - confirm values in DB are the ones we expected
            self.assertEqual(str(video_track_number), video_track_number_query.decode('ascii').strip())
            file_to_encrypt = \
                con.execute(test_uploaded_videos.select(test_uploaded_videos.c.input_content_id == input_content_id)).fetchone()[
                    4]
            self.assertEqual(output_file_path, file_to_encrypt)
            output_file_path2=(str(output_file_path)+"_encrypted")
            encryptation = ("\nOK - File" + self.input_file1 + " has been encrypted with key:" + video_key + "kid:" + \
                           kid, output_file_path2, 1)
            """Return includes a '1' at the end if successful"""
            if (encryptation[-1]) == 1:
                """As successful, we need to update the SQL database"""
                result = con.execute(
                    test_uploaded_videos.update().where(test_uploaded_videos.c.input_content_id == input_content_id).values(
                        status='Encrypted', output_file_path=encryptation[1]))
                status_query = subprocess.check_output(
                    "mysql -u root -proot -D test_video_files -s -N -e \"SELECT status FROM test_uploaded_videos WHERE input_content_id = \'{}\'\"".format(
                        input_content_id), shell=True)
                self.assertEqual("Encrypted", status_query.decode('ascii').strip())
                """Once updated, we finally transcode into MPEG-Dash """
                dash_output=(output_file_path2 + "/dash/stream.mpd")
                dash_convert = ("OK - File" + output_file_path2 + " has been processed into " +
                      dash_output, dash_output, 1)
                """Return includes a '1' at the end if successful"""
                if (dash_convert[-1]) == 1:
                    result = con.execute(test_uploaded_videos.update().where(test_uploaded_videos.c.input_content_id == input_content_id).values(status='Ready', url=dash_convert[1]))
                    url_query = subprocess.check_output(
                        "mysql -u root -proot -D test_video_files -s -N -e \"SELECT url FROM test_uploaded_videos WHERE input_content_id = \'{}\'\"".format(
                            input_content_id), shell=True)
                    url=dash_convert[1]
                    self.assertEqual(url, url_query.decode('ascii').strip())
                    status_query = subprocess.check_output(
                        "mysql -u root -proot -D test_video_files -s -N -e \"SELECT status FROM test_uploaded_videos WHERE input_content_id = \'{}\'\"".format(
                            input_content_id), shell=True)
                    self.assertEqual("Ready", status_query.decode('ascii').strip())
                else:
                     return ("ERROR - Check command line")
            else:
                 return ("ERROR - Check command line")
        else:
             return ("ERROR - Check command line")

    def test_consult_status(self):
        packaged_content_id = 1
        test_uploaded_videos = Table('test_uploaded_videos', metadata, autoload=True)
        con = engine.connect()
        status = \
        con.execute(test_uploaded_videos.select(test_uploaded_videos.c.packaged_content_id == packaged_content_id)).fetchone()[3]
        url = \
        con.execute(test_uploaded_videos.select(test_uploaded_videos.c.packaged_content_id == packaged_content_id)).fetchone()[8]
        video_key = \
        con.execute(test_uploaded_videos.select(test_uploaded_videos.c.packaged_content_id == packaged_content_id)).fetchone()[5]
        kid = \
        con.execute(test_uploaded_videos.select(test_uploaded_videos.c.packaged_content_id == packaged_content_id)).fetchone()[6]
        status_query = subprocess.check_output(
                 "mysql -u root -proot -D test_video_files -s -N -e \"SELECT status FROM test_uploaded_videos WHERE input_content_id = \'{}\'\"".format(
                     self.input_content_id), shell=True)
        url_query = subprocess.check_output(
                 "mysql -u root -proot -D test_video_files -s -N -e \"SELECT url FROM test_uploaded_videos WHERE input_content_id = \'{}\'\"".format(
                     self.input_content_id), shell=True)
        video_key_query = subprocess.check_output(
                 "mysql -u root -proot -D test_video_files -s -N -e \"SELECT video_key FROM test_uploaded_videos WHERE input_content_id = \'{}\'\"".format(
                     self.input_content_id), shell=True)
        kid_query = subprocess.check_output(
                 "mysql -u root -proot -D test_video_files -s -N -e \"SELECT kid FROM test_uploaded_videos WHERE input_content_id = \'{}\'\"".format(
                     self.input_content_id), shell=True)
        self.assertEqual(status, status_query.decode('ascii').strip())
        self.assertEqual(url, url_query.decode('ascii').strip())
        self.assertEqual(video_key, video_key_query.decode('ascii').strip())
        self.assertEqual(kid, kid_query.decode('ascii').strip())
        if status == 'Ready':
            data_set = {"url": [url], "key": [video_key], "kid": [kid]}
            data_set_from_queries = {"url": [url_query.decode('ascii').strip()], "key": [video_key_query.decode('ascii').strip()], "kid": [kid_query.decode('ascii').strip()]}
            self.assertEqual(data_set, data_set_from_queries)
        else:
            output = ("The packaged_content_id with number" + packaged_content_id + "is currently with status" + status)
            return (output)

    def test_index(self):
        swagger_url = "https://app.swaggerhub.com/apis-docs/kahache/VideoPackagingPlatform/1.0.0"
        ping_command = ("curl -I \"{}\"".format(swagger_url) + " 2>&1 | awk '/HTTP\// {print $2}'")
        check_alive = subprocess.check_output(ping_command, shell=True)
        self.assertEqual("200", check_alive.decode('ascii').strip())

if __name__ == '__main__':
    unittest.main()
