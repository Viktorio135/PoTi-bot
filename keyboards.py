import json
from aiogram.types import (
    InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, 
    InlineKeyboardButton, 
    KeyboardButton
)
from dataBase.db_commands import read_university

def select_sex():
    btn1 = InlineKeyboardButton(text='Мальчик', callback_data='register_sex:boy')
    btn2 = InlineKeyboardButton(text='Девочка', callback_data='register_sex:girl')
    keyboard = InlineKeyboardMarkup().add(btn1, btn2)
    return keyboard

def select_education():
    btn1 = InlineKeyboardButton(text='СПО', callback_data='register_education:spo')
    btn2 = InlineKeyboardButton(text='Бакалавриат', callback_data='register_education:bakalavriat')
    btn3 = InlineKeyboardButton(text='Специалитет', callback_data='register_education:specialitet')
    btn4 = InlineKeyboardButton(text='Магистратура', callback_data='register_education:magistratura')

    keyboard = InlineKeyboardMarkup().add(btn1, btn2).add(btn3, btn4)
    return keyboard

async def select_university():
    universities = await read_university()

    keyboard = InlineKeyboardMarkup()

    for university in universities:
        btn = InlineKeyboardButton(text=university, callback_data=f'register_university:{university}')
        keyboard.add(btn)

    return keyboard

def end_registration_kb(file_id):
    
    btn1 = InlineKeyboardButton(text='Всё верно!', callback_data=f'end_registration:{file_id}')
    # btn2 = InlineKeyboardButton('Заполнить заново:(')
    keyboard = InlineKeyboardMarkup().add(btn1)
    return keyboard
