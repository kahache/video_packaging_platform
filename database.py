import sqlite3

class Database:

    def __init__():
        conn=sqlite3.connect("movies.db")
        cur=conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS movie_files (input_content TEXT, input_content_id INTEGER PRIMARY KEY AUTOINCREMENT, file_path TEXT, video_track_number INTEGER, status TEXT, key TEXT, kid TEXT, packaged_content_id TEXT, url TEXT)")
        conn.commit()
        conn.close


    def insert(input_content,input_content_id,file_path,video_track_number,
    status,key,kid,packaged_content_id,url):
        conn=sqlite3.connect("movies.db")
        cur=conn.cursor()
        cur.execute("INSERT INTO movie_files VALUES (?,?,?,?,?,?,?,?,?)",
        (input_content,input_content_id,file_path,video_track_number,status,key,
        kid,packaged_content_id,url))
        conn.commit()
        conn.close

    def view():
        conn=sqlite3.connect("movies.db")
        cur=conn.cursor()
        cur.execute("SELECT * FROM movie_files")
        rows=cur.fetchall()
        conn.close()
        return rows

    def delete(input_content):
        conn=sqlite3.connect("movies.db")
        cur=conn.cursor()
        cur.execute("DELETE FROM movie_files WHERE input_content=?",
        (input_content,))
        conn.commit()
        conn.close()

    def update(column,value,input_content_id):
        conn=sqlite3.connect("movies.db")
        cur=conn.cursor()
        cur.execute("UPDATE movie_files SET "+column+" = \""+value+
         "\" WHERE input_content_id = "+input_content_id)
        conn.commit()
        conn.close()

    def update_prueba(column,value,input_content_id):
        conn=sqlite3.connect("movies.db")
        cur=conn.cursor()
        #string_query=("UPDATE movie_files SET "+tipo+" = \""+valor+ "\" WHERE input_content_id = "+input_content_id)
        #cur.execute("UPDATE movie_files SET %s = %s WHERE input_content_id = %d",(tipo,valor),input_content_id)
        print(string_query)
        cur.execute("UPDATE movie_files SET "+column+" = \""+value+
         "\" WHERE input_content_id = "+input_content_id)
        #cur.execute("SELECT %s FROM Data where %s=?" % (column, goal), (constrain,))
        #cur.execute("SELECT "+column+" FROM Data where "+goal+"=?", (constrain,))
        conn.commit()
        conn.close()

#print(view())
#create_table()
#insert("archivo_1",2,"/archivo/dondesencuentra","NULL","NULL","NULL","NULL")
#connect()
#Database.__init__()
#print(Database.view())
