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

def select_education(is_filter=False):
    if not is_filter:
        btn1 = InlineKeyboardButton(text='СПО', callback_data='register_education:spo')
        btn2 = InlineKeyboardButton(text='Бакалавриат', callback_data='register_education:bakalavriat')
        btn3 = InlineKeyboardButton(text='Специалитет', callback_data='register_education:specialitet')
        btn4 = InlineKeyboardButton(text='Магистратура', callback_data='register_education:magistratura')
        keyboard = InlineKeyboardMarkup().add(btn1, btn2).add(btn3, btn4)

    elif is_filter:
        btn1 = InlineKeyboardButton(text='СПО', callback_data='filter_education:spo')
        btn2 = InlineKeyboardButton(text='Бакалавриат', callback_data='filter_education:bakalavriat')
        btn3 = InlineKeyboardButton(text='Специалитет', callback_data='filter_education:specialitet')
        btn4 = InlineKeyboardButton(text='Магистратура', callback_data='filter_education:magistratura')
        btn5 = InlineKeyboardButton(text='Любая', callback_data='filter_education:all')
        keyboard = InlineKeyboardMarkup().add(btn1, btn2).add(btn3, btn4).add(btn5)
    return keyboard

async def select_university(is_filter=False):
    universities = await read_university()

    keyboard = InlineKeyboardMarkup()

    if not is_filter:
        for university in universities:
            if university != 'all':
                btn = InlineKeyboardButton(text=university, callback_data=f'register_university:{university}')
                keyboard.add(btn)
        return keyboard
    elif is_filter:
        for university in universities:
            if university != 'all':
                btn = InlineKeyboardButton(text=university, callback_data=f'filter_university:{university}')
                keyboard.add(btn)
        btn_all = InlineKeyboardButton(text='Все', callback_data='filter_university:all')
        keyboard.add(btn_all)
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
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(btn1)
    return keyboard

def my_profile_kb():
    btn1 = InlineKeyboardButton(text='Заполнить анкету заново', callback_data='repeat_profile')
    btn2 = InlineKeyboardButton(text='Я больше не хочу никого искать ', callback_data='disable_active')
    keyboard = InlineKeyboardMarkup().add(btn1).add(btn2)
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
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(btn1, btn4, btn2)
    return keyboard


def filters_main_kb():
    btn1 = KeyboardButton('Возраст')
    btn2 = KeyboardButton('Уч. заведение')
    btn3 = KeyboardButton('Курс')
    btn4 = KeyboardButton('Форма обучения')
    btn5 = KeyboardButton('Вернуться назад')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(btn1, btn2).row(btn3, btn4).row(btn5)
    return keyboard

def filter_cource_age_kb(is_filter_age=False):
    if not is_filter_age:
        btn1 = InlineKeyboardButton(text='Любой курс', callback_data='filter_cource_all')
        btn2 = InlineKeyboardButton(text='Отмена', callback_data='filter_cource_cancle')
    elif is_filter_age:
        btn1 = InlineKeyboardButton(text='Любой возраст', callback_data='filter_age_all')
        btn2 = InlineKeyboardButton(text='Отмена', callback_data='filter_age_cancle')
    keyboard = InlineKeyboardMarkup().add(btn1).add(btn2)
    return keyboard
