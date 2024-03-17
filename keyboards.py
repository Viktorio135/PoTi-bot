from aiogram.types import (
    InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, 
    InlineKeyboardButton, 
    KeyboardButton
)
from dataBase.db_commands import read_university

def select_sex():
    btn1 = InlineKeyboardButton(text='👱🏻‍♂️ Мужской', callback_data='register_sex:boy')
    btn2 = InlineKeyboardButton(text='👱🏻‍♀️ Женский', callback_data='register_sex:girl')
    keyboard = InlineKeyboardMarkup().add(btn1, btn2)
    return keyboard

def select_search():
    btn1 = InlineKeyboardButton(text='👱🏻‍♂️ Парня', callback_data='register_search:boy')
    btn2 = InlineKeyboardButton(text='👱🏻‍♀️ Девушку', callback_data='register_search:girl')
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
    universities.remove('all')
    keyboard = InlineKeyboardMarkup()

    if not is_filter:
        for university in range(0, len(universities), 3):
            if universities[university] != 'all':
                if (university + 1 < len(universities)) and (university + 2 < len(universities)):
                    btn1 = InlineKeyboardButton(text=universities[university], callback_data=f'register_university:{universities[university]}')
                    btn2 = InlineKeyboardButton(text=universities[university+1], callback_data=f'register_university:{universities[university+1]}')
                    btn3 = InlineKeyboardButton(text=universities[university+2], callback_data=f'register_university:{universities[university+2]}')
                    keyboard.add(btn1, btn2, btn3)
                elif (university + 1 < len(universities)) and (university + 2 >= len(universities)):
                    btn1 = InlineKeyboardButton(text=universities[university], callback_data=f'register_university:{universities[university]}')
                    btn2 = InlineKeyboardButton(text=universities[university+1], callback_data=f'register_university:{universities[university+1]}')
                    keyboard.add(btn1, btn2)
                else:
                    btn1 = InlineKeyboardButton(text=universities[university], callback_data=f'register_university:{universities[university]}')
                    keyboard.add(btn1)
        return keyboard
#filter_university
    elif is_filter:
        for university in range(0, len(universities), 3):
            if universities[university] != 'all':
                if (university + 1 < len(universities)) and (university + 2 < len(universities)):
                    btn1 = InlineKeyboardButton(text=universities[university], callback_data=f'filter_university:{universities[university]}')
                    btn2 = InlineKeyboardButton(text=universities[university+1], callback_data=f'filter_university:{universities[university+1]}')
                    btn3 = InlineKeyboardButton(text=universities[university+2], callback_data=f'filter_university:{universities[university+2]}')
                    keyboard.add(btn1, btn2, btn3)
                elif (university + 1 < len(universities)) and (university + 2 >= len(universities)):
                    btn1 = InlineKeyboardButton(text=universities[university], callback_data=f'filter_university:{universities[university]}')
                    btn2 = InlineKeyboardButton(text=universities[university+1], callback_data=f'filter_university:{universities[university+1]}')
                    keyboard.add(btn1, btn2)
                else:
                    btn1 = InlineKeyboardButton(text=universities[university], callback_data=f'filter_university:{universities[university]}')
                    keyboard.add(btn1)
        btn_all = InlineKeyboardButton(text='Все', callback_data='filter_university:all')
        keyboard.add(btn_all)
        return keyboard

def description_is_empty():
    btn1 = InlineKeyboardButton(text='Оставить пустым', callback_data='description_is_empty')
    keyboard = InlineKeyboardMarkup().add(btn1)
    return keyboard

def promocode_is_empty():
    btn1 = InlineKeyboardButton(text='Оставить пустым', callback_data='promocode_is_empty')
    keyboard = InlineKeyboardMarkup().add(btn1)
    return keyboard

def end_registration_kb(file_id):
    
    btn1 = InlineKeyboardButton(text='Всё верно!', callback_data=f'end_registration:{file_id}')
    btn2 = InlineKeyboardButton('Заполнить заново', callback_data='repeat_registration')
    keyboard = InlineKeyboardMarkup().add(btn1).add(btn2)
    return keyboard

def menu_kb():
    btn1 = KeyboardButton(text='👤 Моя анекта')
    btn2 = KeyboardButton(text='🚀 Cмотреть анкеты')
    btn3 = KeyboardButton(text='⚙️ Фильтры')
    btn4 = KeyboardButton(text='📚 История')
    btn5 = KeyboardButton(text='🆘 Поддержка')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(btn2).row(btn5, btn4, btn3).row(btn1)
    return keyboard


def support_kb():
    btn1 = InlineKeyboardButton(text='📔 Инструкция', callback_data='support:instruction')
    btn2 = InlineKeyboardButton(text='✍️ Связаться с нами', callback_data='support:contact')
    keyboard = InlineKeyboardMarkup().add(btn1).add(btn2)
    return keyboard



def reminder_kb():
    btn1 = KeyboardButton(text='🚀 Cмотреть анкеты')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(btn1)
    return keyboard


def reg_menu():
    btn1 = KeyboardButton(text='Меню')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(btn1)
    return keyboard

