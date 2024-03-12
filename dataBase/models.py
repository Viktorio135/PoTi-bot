import os

from dotenv import load_dotenv

from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Boolean, 
    Text, 
    ForeignKey,
    DateTime
)

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from datetime import datetime



load_dotenv()

user_bd = os.getenv('USER_BD')
password = os.getenv('PASSWORD')
host = os.getenv('HOST')
database = os.getenv('DATABASE')

Base = declarative_base()
engine = create_engine(f"mysql+mysqlconnector://{user_bd}:{password}@{host}/{database}")

class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    sex = Column(String(10))
    search_to = Column(String(10))
    age = Column(Integer)
    description = Column(Text(2000))
    user_name = Column(String(100))
    user_id = Column(String(100))
    is_active = Column(Boolean)
    photos = Column(String(500))
    university = Column(Integer, ForeignKey('university.id'))
    speciality = Column(String(1000))
    course = Column(Integer)
    education = Column(String(100))
    is_blocked = Column(Boolean)
    registration_date = Column(DateTime(), default=datetime.now)
    to_education = Column(String(100), default='all')
    to_university = Column(Integer, ForeignKey('university.id'), default=3)
    to_course = Column(Integer, default=0)
    max_age = Column(Integer, default=0)
    min_age = Column(Integer, default=0)


class University(Base):
    __tablename__ = 'university'

    id = Column(Integer, primary_key=True)
    name = Column(String(500))

class Admins(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(50))


def start_db():
    Base.metadata.create_all(bind=engine, checkfirst=True)




