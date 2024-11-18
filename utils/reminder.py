import time
import logging

from keyboards import menu_kb
from dataBase.db_commands import get_user_by_id

async def check_activity(dict_of_profiles, bot):
    try:
        for user in dict_of_profiles:
            if user.isdigit():
                data = await get_user_by_id(user)
                if data != 'User not found' and data != 'Error':
                    if not(data["is_blocked"]) and data["is_active"]:
                        if int(time.time()) - dict_of_profiles[user]['last_activity'] > 129600:
                            dict_of_profiles[user]['last_activity'] = int(time.time())
                            await bot.send_message(
                                int(user),
                                'Привет! От тебя давно не было активности. 😒\n\n❤️ Посмотри несколько анкет чтобы ничего не пропустить. 👈\n\n1. Смотреть анкеты.\n2. Моя анкета.\n3. Я больше не хочу никого искать.\n***\n4. Пригласи друзей - получи больше лайков 😎.',
                                reply_markup=menu_kb()
                            )
        logging.info('Успешное напоминание')
    except Exception as e:
        logging.error('Ошибка напоминания', exc_info=True)


async def unlock_limits(dict_of_profiles):
    try:
        for user in dict_of_profiles:
            if user.isdigit():
                dict_of_profiles[user]['activity'] = 0
    except:
        logging.error('Ошибка сброса лимита', exc_info=True)



async def update_love_stat(love_activity):
    try:
        love_activity[0] = 0
    except:
        logging.error('Ошибка сброса активности', exc_info=True)