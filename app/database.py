from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import *


def init_db():
    metadata.create_all(bind=engine)


engine = create_engine('mysql://root:root@localhost:3306/video_files', convert_unicode=True, echo=True)
metadata = MetaData()
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))


def insert(row_name, value1):
    uploaded_videos = Table(uploaded_videos, metadata, autoload=True)
    con = engine.connect()
    con.execute(uploaded_videos.insert(), row_name=value1)


# def view_db():


# def update_db():
#   result = con.execute(uploaded_videos.update().where(uploaded_videos.c.input_content_id == 3).values(
#      input_content_origin='prueba/archivoOJETE.mp4'))
# print(result)

# We define the table we're going to use
db_name = "video_files"
table_name = "updated_files"
