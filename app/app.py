from typing import List, Dict
from flask import *
import mysql.connector
import json
from database import *
from video_ops import *
import os
import subprocess
import sys

#We declare variables
storage_dir=os.getcwd()+"/../storage/"
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = storage_dir


#def movie_files() -> List[Dict]:
#    config = {
#        'user': 'root',
#        'password': 'root',
#        'host': 'db',
#        'port': '3306',
#        'database': 'video_files'
#    }
#    connection = mysql.connector.connect(**config)
#    cursor = connection.cursor()
#    cursor.execute('SELECT * FROM movie_files')
#    results=cursor.fetchall()
#    cursor.close()
#    connection.close()
#    return results

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
#def index() -> str:
#    return json.dumps({'movie_files': movie_files()})
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
            print("HA FUNCIONADO")
            Database.insert_one_row(table_name,"input_content_origin",f.filename)
            input_content_id=(Database.view_one_value("input_content_id",table_name,"input_content_origin",f.filename))
            print(input_content_id)
            Database.update(table_name,"status","Ingested",str(input_content_id))
        else:
            print(result)
        return render_template("success.html", name = f.filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
