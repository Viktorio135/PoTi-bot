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

def select_search():
    btn1 = InlineKeyboardButton(text='Мальчика', callback_data='register_search:boy')
    btn2 = InlineKeyboardButton(text='Девочку', callback_data='register_search:girl')
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
    btn2 = InlineKeyboardButton('Заполнить заново:(', callback_data='repeat_registration')
    keyboard = InlineKeyboardMarkup().add(btn1).add(btn2)
    return keyboard

def menu_kb():
    btn1 = KeyboardButton(text='Моя анкета')
    btn2 = KeyboardButton(text='Cмотреть анкеты')
    btn3 = KeyboardButton(text='Фильтр')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(btn2).row(btn1, btn3)
    return keyboard

def reg_menu():
    btn1 = KeyboardButton(text='Главное меню')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(btn1)
    return keyboard

def my_profile_kb():
    btn1 = InlineKeyboardButton(text='Заполнить анкету заново', callback_data='repeat_profile')
    keyboard = InlineKeyboardMarkup().add(btn1)
    return keyboard

def search_kb():
    btn1 = KeyboardButton('❤️')
    btn2 = KeyboardButton('👎')
    btn3 = KeyboardButton('💤')
    btn4 = KeyboardButton('⚠️')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(btn1, btn4, btn2, btn3)
    return keyboard

def show_like_kb():
    btn1 = KeyboardButton('Показать')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(btn1)
    return keyboard

def like_kb():
    btn1 = KeyboardButton('💜')
    btn2 = KeyboardButton('👎🏻')
    btn4 = KeyboardButton('❗️')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(btn1, btn4, btn2)
    return keyboard