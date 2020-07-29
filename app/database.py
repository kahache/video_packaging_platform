import mysql.connector

class Database:

    def __init__(db_name,table_name):
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(db_name))
        cursor.execute("CREATE TABLE IF NOT EXISTS {}".format(table_name)+
        " (input_content_origin VARCHAR(255),input_content_id INT PRIMARY KEY AUTO_INCREMENT,video_track_number INT,status VARCHAR(20),output_file_path VARCHAR(255),video_key TEXT,kid TEXT,packaged_content_id INT UNIQUE,url VARCHAR(255))")
        connection.close()

    def insert_all(table_name,row_names,test_row):
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO {}".format(table_name)+" ("+(', '.
        join(row_names))+") VALUES ("+str(test_row)[1:-1]+")")
        connection.commit()
        connection.close()

    def insert_one_row(table_name,row_name,value):
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute("INSERT INTO {}".format(table_name)+" ("+row_name+
        ") VALUES ('{}'".format(value)+")")
        connection.commit()
        connection.close()

    def view_all(table,config):
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM {}".format(table))
        results=cursor.fetchall()
        connection.close()
        return results


    def view_one_row(row,table_name,input_content_id):
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute("SELECT {}".format(row)+
        " FROM {}".format(table)+" WHERE input_content_id = {}"
        .format(input_content_id))
        row=cursor.fetchone()[0]
        connection.close()
        return row

    def delete_row(table_name,input_content_id):
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        #https://youtu.be/jsuerKRsEyA
        cursor.execute("DELETE FROM {}".format(table_name)+
        " WHERE input_content_id = {}".format(input_content_id))
        connection.commit()
        connection.close()

    def update(table_name,column_name,value,input_content_id):
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        cursor.execute("UPDATE "+table_name+" SET "+column_name+" = \""+value+
        "\" WHERE input_content_id = "+input_content_id)
        connection.commit()
        connection.close()

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
#row_names = [ "input_content_origin", "video_track_number","status",
#"output_file_path","video_key","kid","packaged_content_id","url"]
#test_row = ["BBB.mp4", "2","Fragmented","/98UXG/stream.mpd",
#"hyN9IKGfWKdAwFaE5pm0qg","oW5AK5BW43HzbTSKpiu3SQ","77",
#"http://0.0.0.0:5000/98UXG/stream.mpd"]
#Database.insert_all(table_name,row_names,test_row)
#print(','.join(row_names))
#Testing purposes
#Database.insert_new("SupuTamadre.mp4",2,"Follao","ruta/salida.mpd","doojsdfb","obsuadboasbd","None","http://alamierda.com")
#file="Suputamadre5.mp4"
#column_name="status"
#row_name="input_content_origin"
#value="Fragmented"
#input_content_id=4
#Database.insert_one_row(table_name,row_name,file)
#Database.delete_row(table_name,input_content_id)
#print(Database.view_all("movie_files",config))
#Database.update(table_name,column_name,value,str(input_content_id))
