# video_packaging_platform

This is a very basic API with a persistance layer that will process video files as a background task. It will receive them, encrypt them and process them into MPEG-DASH ready to be streamed.

## Getting Started

Obviously, you first need to clone this repo
```
git clone https://github.com/kahache/video_packaging_platform.git
```
And then, you can launch the main App 
```
cd video_packaging_platform
docker-compose up
```
It will start running the system on http://0.0.0.0:5000 on your system. 

Once you open that link on your browser, you'll find a small index that will detail you the 4 options you can launch. 

In case you'd like to open locally, please notice you should have the Bento 4 SDK for your current OS and even replace the files at /bin/ and /utils just in case. Once done, just run python3 app/app.py

### Prerequisites

You'll need some software installed in your system:
```
Python 3.6 or higher
MySQL Server
Docker
(in case you run local outside Docker, pip3 install -r app/requirements.txt)
```

### How does it work

* WORK IN PROGRESS *

This platform opens up a simple web file loader. You can insert files and they will be processed. 
Once you have the files packaged, you can open the files with VLC Media Player or FFPlay. You should be able to hear the audio but you shouldn't be able to see the video.

* The Video logic

For this exercise, first of all we have considerated about the encryption. The point is that the industry recommends to encrypt all the tracks contained in the MP4 file.

However, as in the example given we are only going to have 1 Key and 1 KID, I have decided to encrypt only the video track. Why?

First reason is to be able to track all the video process. When it's success, we can open the file and hear the ideo but receive glitches/bad image as video input. I suspect this is the same way BeIn Sports is encrypted in Spain with Movistar Imagenio: even you know the UDP address and try to record it with FFMpeg (theorically they aren't encrypted), you're able to record a video file with a lot of glitches but with clear sound.

This will also be a way to ensure nobody has done this exercise as this before :-)

So the first point will be to receive a file and determine wether it can be processed or not, and extract metadata from the container like this

![](images/video_ops_ingest.png)

As we can see, only files able to be processed will continue the operation.

For the rest of the process, we are going to work in a chain with the required steps to have an MPEG-DASH output.

That means, if one step fails, we can't continue the process. This will be the logic contained inside the main class in video_ops.py

![](images/VideoOperationsLogic.png)

All this is processed in **app/video_ops.py**, which will cal to /bin/ and /utils/ when needed

* The Database

After consider the simplicity of the exercise, I've decided to go only with one table only. This is because the API will only do a few stuff. For further professional environments, we should consider to have several tables and add more data into the tables, such as datetimes (creation, processing, etc), users, etc.

I've considered only 9 rows for this exercise:
```
+----------------------+--------------+------+-----+---------+----------------+
| Field                | Type         | Null | Key | Default | Extra          |
+----------------------+--------------+------+-----+---------+----------------+
| input_content_id     | int(11)      | NO   | PRI | NULL    | auto_increment |
| input_content_origin | varchar(255) | YES  |     | NULL    |                |
| video_track_number   | int(11)      | YES  |     | NULL    |                |
| status               | varchar(255) | YES  |     | NULL    |                |
| output_file_path     | varchar(255) | YES  |     | NULL    |                |
| video_key            | varchar(255) | YES  |     | NULL    |                |
| kid                  | varchar(255) | YES  |     | NULL    |                |
| packaged_content_id  | int(11)      | YES  | UNI | NULL    |                |
| url                  | varchar(255) | YES  |     | NULL    |                |
+----------------------+--------------+------+-----+---------+----------------+
9 rows in set (0,00 sec)
```
**_input_content_id:_** : the ID generated for each file that is ingested in the platform.  

**_input_content_origin_** : The path of the original file. This will be used to check if we have already uploaded a file with that name or not. 

**_video_track_number_** : Video track number ID from metadata extracted with Bento4 utils, notice for other softwares as FFMpeg should be different wether they count zero as first or not)

**_status_** : This is very important. This will be a text cell that will explain the last operation done with that video file.
    It can be:
    
    "Ingested" - file moved to storage and video track number saved
    "Fragmented" - file has been fragmentated
    "Encrypted" - file's video track has been encrypted with the KEY and KID values given in the JSON
    "Ready" - file has been converted into MPEG-DASH and has a URL output

**_output_file_path_** : This will be the path of the last processed file. For each video process, we generate a new file. For this exercise we aren't deleting the non-usable files, so we can track the results. Notice that for further production environments, this should be erased with some cronjob 

**_video_key_** : video KEY for AES CBCS encryption given by user

**_kid_** : video KID for AES CBCS encryption given by user 

**_packaged_content_id_** : ID for a file that is in the process of being packaged. This is a random number generated by our main App.

**_url_** : Last cell, only filled if a video has been packaged and contains its output link. For this exercise it will be inside the filepath inside the server.       

For the docker, the database is declared in **/db/db.init.sql** 

* The operations logic, mixing Video and Database 

* The Flask API

This simply redirects the endpoints of the API with the templates and the operations. It's the main file, which gets executed automatically and starts the service at http://0.0.0.0:5000


## Running the tests

To run the tests, get with Linux/UNIX terminal into the /tests/ forlder and run:
```
bash run_tests.sh
```
There you'll find a dialog box where you can choose the different tests to run. It's highly recommended to first download the test videos otherwise it can give errors. Feel free to check out the code and change variables or situations you'd like to test.

## Files included in this package

```
.
└── video_packaging_platform
    ├── Dockerfile
    ├── README.md
    ├── app
    │   ├── app.py
    │   ├── database.py
    │   ├── main_ops.py
    │   ├── models.py
    │   ├── requirements.txt
    │   ├── templates
    │   │   ├── file_upload_form.html
    │   │   ├── success.html
    │   │   └── success_packaged.html
    │   └── video_ops.py
    ├── bin
    │   ├── mp4-dash.py
    │   ├── mp4dash
    │   ├── mp4decrypt
    │   ├── mp4dump
    │   ├── mp4encrypt
    │   ├── mp4fragment
    │   ├── mp4info
    │   └── mp4split
    ├── db
    │   └── init.sql
    ├── docker-compose.yml
    ├── images
    │   ├── Video\ Operations\ logic.jpg
    │   ├── VideoOperationsLogic.png
    │   ├── video_ops_ingest.jpg
    │   └── video_ops_ingest.png
    ├── tests
    │   ├── TEST_VIDEOS
    │   │   ├── download_videos.sh
    │   │   └── public_test_video_list.txt
    │   ├── __init__.py
    │   ├── run_tests.sh
    │   ├── test_app.py
    │   ├── test_database.py
    │   ├── test_models.py
    │   └── test_video_ops.py
    └── utils
        ├── aes.py
        ├── check-indexes.py
        ├── mp4-dash-clone.py
        ├── mp4-dash-encode.py
        ├── mp4-dash.py
        ├── mp4-hls.py
        ├── mp4utils.py
        ├── pr-derive-key.py
        ├── skm.py
        ├── subtitles.py
        └── wv-request.py
```

## Built With

* [Python](https://www.python.org/downloads/release/python-360/) - Most programming language used
* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - Framework used to generate the API
* [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) - Library used as ORM
* [MySQL](https://www.mysql.com) - Relational database system used
* [Bento4](https://www.bento4.com) - MP4 & Dash library
* [Docker](https://www.docker.com) - PaaS that uses OS-level virtualization to deliver software in packages called containers

## Authors

* **Javier Brines Garcia** - *Initial work* - [LinkedIn](https://www.linkedin.com/in/javi-brines-cto)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Guillem C. & David V.
* Roc a.k.a. Roc Rocks, for the Docker comments
* Ben M., for the tips with the player
