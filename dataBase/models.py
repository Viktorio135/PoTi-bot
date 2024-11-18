import os
from dotenv import load_dotenv
from sqlalchemy import (
    Column, 
    Integer, 
    String, 
    Boolean, 
    Text, 
    ForeignKey,
    DateTime,
    create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# Загрузка переменных окружения
load_dotenv()

user_bd = os.getenv('USER_BD')
password = os.getenv('PASSWORD')
host = os.getenv('HOST')
database = os.getenv('DATABASE')

# Базовый класс для декларативного стиля
Base = declarative_base()

# Создание движка для подключения к базе данных
engine = create_engine(f"mysql+mysqlconnector://{user_bd}:{password}@{host}/{database}")

# Определение класса User для таблицы Users
class User(Base):
    __tablename__ = 'Users'

    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    game_id = Column(String(100))
    description = Column(Text(2000))
    role1 = Column(String(50))
    role2 = Column(String(50))
    role3 = Column(String(50))
    screenshot1 = Column(String(500))
    screenshot2 = Column(String(500))
    promocode = Column(String(100))
    user_name = Column(String(100))
    user_id = Column(String(100))
    is_active = Column(Boolean)
    is_blocked = Column(Boolean)
    registration_date = Column(DateTime(), default=datetime.now)


    

# Определение класса Photo для таблицы Photos
class Photo(Base):
    __tablename__ = 'Photos'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(100))
    is_screenshot = Column(Boolean)
    photo_path = Column(String(500))


# Определение класса Admins для таблицы admins
class Admins(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(50))

# Функция для создания таблиц в базе данных
def start_db():
    Base.metadata.create_all(bind=engine, checkfirst=True)


