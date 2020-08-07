# video_packaging_platform

This is a very basic API with a persistance layer that will process video files as a background task. It will receive them, encrypt them and process them into MPEG-DASH ready to be streamed.

## Getting Started

Obviously, you first need to clone this repo
```
git clone https://github.com/kahache/video_packaging_platform.git
```
And then, you can launch the main App 
```
cd app
python3 app.py
```
It will start running the system on http://0.0.0.0:5000 on your system. 

Once you open that link on your browser, you'll find a small index that will detail you the 3 options you can launch
### Prerequisites

You'll need some software installed in your system:
```
Python 3.6 or higher
MySQL Server
pip3 install -r app/requirements.txt
```

### How does it work

* WORK IN PROGRESS *

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

![](images/VideoOperationsLogic.png)

## Running the tests

To run the tests, get with Linux/UNIX terminal into the /tests/ forlder and run:
```
bash run_tests.sh
```
There you'll find a dialog box where you can choose the different tests to run. It's highly recommended to first download the test videos otherwise it can give errors. Feel free to check out the code and change variables or situations you'd like to test.
## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Python](https://www.python.org/downloads/release/python-360/) - Most programming language used
* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - Framework used to generate the API
* [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/) - Library used as ORM
* [MySQL](https://www.mysql.com) - Relational database system used
* [Bento4](https://www.bento4.com) - MP4 & Dash library

## Authors

* **Javier Brines Garcia** - *Initial work* - [LinkedIn](https://www.linkedin.com/in/javi-brines-cto)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Guillem C.
* Roc a.k.a. Roc Rocks, for the Docker comments
* Ben, for the tips with the player
