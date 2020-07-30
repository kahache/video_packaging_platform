from typing import List, Dict
from flask import Flask
import mysql.connector
import json
from database import *
from video_ops import *

app = Flask(__name__)


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

if __name__ == '__main__':
    app.run(host='0.0.0.0')
