import time

from keyboards import reminder_kb
from dataBase.db_commands import get_user_by_id

async def check_activity(dict_of_profiles, bot):
    for user in dict_of_profiles:
        data = await get_user_by_id(user)
        if not(data["is_blocked"]) and data["is_active"]:
            if int(time.time()) - dict_of_profiles[user]['last_activity'] > 30:
                dict_of_profiles[user]['last_activity'] = int(time.time())
                await bot.send_message(
                    int(user),
                    'От вас давно не было никакой активности',
                    reply_markup=reminder_kb()
                )


