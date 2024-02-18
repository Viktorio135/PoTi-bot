import config

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


Base = declarative_base()
engine = create_engine(f"mysql+mysqlconnector://{config.USER}:{config.PASSWORD}@{config.HOST}/{config.DATABASE}")

class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    sex = Column(String(10))
    age = Column(Integer)
    description = Column(Text(1000))
    user_name = Column(String(100))
    user_id = Column(String(100))
    is_active = Column(Boolean)
    photos = Column(String(500))
    university = Column(String(1000), ForeignKey('university.name'))  # Изменено на 'university.id'
    speciality = Column(String(1000))
    course = Column(Integer)
    education = Column(String(100))
    is_blocked = Column(Boolean)
    registration_date = Column(DateTime(), default=datetime.now)

class University(Base):
    __tablename__ = 'university'

    id = Column(Integer, primary_key=True)
    name = Column(String(1000))  # Добавлен index


def start_db():
    Base.metadata.create_all(bind=engine, checkfirst=True)