def my_profile_kb():
    btn1 = InlineKeyboardButton(text='🗑️ Заполнить заново', callback_data='repeat_profile')
    btn2 = InlineKeyboardButton(text='🖊️ Изменить', callback_data='change_profile')
    btn3 = InlineKeyboardButton(text='🔑 Мой реферальный промокод', callback_data='referal_code')
    btn4 = InlineKeyboardButton(text='🛑 Я больше не хочу никого искать', callback_data='disable_active')
    keyboard = InlineKeyboardMarkup().add(btn1).add(btn2).add(btn3).add(btn4)
    return keyboard


def change_profile_kb():
    btn1 = InlineKeyboardButton(text='📷 Фото', callback_data='change_ask:photo')
    btn2 = InlineKeyboardButton(text='📝 Описание', callback_data='change_ask:description')
    # btn3 = InlineKeyboardButton(text='Возраст', callback_data='change_ask:age')
    # btn4 = InlineKeyboardButton(text='Курс', callback_data='change_ask:cource')
    keyboard = InlineKeyboardMarkup().add(btn1, btn2)
    return keyboard

def change_profile_photo_cancel():
    btn1 = InlineKeyboardButton(text='❌ Отмена', callback_data='change_profile_photo_cancel')
    keyboard = InlineKeyboardMarkup().add(btn1)
    return keyboard

def change_profile_description_cancel():
    btn1 = InlineKeyboardButton(text='❌ Отмена', callback_data='change_profile_description_cancel')
    btn2 = InlineKeyboardButton(text='Сделать пустым', callback_data='change_profile_description_empty')
    keyboard = InlineKeyboardMarkup().add(btn2).add(btn1)
    return keyboard


def search_kb():
    btn1 = KeyboardButton('❤️')
    btn2 = KeyboardButton('👎')
    btn3 = KeyboardButton('💤')
    btn4 = KeyboardButton('⚠️')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(btn1, btn4, btn2, btn3)
    return keyboard

def show_like_kb():
    btn1 = KeyboardButton('🚀 Показать')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(btn1)
    return keyboard

def like_kb():
    btn1 = KeyboardButton('💜')
    btn2 = KeyboardButton('👎🏻')
    btn4 = KeyboardButton('❗️')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(btn1, btn4, btn2)
    return keyboard


def filters_main_kb():
    btn1 = KeyboardButton('🔞 Возр.диапазон')
    btn2 = KeyboardButton('👨‍🎓 Уч. заведение')
    btn3 = KeyboardButton('1️⃣ Курс')
    btn4 = KeyboardButton('📕 Форма обучения')
    btn5 = KeyboardButton('⏪️ Назад')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).row(btn1, btn2).row(btn3, btn4).row(btn5)
    return keyboard

def filter_cource_age_kb(is_filter_age=False):
    if not is_filter_age:
        btn1 = InlineKeyboardButton(text='Любой курс', callback_data='filter_cource_all')
        btn2 = InlineKeyboardButton(text='❌ Отмена', callback_data='filter_cource_cancle')
    elif is_filter_age:
        btn1 = InlineKeyboardButton(text='Любой возраст', callback_data='filter_age_all')
        btn2 = InlineKeyboardButton(text='❌ Отмена', callback_data='filter_age_cancle')
    keyboard = InlineKeyboardMarkup().add(btn1).add(btn2)
    return keyboard

def history_dislike_kb(has_nexn, has_last, page):
    keyboard = InlineKeyboardMarkup()
    if has_nexn and has_last:
        btn1 = InlineKeyboardButton(text='❤️', callback_data=f'history_like:{page}')
        btn2 = InlineKeyboardButton(text='👉', callback_data=f'history_dislike_next:{page}')
        btn3 = InlineKeyboardButton(text='👈', callback_data=f'history_dislike_last:{page}')
        keyboard.add(btn3, btn1, btn2)
    elif has_nexn and not has_last:
        btn1 = InlineKeyboardButton(text='❤️', callback_data=f'history_like:{page}')
        btn2 = InlineKeyboardButton(text='👉', callback_data=f'history_dislike_next:{page}')
        keyboard.add(btn1, btn2)
    elif not has_nexn and has_last:
        btn1 = InlineKeyboardButton(text='❤️', callback_data=f'history_like:{page}')
        btn2 = InlineKeyboardButton(text='👈', callback_data=f'history_dislike_last:{page}')
        keyboard.add(btn2, btn1)
    else:
        btn1 = InlineKeyboardButton(text='❤️', callback_data=f'history_like:{page}')
        keyboard.add(btn1)
    return keyboard


def report_kb():
    btn1 = InlineKeyboardButton(text='🔞 Порнография', callback_data=f'report:adults')
    btn2 = InlineKeyboardButton(text='💊 Наркотики', callback_data=f'report:drugs')
    btn3 = InlineKeyboardButton(text='💰 Скам', callback_data=f'report:scum')    
    btn4 = InlineKeyboardButton(text='🦨 Другое', callback_data=f'report:other')
    btn5 = InlineKeyboardButton(text='❌ Отмена', callback_data='report:cancel')
    keyboard = InlineKeyboardMarkup().add(btn1, btn2).add(btn3, btn4).add(btn5)
    return keyboard
