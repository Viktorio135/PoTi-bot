from aiogram.types import (
    InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, 
    InlineKeyboardButton, 
    KeyboardButton
)

def check_sub():
    btn1 = InlineKeyboardButton(text='Проверить', callback_data='check_sub')
    keyboard = InlineKeyboardMarkup().add(btn1)
    return keyboard




def select_role(second=False):
    btn1 = KeyboardButton(text='Золото 🥇')
    btn2 = KeyboardButton(text='Опыт 💪🏼')
    btn3 = KeyboardButton(text='Мид 🧙🏻‍♂️')
    btn4 = KeyboardButton(text='Лес 🌳')
    btn5 = KeyboardButton(text='Роум 🔰')
    btn6 = KeyboardButton(text='Все')
    btn7 = KeyboardButton(text='Это все, сохранить роли')

    if not second:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(btn3, btn4, btn5).row(btn1, btn2).row(btn6)
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(btn1, btn2, btn3).row(btn4, btn5).row(btn7)
    return keyboard


def select_role_next():
    btn1 = InlineKeyboardButton(text='Это все, сохранить роли', callback_data='second_screenshot')
    keyboard = InlineKeyboardMarkup().add(btn1)
    return keyboard

def skip_description():
    btn1 = KeyboardButton(text='Пропустить')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(btn1)
    return keyboard


def second_screenshot():
    btn1 = InlineKeyboardButton(text='Это все, сохранить фото', callback_data='second_screenshot')
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
    btn1 = KeyboardButton(text='2')#👤 Моя анекта
    btn2 = KeyboardButton(text='1')#🚀 Cмотреть анкеты
    btn3 = KeyboardButton(text='3')#Я больше не хочу никого искать.
    btn4 = KeyboardButton(text='4')#Пригласи друзей - получи больше лайков 😎.
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(btn2, btn1, btn3, btn4)
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
    btn1 = KeyboardButton(text='𝟏')#смотреть анкеты
    btn2 = KeyboardButton(text='𝟐')#заполнить заново
    btn3 = KeyboardButton(text='𝟑')#изменить фото
    btn4 = KeyboardButton(text='𝟒')#изменить текст
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(btn1, btn2, btn3, btn4)
    return keyboard


def change_profile_kb():
    btn1 = InlineKeyboardButton(text='📷 Фото', callback_data='change_ask:photo')
    btn2 = InlineKeyboardButton(text='📝 Описание', callback_data='change_ask:description')
    keyboard = InlineKeyboardMarkup().add(btn1, btn2)
    return keyboard

def change_profile_photo_cancel():
    btn1 = KeyboardButton(text='❌ Отмена')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(btn1)
    return keyboard
 
def change_profile_photo2_cancel():
    btn1 = KeyboardButton(text='Это все, сохранить фото')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).row(btn1)
    return keyboard

def change_profile_description_cancel():
    btn1 = KeyboardButton(text='❌ Отмена')
    keyboard = ReplyKeyboardMarkup().add(btn1)
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
