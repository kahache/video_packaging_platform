__author__ = "The One & Only Javi"
__version__ = "1.0.0"
__start_date__ = "25th July 2020"
__end_date__ = "3rd August 2020"
__maintainer__ = "me"
__email__ = "little_kh@hotmail.com"
__requirements__ = "SQL-Alchemy, MySQL, Flask-SQLAlchemy"
__status__ = "Production"
__description__ = """
This is the Database connection script.
It will generate the connections between our Flask APP and the MySQL database
"""

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from flask_sqlalchemy import *


def init_db():
    metadata.create_all(bind=engine)


"""
Uncomment this line if you are going to run in your system, outside the Docker
And then comment the one down.
localhost - makes reference to the system
db - makes reference to the virtual DB inside
"""
engine = create_engine(
    'mysql://root:root@localhost:3306/video_files', convert_unicode=True,
    echo=True)
# engine = create_engine('mysql://root:root@db:3306/video_files',
# convert_unicode=True, echo=True)
metadata = MetaData()
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
