import json
import logging
import threading
import os
import time
import random

from dotenv import load_dotenv

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from dataBase.db_commands import (
    create_user, has_register, get_university_id_by_name, 
    get_university_name_by_id, get_user_by_id, delete_profile, 
    get_list_of_profiles, update_active_to_true, update_active_to_false,
    update_filter_age_max, update_filter_age_min, update_filter_university_db,
    update_filter_cource, update_filter_education_db, change_description_by_id,
    change_age_by_id, get_list_of_admins, block_user_db,
    unblock_user_db, get_statistic_user_db, get_list_of_users_for_spam_db,
    add_admin_db, delete_admin_db, add_university_db, delete_university_db
)
from keyboards import (
    select_sex, select_university, select_education, 
    end_registration_kb, menu_kb, reg_menu,
    my_profile_kb, select_search, search_kb,
    show_like_kb, like_kb, filters_main_kb,
    filter_cource_age_kb, history_dislike_kb, report_kb, 
    change_profile_kb, description_is_empty, reminder_kb,
    support_kb, promocode_is_empty
)

from states.user_states import (
    Register_new_user, Filter_age, Filter_university, 
    Filter_course, Change_age, Change_description, 
    Change_photo, ReportUserOther
)

from states.admin_states import (
    AdminBlockUser, AdminUnblockUser, AdminGetUserById,
    AdminSpamHasPhoto, AdminSpamOnlyText, AdminSpamWithPhoto,
    AdminGetUserByPhoto, AdminSendMessageFromUserById, AdminAddAdmin,
    AdminDeleteAdmin, AdminAddUniversity, AdminDeleteUniversity
)

from utils.search_photo import compare_images
from dataBase.models import start_db
from utils.scheduler import start_schedule




load_dotenv()
token = os.getenv('TOKEN')
main_admin = os.getenv('MAIN_ADMIN')

bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())

cached_data = {}
dict_of_profiles = {}

@dp.message_handler(commands='start')
async def cmd_start(msg: types.Message):
    await bot.send_message(
            msg.from_user.id, 
            'Привет, ты попал в Link Up Students | Калининград\n Мы поможем тебе найти кого-нибудь найти.'
            )
    if await has_register(str(msg.from_user.id)):
        await menu(msg)
    elif not(await has_register(str(msg.from_user.id))):
        await register_or_update_user(msg)

############################## Регистрация ####################################

async def register_or_update_user(msg: types.Message, is_new=False):
    if not is_new:
        await bot.send_message(
                msg.from_user.id, 
                'Для начала, давай создадим аккаунт!\nНапишите мне ваше имя, которое будут все видеть в анкете?'
                )
        await Register_new_user.name.set()
    else:
        await bot.send_message(
                msg.from_user.id, 
                'Давай создадим анкету заново.\nНапишите мне ваше имя, которое будут все видеть в анкете?'
                )
        await Register_new_user.name.set()
         

@dp.message_handler(state=Register_new_user.name)
async def register_name(msg: types.Message, state: FSMContext):

    async with state.proxy() as data:
        data['name'] = msg.text

    await bot.send_message(
        msg.from_user.id, 
        f'Отлично, {data["name"]}, теперь давай определимся с полом!', 
        reply_markup=select_sex()
        )
    await Register_new_user.next()


@dp.callback_query_handler(state=Register_new_user.sex)
async def register_sex(callback_query: types.CallbackQuery, state: FSMContext):

    await callback_query.message.delete()

    z = callback_query.data.split(':')
    async with state.proxy() as data:
        data['sex'] = z[1]

    await bot.send_message(
        callback_query.from_user.id, 
        'Прекрасно, кого ты хочешь найти?',
        reply_markup=select_search()
        )
    #Прекрасно, сколько тебе лет?
    await Register_new_user.next()

@dp.callback_query_handler(state=Register_new_user.search_to)
async def register_search(callback_query: types.CallbackQuery, state: FSMContext):
     
    await callback_query.message.delete()
    z = callback_query.data.split(':')
    async with state.proxy() as data:
        data['search_to'] = z[1]

    await bot.send_message(
        callback_query.from_user.id, 
        'Cколько тебе лет?',
        )
    #Прекрасно, сколько тебе лет?
    await Register_new_user.next()

@dp.message_handler(state=Register_new_user.age)
async def register_age(msg: types.Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    if msg.text.isdigit() and 15 <= int(msg.text) < 100:
            async with state.proxy() as data:
                data['age'] = msg.text
            cached_data[user_id] = await bot.send_message(
                msg.from_user.id, 
                'Хорошо, теперь придумая описание профиля',
                reply_markup=description_is_empty()
                )
            
            await Register_new_user.next()
    else:
        await bot.send_message(
                msg.from_user.id, 
                'Пожалуйста, введите корректный возраст, от 15 лет'
            )
        return
    
@dp.callback_query_handler(state=Register_new_user.description)
async def callback_description_is_empty(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = str(callback_query.from_user.id)
    async with state.proxy() as data:
        data["description"] = ''
    if user_id in cached_data:
        await cached_data[user_id].delete()
        del cached_data[user_id]
    await bot.send_message(
        callback_query.from_user.id, 
        'Давай теперь определимся с учебным заведением!',
        reply_markup=await select_university() 
    )
    await Register_new_user.next()
    
@dp.message_handler(state=Register_new_user.description)
async def register_description(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['description'] = msg.text
    await bot.send_message(
        msg.from_user.id, 
        'Давай теперь определимся с учебным заведением!',
        reply_markup=await select_university() 
    )
    await Register_new_user.next()


@dp.callback_query_handler(lambda c: 'register_university' in c.data, state=Register_new_user.university)
async def register_university(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    university = callback_query.data.split(':')[1]
    async with state.proxy() as data:
        data['university'] = await get_university_id_by_name(university)
    await bot.send_message(
         callback_query.from_user.id, 
         'Какая у тебя форма обучения?',
         reply_markup=select_education()
    )
    await Register_new_user.next()

@dp.callback_query_handler(lambda c: 'register_education' in c.data, state=Register_new_user.education)
async def register_education(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.delete()
    education = callback_query.data.split(':')[1]
    async with state.proxy() as data:
        data['education'] = education
    await bot.send_message(
        callback_query.from_user.id, 
        'Остались последние штрихи, на какой специальности ты учишься?'
    )
    await Register_new_user.next()

@dp.message_handler(state=Register_new_user.speciality)
async def register_speciality(msg: types.Message, state: FSMContext):
    
    async with state.proxy() as data:
        data['speciality'] = msg.text
    await bot.send_message(
         msg.from_user.id, 
         'На каком курсе ты проходишь обучение?'
    )
    await Register_new_user.next()

@dp.message_handler(state=Register_new_user.course)
async def register_course(msg: types.Message, state: FSMContext):
    if msg.text.isdigit() and 1 <= int(msg.text) <= 5:
            async with state.proxy() as data:
                data['course'] = msg.text

            await bot.send_message(
                msg.from_user.id, 
                'Пришлите мне вашу фотографию!'
                )

            await Register_new_user.next()
    else:
        await bot.send_message(
                msg.from_user.id, 
                'Пожалуйста, введите корректный номер курса'
            )
        return


@dp.message_handler(content_types=['photo'], state=Register_new_user.photos)
async def register_photo(msg: types.Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    try:
        file_name = f'{msg.from_user.id}.jpg'
        path = f'static/users_photo/{file_name}'
        await msg.photo[-1].download(path)

        async with state.proxy() as data:
                data['photos'] = path
                
        await bot.send_message(
             msg.from_user.id, 
             'Фотография успешно добавлена'
             )
        await Register_new_user.next()
        
        cached_data[user_id] = await bot.send_message(
                                    msg.from_user.id,
                                    'И напоследок, введите реферальный промокод, если у тебя он есть',
                                    reply_markup=promocode_is_empty()
                                )
        
        
        # await end_registration(msg, data)
        # await state.finish()
    except Exception as e:   
        logging.error(f'Ошибка в регистрации при сохранении фото у пользователя {user_id}', exc_info=True) 
        await bot.send_message(
            msg.from_user.id, 
            'Возникла ошибка. Попробуйте еще раз'
            )
        return
    
@dp.message_handler(state=Register_new_user.promocod)
async def registration_promocode(msg: types.Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    if msg.text.isdigit():
        if user_id in cached_data:
            await cached_data[user_id].delete()
            del cached_data[user_id]
        if await has_register(msg.text):
            async with state.proxy() as data:
                data["promocode"] = msg.text
            await bot.send_message(
                msg.from_user.id,
                'Ваш промокод успешно активирован!\n\nВаша анкета получила буст на 24 часа!'
            )
            await bot.send_message(
                data['promocode'],
                'По вашему реферальному промокоду зарегистрировался пользователь\n\nВаша анкета получила буст на 24 часа!'
            )
            await end_registration(msg, data)
            await state.finish()
        elif not(await has_register(msg.text)):
            cached_data[user_id] = await bot.send_message(
                msg.from_user.id,
                'Такого промокода не существует, попробуйте еще раз...',
                reply_markup=promocode_is_empty()
            )
            return
    else:
        cached_data[user_id] = await bot.send_message(
            msg.from_user.id,
            'Промокод может состоять только из цифр, попробуйте еще раз...',
            reply_markup=promocode_is_empty()
        )
        return
    
@dp.callback_query_handler(state=Register_new_user.promocod)
async def registration_promocode_callback(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = str(callback_query.from_user.id)
    if user_id in cached_data:
        await cached_data[user_id].delete()
        del cached_data[user_id]
    async with state.proxy() as data:
        data["promocode"] = ''
    await state.finish()
    await end_registration(callback_query, data)
    
        

async def end_registration(msg: types.Message, data):
    datas = {
        "name": data["name"],
        "sex": data["sex"], 
        "search_to": data["search_to"],
        "age": data["age"], 
        "description": data["description"], 
        "university": data["university"], 
        "education": data["education"], 
        "speciality": data["speciality"], 
        "course": data["course"], 
        "photos": data["photos"]
        }
    file_id = hash(json.dumps(datas, sort_keys=True))
    cached_data[file_id] = datas

    match datas["education"]:
        case 'spo':
            datas["education"] = 'СПО'
        case 'bakalavriat':
            datas["education"] = 'Бакалавриат'
        case 'specialitet':
            datas["education"] = 'Специалитет'
        case 'magistratura':
            datas["education"] = 'Магистратура'

    await bot.send_message(msg.from_user.id, 
            f'Ты успешно завершил, твой профиль будет выглядеть вот так:'
        )
    university = await get_university_name_by_id(datas["university"])
    await bot.send_photo(
            msg.from_user.id, 
            open(f'static/users_photo/{msg.from_user.id}.jpg', 'rb'),
            f'{datas["name"]}, {datas["age"]}, {university} - {datas["speciality"]}({datas["course"]} курс, {datas["education"]})\n\n{datas["description"]}',
            reply_markup=end_registration_kb(file_id)
        ) 
    

@dp.callback_query_handler(lambda c: 'end_registration' in c.data)
async def save_user_to_bd(callback_query: types.CallbackQuery):
    try:
        file_id = int(callback_query.data.split(':')[1])
        data = cached_data.get(file_id)        
        del cached_data[file_id]

        user_name = callback_query.from_user.username
        id_user = callback_query.from_user.id

        save = await create_user(
            name=data["name"], 
            sex=data["sex"], 
            search_to=data["search_to"],
            age=data["age"], 
            user_name=user_name, 
            user_id=id_user,
            photos=data["photos"], 
            university=data["university"],
            speciality=data["speciality"], 
            course=data["course"], 
            education=data["education"], 
            description='' if data["description"] == '0' else data["description"]
        )


        if save:
            await bot.send_message(
                callback_query.from_user.id, 
                'Отлично! Надеюсь вы хорошо проведете время ;) Начинай общаться!',
                reply_markup=reg_menu()
            )
            
        else:
            await bot.send_message(
                callback_query.from_user.id, 
                'Возникла ошибка. Попробуйте еще раз'
            )
            await register_or_update_user(callback_query)


    except Exception as e:
            logging.error(f'Ошибка в окончании регистрации у пользователя {str(callback_query.from_user.id)}', exc_info=True)
            await bot.send_message(
                 callback_query.from_user.id,
                 'Возникла ошибка. Попробуйте еще раз'
            )
            await register_or_update_user(callback_query.message)


@dp.callback_query_handler(lambda c: c.data == 'repeat_registration')
async def repeat_reg(callback_query: types.CallbackQuery):
    await register_or_update_user(callback_query, is_new=True)

##########################################################################################

#################################### Главное меню #####################################
@dp.message_handler(Text('⏪️ Назад'))
@dp.message_handler(Text('Меню'))
@dp.message_handler(commands='menu')
async def menu(msg: types.Message):
    try:
        user = await get_user_by_id(str(msg.from_user.id))
        
        if user != 'Error' and user != 'User not found':
            await bot.send_message(
                msg.from_user.id,
                f'{user["name"]}, вы попали в главное меню, выбери действие;)',
                reply_markup=menu_kb()
            )
        else:
            await bot.send_message(
                msg.from_user.id,
                f'Возникла ошибка. Попробуйте еще раз',
            )
             
    except Exception as e:
        logging.error(f'Ошибка в главном меню у пользователя {str(msg.from_user.id)}', exc_info=True)
        await bot.send_message(
                msg.from_user.id,
                'Возникла ошибка. Попробуйте еще раз',
            )
        

@dp.message_handler(Text('🆘 Поддержка'))
async def support(msg: types.Message):
    await bot.send_message(
        msg.from_user.id,
        'Выберите действие',
        reply_markup=support_kb()
    )

@dp.callback_query_handler(lambda c: 'support' in c.data)
async def support_callback(callback_query: types.CallbackQuery):
    cause = callback_query.data.split(':')[1]
    match cause:
        case 'instruction':
            await bot.send_message(
                callback_query.from_user.id,
                'Cсылка на инструкцию:\n\nhttps://telegra.ph/Instrukciya-k-botu-LinkUp-03-11'
            )
        case 'contact':
            await bot.send_message(
                callback_query.from_user.id,
                'Столкнулись с проблемой, хотите предложить что-то новое:\n\n@LinkUp_admin'
            )


############# Анкета #############


@dp.message_handler(Text('👤 Моя анекта'))
async def my_profile(msg: types.Message):
    user_id = str(msg.from_user.id)
    is_blocked = await get_user_by_id(user_id)
    if not is_blocked["is_blocked"]:
        await bot.send_message(
            msg.from_user.id,
            'Ваша анкета выглядит вот так:'
        )
        user = await get_user_by_id(user_id, Anketa=True)

        if user != 'User not found':
            await bot.send_photo(
                msg.from_user.id, 
                open(f'static/users_photo/{msg.from_user.id}.jpg', 'rb'),
                user,
                reply_markup=my_profile_kb()
            ) 
    elif is_blocked["is_blocked"]:
        await bot.send_message(
            msg.from_user.id,
            'Ваша анкета была заблокирована'
        )


@dp.callback_query_handler(lambda c: c.data == 'repeat_profile')
async def repeat_profile(callback_query: types.CallbackQuery):
    await delete_profile(callback_query.message.chat.id)
    await register_or_update_user(callback_query, is_new=True)


@dp.callback_query_handler(lambda c: c.data == 'change_profile')
async def change_profile(callback_query: types.CallbackQuery):
    await bot.send_message(
        callback_query.from_user.id,
        'Что вы хотите изменить?',
        reply_markup=change_profile_kb()
    )

@dp.callback_query_handler(lambda c: 'change_ask' in c.data)
async def change_ask(callback_query: types.CallbackQuery):
    change = callback_query.data.split(':')[1]
    match change:
        case 'photo':
            await callback_query.message.delete()
            await Change_photo.photo.set()
            await bot.send_message(
                callback_query.from_user.id, 
                'Отправьте мне новую фотографию'
            )
        case 'description':
            await callback_query.message.delete()
            await Change_description.description.set()
            await bot.send_message(
                callback_query.from_user.id, 
                'Расскажите о себе'
            )
        # case 'age':
        #     await callback_query.message.delete()
        #     await Change_age.age.set()
        #     await bot.send_message(
        #         callback_query.from_user.id, 
        #         'Сколько тебе лет?'
        #     )
        
@dp.message_handler(content_types=['photo'], state=Change_photo.photo)
async def state_change_photo(msg: types.Message, state: FSMContext):
    try:
        usere_id = msg.from_user.id
        file_name = f'{usere_id}.jpg'
        path = f'static/users_photo/{file_name}'
        async with state.proxy() as data:
                data['photo'] = path
        await msg.photo[-1].download(path)
        await state.finish()
        await bot.send_message(
            msg.from_user.id, 
            'Фотография успешно обновлена'
            )
        await my_profile(msg)
    except Exception as e:
        logging.error(f'Ошибка при обновлении фото у пользователя {str(msg.from_user.id)}', exc_info=True)
        await bot.send_message(
            msg.from_user.id, 
            'Произошла ошибка, попробуйте отправить фотографию еще раз...'
        )
        return
    
@dp.message_handler(state=Change_description.description)
async def state_change_description(msg: types.Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    async with state.proxy() as data:
        data["description"] = msg.text
    await change_description_by_id(user_id, data["description"])
    await state.finish()
    await bot.send_message(
        msg.from_user.id, 
        'Описание профиля успешно обновлено'
    )
    await my_profile(msg)


# @dp.message_handler(state=Change_age.age)
# async def state_change_age(msg: types.Message, state: FSMContext):
#     user_id = str(msg.from_user.id)
#     if msg.text.isdigit() and 15 <= int(msg.text) < 100:
#             async with state.proxy() as data:
#                 data['age'] = msg.text
#             await change_age_by_id(user_id, int(data["age"]))
#             await bot.send_message(
#                 msg.from_user.id, 
#                 'Ваш возраст успешно обновлен'
#                 )

#             await state.finish()
#             await my_profile(msg)
#     else:
#         await bot.send_message(
#                 msg.from_user.id, 
#                 'Пожалуйста, введите корректный возраст, от 15 лет'
#             )
#         return


        





@dp.callback_query_handler(lambda c: c.data == 'disable_active')
async def disable_active(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user = await get_user_by_id(user_id)
    await update_active_to_false(user_id)
    for user in dict_of_profiles.copy():
        if user_id in user["profiles_list"]:
            user["profiles_list"].remove(user_id)
    await bot.send_message(
        callback_query.from_user.id,
        f'Рад был помочь, {user["name"]}!\nНадеюсь, ты нашел кого-то благодаря мне'
    )

@dp.callback_query_handler(lambda c: c.data == 'referal_code')
async def call_referal_code(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    user = await get_user_by_id(user_id)
    await bot.send_message(
        callback_query.from_user.id,
        f'Твой реферальный промокод:\n\n{user["user_id"]}\n\nПри регистрации нового пользователя по твоему реферальному промокоду, ваша анкета и анкета пользоватлея, который зарегистрировался получат буст на 24 часа!'
    )

###############

@dp.message_handler(Text('📚 История'))
async def last_activity(msg: types.Message, page=0):
    user_id = str(msg.from_user.id)
    user = await get_user_by_id(user_id)
    if not user["is_blocked"]:
        if user_id in dict_of_profiles:
            if len(dict_of_profiles[user_id]["history_dislike"]) != 0 :
                list_history_profiles = dict_of_profiles[user_id]["history_dislike"]
                last_profile_id = list_history_profiles[int(page)]
                last_profile = await get_user_by_id(last_profile_id, Anketa=True)
                if len(list_history_profiles) != 1:
                    next_button = True if last_profile_id != list_history_profiles[-1] else False
                    last_button = True if last_profile_id != list_history_profiles[0] else False
                elif len(list_history_profiles) == 1:
                    next_button = False
                    last_button = False
                await bot.send_photo(
                    msg.from_user.id,
                    open(f'static/users_photo/{last_profile_id}.jpg', 'rb'),
                    last_profile,
                    reply_markup=history_dislike_kb(has_nexn=next_button, has_last=last_button, page=page)
                )
            else:
                await bot.send_message(
                    msg.from_user.id,
                    'Никакой активности нет'
                )
                await menu(msg)
        else:
            await bot.send_message(
                    msg.from_user.id,
                    'Никакой активности нет'
                )
            await menu(msg)
    elif user['is_blocked']:
        await bot.send_message(
            msg.from_user.id,
            'Ваша анкета была заблокирована'
        )

@dp.callback_query_handler(lambda c: 'history_like' in c.data)
async def like_history_dislike(callback_query: types.CallbackQuery):
    page = callback_query.data.split(':')[1]
    user_id = str(callback_query.from_user.id)
    whom = dict_of_profiles[user_id]["history_dislike"][int(page)]
    dict_of_profiles[whom]["who_like"].append(user_id)
    who_len = len(dict_of_profiles[whom]["who_like"])
    await bot.send_message(
        whom,
        'Вы понравились 1 человеку, показать его?' if who_len == 1 else f'Вы понравились {who_len} людям, показать их?',
        reply_markup=show_like_kb()
    )
    await bot.send_message(
        callback_query.from_user.id,
        'Реакция успешно отправлена, ждем ответа...',
    )

@dp.callback_query_handler(lambda c: 'history_dislike_next' in c.data)
async def next_history_dislike(callback_query: types.CallbackQuery):
    page = callback_query.data.split(':')[1]
    await callback_query.message.delete()
    await last_activity(callback_query, page=int(page)+1)

@dp.callback_query_handler(lambda c: 'history_dislike_last' in c.data)
async def next_history_dislike(callback_query: types.CallbackQuery):
    page = callback_query.data.split(':')[1]
    await callback_query.message.delete()
    await last_activity(callback_query, page=int(page)-1)

########################################################################################
    
################################### Смотреть анкеты ######################################
    
@dp.message_handler(Text('🚀 Cмотреть анкеты'))
async def search_love_reg(msg: types.Message):
    user_id = str(msg.from_user.id)
    await update_active_to_true(user_id)
    data = await get_user_by_id(user_id)
    if not data["is_blocked"]:
        if user_id not in dict_of_profiles:
            list_of_profiles = await get_list_of_profiles(
                user_id,
                data["to_education"],
                data["to_university"],
                data["to_course"],
                data["max_age"],
                data["min_age"],
                )
            dict_of_profiles[user_id] = {
                    "profiles_list": list_of_profiles,
                    "last_activity": int(time.time()),
                    "like": [],
                    "history_dislike": [],
                    "who_like": [],
                }
            for user in dict_of_profiles:
                if user != user_id:
                    new_user = await get_user_by_id(user_id)
                    old_user = await get_user_by_id(user)
                    if new_user["sex"] == old_user["search_to"]:
                        if len(dict_of_profiles[user]['profiles_list']) != 0:
                            place = random.randint(0, len(dict_of_profiles[user]['profiles_list']))
                            dict_of_profiles[user]['profiles_list'].insert(place, user_id)
            await search_love_step1(msg)
        else:
            if len(dict_of_profiles[user_id]["profiles_list"]) == 0:
                list_of_profiles = await get_list_of_profiles(
                    user_id,
                    data["to_education"],
                    data["to_university"],
                    data["to_course"],
                    data["max_age"],
                    data["min_age"],
                    )
                if len(list_of_profiles) != 0:
                    dict_of_profiles[user_id]["profiles_list"] = list_of_profiles
                    await search_love_step1(msg)
                else:
                    await bot.send_message(
                        msg.from_user.id,
                        'На данный момент у нас нет подходящих анкет для вас'
                    )
            else:
                await search_love_step1(msg)
    elif data["is_blocked"]:
        await bot.send_message(
            msg.from_user.id,
            'Ваша анкета была заблокирована'
        )

async def update_list_of_profiles_with_new_filters(msg: types.Message):
    user_id = str(msg.from_user.id)
    data = await get_user_by_id(user_id)
    list_of_profiles = await get_list_of_profiles(
            user_id,
            data["to_education"],
            data["to_university"],
            data["to_course"],
            data["max_age"],
            data["min_age"],
            )
    if user_id in dict_of_profiles:
        dict_of_profiles[user_id]["profiles_list"] = list_of_profiles
    else:
        dict_of_profiles[user_id] = {
                "profiles_list": list_of_profiles,
                "last_activity": int(time.time()),
                "like": [],
                "history_dislike": [],
                "who_like": [],
            }


async def search_love_step1(msg: types.Message):
    user_id = str(msg.from_user.id)
    list_of_profiles = dict_of_profiles[user_id]["profiles_list"]

    if list_of_profiles == 'Пользователи не найдены':
        await bot.send_message(
            msg.from_user.id,
            'На данный момент у нас нет подходящих анкет для вас',
            reply_markup=search_kb()
        )
        
    else:
        if len(list_of_profiles) != 0:
            next_profile_id = list_of_profiles[-1]
            next_profile = await get_user_by_id(next_profile_id, Anketa=True)
            await bot.send_photo(
                msg.from_user.id,
                open(f'static/users_photo/{next_profile_id}.jpg', 'rb'),
                next_profile,
                reply_markup=search_kb()
            )
        else:
            await search_love_reg(msg)

    
@dp.message_handler(Text('❤️'))
async def like_main(msg: types.Message):
    user_id = str(msg.from_user.id)
    try:
        user = await get_user_by_id(user_id)
        if not user["is_blocked"]:
            dict_of_profiles[user_id]["last_activity"] = int(time.time())
            list_of_profiles = dict_of_profiles[user_id]["profiles_list"]
            like = list_of_profiles[-1]
            dict_of_profiles[list_of_profiles[-1]]["who_like"].append(user_id)
            
            who_len = len(dict_of_profiles[list_of_profiles[-1]]["who_like"])
            dict_of_profiles[user_id]["profiles_list"].pop()
            await bot.send_message(
                like,
                'Вы понравились 1 человеку, показать его?' if who_len == 1 else f'Вы понравились {who_len} людям, показать их?',
                reply_markup=show_like_kb()
            )

            await bot.send_message(
                msg.from_user.id,
                'Сердечко успешно отправлено, ждем ответа пользователя...',
            )

            await search_love_step1(msg)
        elif user["is_blocked"]:
            await bot.send_message(
                msg.from_user.id,
                'Ваша анкета была заблокирована'
            )
    except Exception as e:
        await bot.send_message(
            msg.from_user.id,
            'Что-то пошло не так, уже чиним...'
        )
        logging.error(user_id, exc_info=True)
        await search_love_step1(msg)
    
@dp.message_handler(Text('👎'))
async def dislike_main(msg: types.Message):
    user_id = str(msg.from_user.id)
    user = await get_user_by_id(user_id)
    if not user["is_blocked"]:
        dict_of_profiles[user_id]["last_activity"] = int(time.time())
        if len(dict_of_profiles[user_id]["history_dislike"]) == 5:
            dict_of_profiles[user_id]["history_dislike"].pop(0)
        if dict_of_profiles[user_id]["profiles_list"][-1] not in dict_of_profiles[user_id]["history_dislike"]:
            dict_of_profiles[user_id]["history_dislike"].append(dict_of_profiles[user_id]["profiles_list"][-1])
        dict_of_profiles[user_id]["profiles_list"].pop()
        await search_love_step1(msg)
    elif user["is_blocked"]:
        await bot.send_message(
            msg.from_user.id,
            'Ваша анкета была заблокирована'
        )


@dp.message_handler(Text('💤'))
async def sleep_main(msg: types.Message):
    user_id = str(msg.from_user.id)
    await menu(msg)


@dp.message_handler(Text('🚀 Показать'))
async def show_like(msg: types.Message):
    user_id = str(msg.from_user.id)
    user = await get_user_by_id(user_id)
    if not user["is_blocked"]:
        dict_of_profiles[user_id]["last_activity"] = int(time.time())
        who_like = dict_of_profiles[str(msg.from_user.id)]["who_like"][-1]
        profile = await get_user_by_id(who_like, Anketa=True)
        await bot.send_photo(
            msg.from_user.id,
            open(f'static/users_photo/{who_like}.jpg', 'rb'),
            profile,
            reply_markup=like_kb()
        )
    elif user["is_blocked"]:
        await bot.send_message(
            msg.from_user.id,
            'Ваша анкета была заблокирована'
        )
    

@dp.message_handler(Text('💜'))
async def like_liked(msg: types.Message):
    user_id = str(msg.from_user.id)
    user = await get_user_by_id(user_id)
    if not user["is_blocked"]:
        dict_of_profiles[user_id]["last_activity"] = int(time.time())
        who_like = dict_of_profiles[str(msg.from_user.id)]["who_like"]
        user = await get_user_by_id(who_like[-1])
        user_like = await get_user_by_id(str(msg.from_user.id))
        who_like_id = dict_of_profiles[str(msg.from_user.id)]["who_like"][-1]
        dict_of_profiles[str(msg.from_user.id)]["who_like"].pop()
        await bot.send_message(
            who_like_id,
            f'У вас взаимная симпатия,\n скорее начинайте общаться: @{user_like["user_name"]}\n\nДавай смотреть анкеты дальше',
            reply_markup=reminder_kb()
        )
        await bot.send_message(
            msg.from_user.id, 
            f'Скорее начинайте общаться: @{user["user_name"]}'
        )
        if len(dict_of_profiles[str(msg.from_user.id)]["who_like"]) != 0:
            await show_like(msg)
        else:
            await bot.send_message(
                msg.from_user.id,
                'На этом все, давай смотреть анкеты дальше',
                reply_markup=reminder_kb()
            )
    elif user["is_blocked"]:
        await bot.send_message(
            msg.from_user.id,
            'Ваша анкета была заблокирована'
        )

@dp.message_handler(Text('👎🏻'))
async def dislike_liked(msg: types.Message):
    user_id = str(msg.from_user.id)
    user = await get_user_by_id(user_id)
    if not user["is_blocked"]:
        dict_of_profiles[user_id]["last_activity"] = int(time.time())
        dict_of_profiles[str(msg.from_user.id)]["who_like"].pop()
        if len(dict_of_profiles[str(msg.from_user.id)]["who_like"]) != 0:
            await show_like(msg)
        else:
            await bot.send_message(
                msg.from_user.id,
                'На этом все, давай смотреть анкеты дальше',
                reply_markup=reminder_kb()
            )
    elif user["is_blocked"]:
        await bot.send_message(
            msg.from_user.id,
            'Ваша анкета была заблокирована'
        )
@dp.message_handler(Text('❗️'))
@dp.message_handler(Text('⚠️'))
async def search_report(msg: types.Message):
    user_id = str(msg.from_user.id)
    dict_of_profiles[user_id]["last_activity"] = int(time.time())
    cached_data[user_id] = msg.text
    await bot.send_message(
        msg.from_user.id, 
        'Укажите причину жалобы:',
        reply_markup=report_kb()
    )

@dp.callback_query_handler(lambda c: 'report' in c.data and c.data != 'report:other')
async def report_callback(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    report = callback_query.data.split(':')[1]
    if cached_data[user_id] == '❗️':
        report_user_id = dict_of_profiles[user_id]["who_like"][-1] 
        dict_of_profiles[user_id]["who_like"].pop()
    elif cached_data[user_id] == '⚠️':      
        report_user_id = dict_of_profiles[user_id]["profiles_list"][-1] 
        dict_of_profiles[user_id]["profiles_list"].pop()
    if report != 'cancel':
        list_of_admins = await get_list_of_admins()
        for admin_id in list_of_admins:
            await bot.send_message(
                admin_id,
                f'На пользователя {report_user_id} была подана жалоба по причине "{report}"'
            )
        await bot.send_message(
            callback_query.from_user.id, 
            'Жалоба успешно отправлена'
        )     
    await search_love_step1(callback_query)

@dp.callback_query_handler(lambda c: c.data == 'report:other')
async def report_callback_other(callback_query: types.CallbackQuery):
    await bot.send_message(
        callback_query.from_user.id,
        'Опишите причину подачи жалобы'
    )
    await ReportUserOther.cause.set()

@dp.message_handler(state=ReportUserOther.cause)
async def report_callback_other_state(msg: types.Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    async with state.proxy() as data:
        data["cause"] = msg.text
    report_user_id = dict_of_profiles[user_id]["profiles_list"][-1] 
    dict_of_profiles[user_id]["profiles_list"].pop()
    list_of_admins = await get_list_of_admins()
    for admin_id in list_of_admins:
        await bot.send_message(
            admin_id,
            f'На пользователя {report_user_id} была подана жалоба по причине "{data["cause"]}"'
        )
        await state.finish()
        await bot.send_message(
            msg.from_user.id, 
            'Жалоба успешно отправлена'
        )  
    await search_love_step1(msg)

    

############################################################################################################################
        
################################### Фильтры ##########################################################################
        
@dp.message_handler(Text('⚙️ Фильтры'))
async def filter(msg: types.Message):
    user_id = str(msg.from_user.id)
    data = await get_user_by_id(user_id)
    university = await get_university_name_by_id(data["to_university"])
    match data["to_education"]:
        case 'spo':
            data["to_education"] = 'СПО'
        case 'bakalavriat':
            data["to_education"] = 'Бакалавриат'
        case 'specialitet':
            data["to_education"] = 'Специалитет'
        case 'magistratura':
            data["to_education"] = 'Магистратура'
        case 'all':
            data["to_education"] = 'Любая'
    await bot.send_message(
        msg.from_user.id,
        f'<b>Ваши фильтры:</b>\n\n\
<i>Учебное заведение</i> - {university}\n\
<i>Форма обучения</i> - {data["to_education"]}\n\
<i>Курс обучения</i> - {"Любой" if data["to_course"] == 0 else data["to_course"]}\n\
<i>Максимальный возраст</i> - {"Любой" if data["max_age"] == 0 else data["max_age"]}\n\
<i>Минимальный возраст</i> - {"Любой" if data["min_age"] == 0 else data["min_age"]}\n\n\
Что вы хотите поменять?' ,
        reply_markup=filters_main_kb(),
        parse_mode='HTML'
    )

@dp.message_handler(Text('🔞 Возр.диапазон'))
async def update_filter_age(msg: types.Message):
    await bot.send_message(
        msg.from_user.id,
        'Введите возраст в формате:\n\n"нижняя граница" - "верхняя граница"\nНапример 18-20\n\nЕсли вы хотите определенный возраст, отправьте просто одно число)',
        reply_markup=filter_cource_age_kb(is_filter_age=True)
    )   
    await Filter_age.age.set()



@dp.message_handler(state=Filter_age.age)
async def state_filter_age(msg: types.Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    age = msg.text
    if age.isdigit():
        if 15 <= int(age) < 100:
            async with state.proxy() as data:
                data['age'] = msg.text
            await update_filter_age_max(user_id, int(data["age"]))
            await update_filter_age_min(user_id, int(data["age"]))
            await state.finish()
            await update_list_of_profiles_with_new_filters(msg)
            await bot.send_message(
                msg.from_user.id,
                'Возраст успешно обновлен!'
            )
            await filter(msg)
        else:
            await bot.send_message(
                msg.from_user.id,
                'Пожалуйста, введите корректный возраст, от 15 лет'
            )
            return
    else:
        try:
            age = age.replace(' ', '')
            split_age = age.split('-')
            min_age = split_age[0]
            max_age = split_age[1]
            if min_age.isdigit() and max_age.isdigit():
                if (15 <= int(min_age) < 100) and (15 <= int(max_age) < 100):
                    async with state.proxy() as data:
                        data['age'] = msg.text
                    await update_filter_age_min(user_id, int(min_age))
                    await update_filter_age_max(user_id, int(max_age))
                    await state.finish()
                    await update_list_of_profiles_with_new_filters(msg)
                    await bot.send_message(
                        msg.from_user.id, 
                        'Возраст успешно обновлен!',
                    )
                    await filter(msg)
                else:
                    await bot.send_message(
                        msg.from_user.id,
                        'Пожалуйста, введите корректный возраст, от 15 лет'
                    )
                    return
            else:
                await bot.send_message(
                    msg.from_user.id,
                    'Вы ввели возраст в неправильно формате, ведите возраст в формате:\n\n"нижняя граница" - "верхняя граница"\nНапример 18-20\n\nЕсли вы хотите определенный возраст, отправьте просто одно число)'
                )
                return
        except Exception as e:
            await bot.send_message(
                    msg.from_user.id,
                    'Вы ввели возраст в неправильно формате, ведите возраст в формате:\n\n"нижняя граница" - "верхняя граница"\nНапример 18-20\n\nЕсли вы хотите определенный возраст, отправьте просто одно число)'
                )
            return


@dp.callback_query_handler(lambda c: c.data == 'filter_age_all', state=Filter_age.age)
async def filter_age_all(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = str(callback_query.from_user.id)
    await state.finish()
    await update_filter_age_max(user_id, 0)
    await update_filter_age_min(user_id, 0)
    await update_list_of_profiles_with_new_filters(callback_query)
    await bot.send_message(
            callback_query.from_user.id, 
            'Возраст успешно обновлен!',
        )
    await filter(callback_query) 

@dp.callback_query_handler(lambda c: c.data == 'filter_age_cancle', state=Filter_age.age)
async def filter_age_cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.send_message(
        callback_query.from_user.id,
        'Действие отменено'
    )
    await filter(callback_query)



@dp.message_handler(Text('👨‍🎓 Уч. заведение'))
async def update_filter_university(msg: types.Message):
    await bot.send_message(
        msg.from_user.id,
        'Выберете учебное заведение)',
        reply_markup=await select_university(is_filter=True)
    )

    await Filter_university.university.set()


@dp.callback_query_handler(lambda c: 'filter_university' in c.data, state=Filter_university.university)
async def state_filter_university(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = str(callback_query.from_user.id)
    university = callback_query.data.split(':')[1]
    await callback_query.message.delete()
    await update_filter_university_db(user_id, university)
    await update_list_of_profiles_with_new_filters(callback_query)
    await bot.send_message(
        callback_query.from_user.id,
        'Учебное заведение успешно обновлено!'
    )
    await state.finish()
    await filter(callback_query)

@dp.message_handler(Text('1️⃣ Курс'))
async def update_filter_course(msg: types.Message):
    await bot.send_message(
        msg.from_user.id,
        'Введите курс обучения!',
        reply_markup=filter_cource_age_kb(),
    )
    await Filter_course.cource.set()

@dp.callback_query_handler(lambda c: c.data == 'filter_cource_cancle', state=Filter_course.cource)
async def filter_age_cancel(callback_query: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await bot.send_message(
        callback_query.from_user.id,
        'Действие отменено'
    )
    await filter(callback_query)

@dp.message_handler(state=Filter_course.cource)
async def state_filter_cource(msg: types.Message, state: FSMContext):
    user_id = str(msg.from_user.id)
    if msg.text.isdigit() and 1 <= int(msg.text) <= 5:
        async with state.proxy() as data:
            data['course'] = msg.text
        await update_filter_cource(user_id, int(data["course"]))
        await state.finish()
        await update_list_of_profiles_with_new_filters(msg)
        await bot.send_message(
            msg.from_user.id,
            'Курс обучения успешно обновлен',
        )
        await filter(msg)
    else:
        await bot.send_message(
                msg.from_user.id, 
                'Пожалуйста, введите корректный номер курса'
            )
        return
    

@dp.callback_query_handler(lambda c: c.data == 'filter_cource_all', state=Filter_course.cource)
async def filter_course_all(callback_query: types.CallbackQuery, state: FSMContext):
    user_id = str(callback_query.from_user.id)
    await state.finish()
    await update_filter_cource(user_id, 0)
    await update_list_of_profiles_with_new_filters(callback_query)
    await bot.send_message(
            callback_query.from_user.id,
            'Курс обучения успешно обновлен',
        )
    await filter(callback_query)



@dp.message_handler(Text('📕 Форма обучения'))
async def update_filter_education(msg: types.Message):
    await bot.send_message(
        msg.from_user.id,
        'Выберете форму обучения',
        reply_markup=select_education(is_filter=True)
    )

@dp.callback_query_handler(lambda c: 'filter_education' in c.data)
async def state_filter_education(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    education = callback_query.data.split(':')[1]
    await update_filter_education_db(user_id, education)
    await update_list_of_profiles_with_new_filters(callback_query)
    await bot.send_message(
        callback_query.from_user.id,
        'Форма обучения успешно обновлена'
    )
    await filter(callback_query)
    



#########################################################################################################################

##################################### Панель администратора ####################################################
    

@dp.message_handler(commands='admin')
async def login_admin(msg: types.Message):
    user_id = str(msg.from_user.id)
    list_of_admins = await get_list_of_admins()
    if user_id in list_of_admins:
        await bot.send_message(
            msg.from_user.id, 
            'Ты попал в админ панель, вот список команд:\n\
"/block_user"\n\
"/get_user_by_id"\n\
"/unblock_user"\n\
"/get_statistic"\n\
"/spam"\n\
"/get_user_by_photo"\n\
"/send_message_from_user_by_id"\n\
"/add_admin"\n\
"/delete_admin"\n\
"/get_backups"\n\
"/add_university"\n\
"/delete_university"'
        )


@dp.message_handler(commands='get_backups')
async def admin_get_backups(msg: types.Message):
    user_id = str(msg.from_user.id)
    list_of_admins = await get_list_of_admins()
    if user_id in list_of_admins:
        with open('static/backups/database.sql', 'rb') as file:
            await bot.send_document(msg.from_user.id, document=file)
        with open('static/backups/dump.json', 'rb') as file:
            await bot.send_document(msg.from_user.id, document=file)


@dp.message_handler(commands='add_admin')
async def admin_add_admin(msg: types.Message):
    user_id = str(msg.from_user.id)
    if user_id == main_admin:
        await AdminAddAdmin.user_id.set()
        await bot.send_message(
            msg.from_user.id,
            'Введите id пользователя'
        )

@dp.message_handler(state=AdminAddAdmin.user_id)
async def state_admin_add_admin(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["user_id"] = msg.text
    await add_admin_db(user_id=data["user_id"])
    await bot.send_message(
        msg.from_user.id,
        'Админ успешно добавлен'
    )
    await state.finish()


@dp.message_handler(commands='delete_admin')
async def admin_delete_admin(msg: types.Message):
    user_id = str(msg.from_user.id)
    list_of_admins = await get_list_of_admins()
    if user_id in list_of_admins:
        if user_id == main_admin:
            await AdminDeleteAdmin.user_id.set()
            await bot.send_message(
                msg.from_user.id,
                'Введите id пользователя'
            )

@dp.message_handler(state=AdminDeleteAdmin.user_id)
async def state_admin_delete_admin(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["user_id"] = msg.text
    await delete_admin_db(user_id=data["user_id"])
    await bot.send_message(
        msg.from_user.id,
        'Админ успешно удален'
    )
    await state.finish()



@dp.message_handler(commands='send_message_from_user_by_id')
async def admin_send_message_from_user_by_id(msg: types.Message):
    user_id = str(msg.from_user.id)
    list_of_admins = await get_list_of_admins()
    if user_id in list_of_admins:
        await AdminSendMessageFromUserById.user_id.set()
        await bot.send_message(
            msg.from_user.id,
            'Введите user_id пользователя, которому хотите отправить сообщение'
        )

@dp.message_handler(state=AdminSendMessageFromUserById.user_id)
async def state_admin_send_message_from_user_by_id_step1(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["user_id"] = msg.text
    await bot.send_message(
        msg.from_user.id,
        'Введите сообщение, которое хотите отправить пользователю'
    )
    await AdminSendMessageFromUserById.next()

@dp.message_handler(state=AdminSendMessageFromUserById.message)
async def state_admin_send_message_from_user_by_id_step2(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["message"] = msg.text
    await bot.send_message(
        msg.from_user.id,
        'Подтвердите действие "Да/Нет"'
    )
    await AdminSendMessageFromUserById.next()

@dp.message_handler(state=AdminSendMessageFromUserById.confirmation)
async def state_admin_send_message_from_user_by_id_step3(msg: types.Message, state: FSMContext):
    if msg.text.lower() == 'да':
        try:
            async with state.proxy() as data:
                data["confirmation"] = msg.text
            await bot.send_message(
                int(data["user_id"]),
                data["message"],
                reply_markup=reminder_kb()
            )
            await bot.send_message(
                msg.from_user.id,
                'Сообщение успешно отправлено'
            )
        except Exception as e:
            await state.finish()
            await bot.send_message(
                msg.from_user.id,
                'Что-то пошло не так'
            )   
        await state.finish()
    elif msg.text.lower() == 'нет':
        async with state.proxy() as data:
            data["confirmation"] = msg.text
        await state.finish()
        await bot.send_message(
            msg.from_user.id,
            'Действие отменено'
        )
    else:
        await bot.send_message(
            msg.from_user.id,
            'Нет такого варианта ответа, введите "Да/Нет"'
        )
        return



@dp.message_handler(commands=['block_user'])
async def admin_block_user(msg: types.Message):
    user_id = str(msg.from_user.id)
    list_of_admins = await get_list_of_admins()
    if user_id in list_of_admins:
        await AdminBlockUser.user_id.set()
        await bot.send_message(
            msg.from_user.id, 
            'Введите id пользователя, которого хотите заблокировать.\nЕсли вы хотите отменить действие, введите "Отмена"'
        )

@dp.message_handler(state=AdminBlockUser.user_id)
async def state_admin_block_user_step1(msg: types.Message, state: FSMContext):
    if msg.text.lower() != 'отмена':
        async with state.proxy() as data:
            data["user_id"] = msg.text
        await bot.send_message(
            msg.from_user.id, 
            'Введите причину блокировки, если вы хотите отменить действие, введите "отмена"'
        )
        await AdminBlockUser.next()
    else:
        await state.finish()
        await bot.send_message(
            msg.from_user.id,
            'Действие отменено'
        )
        
@dp.message_handler(state=AdminBlockUser.cause)
async def state_admin_block_user_step2(msg: types.Message, state: FSMContext):
    if msg.text.lower() != 'отмена':
            async with state.proxy() as data:
                data["cause"] = msg.text
            await AdminBlockUser.next()
            await bot.send_message(
                msg.from_user.id,
                'Подтвердите действие, введите "Да/Нет"'
            )
    else:
        await state.finish()
        await bot.send_message(
            msg.from_user.id,
            'Действие отменено'
        )

@dp.message_handler(state=AdminBlockUser.confirmation)
async def state_admin_block_user_step3(msg: types.Message, state: FSMContext):
    if msg.text.lower() == 'да':
        async with state.proxy() as data:
            data["confirmation"] = msg.text
        block = await block_user_db(data["user_id"])
        if block:
            await bot.send_message(
                msg.from_user.id, 
                f'Пользователь {data["user_id"]} успешно заблокирован'
            )
            blocked_user = await get_user_by_id(data["user_id"])
            del dict_of_profiles[data["user_id"]]
            await bot.send_message(
                data["user_id"],
                f'Привет, {blocked_user["name"]}, вы были заблокированы по причине:\n\n"{data["cause"]}"\n\nВы можете обратиться в поддержку и оспорить решение: @sliv_kursov_admin'
            )
        elif not block:
            await bot.send_message(
                msg.from_user.id, 
                'Произошла ошибка, скорее всего пользователя с таким id не существует'
            )
    elif msg.text.lower() == 'нет':
        await bot.send_message(
            msg.from_user.id, 
            'Действие отменено'
        )
    else:
        await bot.send_message(
            msg.from_user.id, 
            'Нет такого варианта ответа, введите "Да/Нет"'
        )
        return 
    await state.finish()


@dp.message_handler(commands=['unblock_user'])
async def admin_unblock_user(msg: types.Message):
    user_id = str(msg.from_user.id)
    list_of_admins = await get_list_of_admins()
    if user_id in list_of_admins:
        await AdminUnblockUser.user_id.set()
        await bot.send_message(
            msg.from_user.id, 
            'Введите id пользователя, которого хотите разблокировать.\nЕсли вы хотите отменить действие, введите "Отмена"'
        )

@dp.message_handler(state=AdminUnblockUser.user_id)
async def state_admin_unblock_user_step1(msg: types.Message, state: FSMContext):
    if msg.text.lower() != 'отмена':
        async with state.proxy() as data:
            data["user_id"] = msg.text
        await bot.send_message(
            msg.from_user.id, 
            'Подтвердите действие, введите "Да/Нет"'
        )
        await AdminUnblockUser.next()
    else:
        await state.finish()
        await bot.send_message(
            msg.from_user.id,
            'Действие отменено'
        )

@dp.message_handler(state=AdminUnblockUser.confirmation)
async def state_admin_unblock_user_step2(msg: types.Message, state: FSMContext):
    if msg.text.lower() == 'да':
        async with state.proxy() as data:
            data["confirmation"] = msg.text
        unblock = await unblock_user_db(data["user_id"])
        if unblock:
            await bot.send_message(
                msg.from_user.id,
                f'Пользователь {data["user_id"]} успешно разблокирован'
            )
            unblocked_user = await get_user_by_id(data["user_id"])
            await bot.send_message(
                data["user_id"],
                f'Привет, {unblocked_user["name"]}, ваша анкета раблокированна!\n\nВведите "/menu" для продолжения.'
            )


        elif not unblock:
            await bot.send_message(
                msg.from_user.id, 
                'Произошла ошибка, скорее всего пользователя с таким id не существует'
            )
    elif msg.text.lower() == 'нет':
        await state.finish()
        await bot.send_message(
            msg.from_user.id, 
            'Действие отменено'
        )
    else:
        await bot.send_message(
            msg.from_user.id, 
            'Нет такого варианта ответа, введите "Да/Нет"'
        )
        return 
    await state.finish()

            

@dp.message_handler(commands=['get_user_by_id'])
async def admin_state_get_user_by_id(msg: types.Message):
    user_id = str(msg.from_user.id)
    list_of_admins = await get_list_of_admins()
    if user_id in list_of_admins:
        await bot.send_message(
            msg.from_user.id,
            'Введите id пользователя'
        )
        await AdminGetUserById.user_id.set()

@dp.message_handler(state=AdminGetUserById.user_id)
async def state_admin_get_user_by_id(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["user_id"] = msg.text
    user_with_anket = await get_user_by_id(data["user_id"], Anketa=True)
    user_data = await get_user_by_id(data["user_id"])
    if user_data != 'User not found' and user_data != 'Error':
        await bot.send_photo(
            msg.from_user.id,
            open(f'static/users_photo/{data["user_id"]}.jpg', 'rb'),
            user_with_anket,
        )
        await bot.send_message(
            msg.from_user.id,
            user_data,
        )
    else:
        await bot.send_message(
            msg.from_user.id,
            'Пользователь не найден'
        )
    await state.finish()

@dp.message_handler(commands=['get_statistic'])
async def admin_get_user_by_admin(msg: types.Message):
    user_id = str(msg.from_user.id)
    list_of_admins = await get_list_of_admins()
    if user_id in list_of_admins:
        users, count = await get_statistic_user_db()
        await bot.send_message(
            msg.from_user.id,
            f'Всего пользователей: {users}\nАктивных пользователей: {count}'
        )


@dp.message_handler(commands=['spam'])
async def admin_spam(msg: types.Message):
    user_id = str(msg.from_user.id)
    list_of_admins = await get_list_of_admins()
    if user_id in list_of_admins:
        await AdminSpamHasPhoto.has_photo.set()
        await bot.send_message(
            msg.from_user.id,
            'Рассылка будет с фото?("Да/Нет")'
        )

@dp.message_handler(state=AdminSpamHasPhoto.has_photo)
async def state_admin_spam_step1(msg: types.Message, state: FSMContext):
    if msg.text.lower() == 'да' or msg.text.lower() == 'нет':
        async with state.proxy() as data:
            data["has_photo"] = msg.text
        await state.finish()
    else:
        await bot.send_message(
            msg.from_user.id,
            'Нет такого варианта ответа'
        )
        return
    if data["has_photo"].lower() == 'да':
        await bot.send_message(
            msg.from_user.id,
            'Отправьте фотографию'
        )
        await AdminSpamWithPhoto.path.set()
    elif data["has_photo"].lower() == 'нет':
        await bot.send_message(
            msg.from_user.id,
            'Введите текст рассылки'
        )
        await AdminSpamOnlyText.spam_text.set()


######## Спам с фото ########
@dp.message_handler(content_types=['photo'], state=AdminSpamWithPhoto)
async def state_admin_spam_with_photo_step1(msg: types.Message, state: FSMContext):
    try:
        file_name = 'spam.jpg'
        path = f'static/spam_photo/{file_name}'
        async with state.proxy() as data:
                data['path'] = path
        await msg.photo[-1].download(path)
        await bot.send_message(
            msg.from_user.id, 
            'Фотография успешно добавлена, введите текст рассылки'
            )
        await AdminSpamWithPhoto.next()
    except Exception as e:
        await bot.send_message(
            msg.from_user.id, 
            'Произошла ошибка, попробуйте отправить фотографию еще раз...'
        )
        return

@dp.message_handler(state=AdminSpamWithPhoto.spam_text)
async def state_admin_spam_with_photo_step2(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["spam_text"] = msg.text
    await bot.send_message(
        msg.from_user.id, 
        'Рассылка будет выглядеть вот так:'
    )
    await bot.send_photo(
        msg.from_user.id,
        open(data["path"], 'rb'),
        data["spam_text"]
    )
    await bot.send_message(
        msg.from_user.id,
        'Подтвердите действие для начала рассылки "Да/Нет"'
    )
    
    await AdminSpamWithPhoto.next()

@dp.message_handler(state=AdminSpamWithPhoto.confirmation)
async def state_admin_spam_with_photo_step2(msg: types.Message, state: FSMContext):
    if msg.text.lower() == 'да':
        async with state.proxy() as data:
            data["confirmation"] = msg.text
        list_of_users = await get_list_of_users_for_spam_db()
        count = 0
        for user in list_of_users:
            try:
                await bot.send_photo(
                    user,
                    open(data["path"], 'rb'),
                    data["spam_text"],
                    reply_markup=reminder_kb()
                )
                count+=1
            except:
                pass
        await state.finish()
        await bot.send_message(
            msg.from_user.id, 
            f'Рассылка успешно отправлена {count} пользователям!'
        )
    elif msg.text.lower() == 'нет':
        await state.finish()
        await bot.send_message(
            msg.from_user.id,
            'Рассылка отменена'
        )
    else:
        await bot.send_message(
            msg.from_user.id,
            'Нет такого варианта ответа, введите "Да/Нет"'
        )
        return

########################

######## Спам без фото ########

@dp.message_handler(state=AdminSpamOnlyText.spam_text)
async def state_admin_spam_only_text_step1(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["spam_text"] = msg.text
    await bot.send_message(
        msg.from_user.id,
        'Рассылка будет выглядеть вот так:'
    )
    await bot.send_message(
        msg.from_user.id,
        data["spam_text"]
    )
    await bot.send_message(
        msg.from_user.id,
        'Подтвердите действие для начала рассылки "Да/Нет"'
    )
    await AdminSpamOnlyText.next()

@dp.message_handler(state=AdminSpamOnlyText.confirmation)
async def state_admin_spam_only_text_step2(msg: types.Message, state: FSMContext):
    if msg.text.lower() == 'да':
        async with state.proxy() as data:
            data["confirmation"] = msg.text
        list_of_users = await get_list_of_users_for_spam_db()
        count = 0
        for user in list_of_users:
            try:
                await bot.send_message(
                    user,
                    data["spam_text"],
                    reply_markup=reminder_kb()
                )
                count+=1
            except:
                pass
        await state.finish()
        await bot.send_message(
            msg.from_user.id, 
            f'Рассылка успешно отправлена {count} пользователям!'
        )
    elif msg.text.lower() == 'нет':
        await state.finish()
        await bot.send_message(
            msg.from_user.id,
            'Рассылка отменена'
        )
    else:
        await bot.send_message(
            msg.from_user.id,
            'Нет такого варианта ответа, введите "Да/Нет"'
        )
        return

########################

######## Поиск по фото ########
@dp.message_handler(commands=['get_user_by_photo'])
async def admin_get_user_by_photo(msg: types.Message):
    user_id = str(msg.from_user.id)
    list_of_admins = await get_list_of_admins()
    if user_id in list_of_admins:
        await bot.send_message(
            msg.from_user.id,
            'Отправьте фотографию'
        )
        await AdminGetUserByPhoto.path.set()
    
@dp.message_handler(content_types=['photo'], state=AdminGetUserByPhoto.path)
async def state_admin_get_user_by_photo(msg: types.Message, state: FSMContext):
    try:
        file_name = 'search.jpg'
        path = f'static/utils_data/{file_name}'
        async with state.proxy() as data:
                data['path'] = path
        await msg.photo[-1].download(path)
        rezult, user = await compare_images(path)
        if user is not None:
            await bot.send_message(
                msg.from_user.id,
                rezult
            )
            anketa = await get_user_by_id(user, Anketa=True)
            await bot.send_photo(
                msg.from_user.id,
                open(f'static/users_photo/{user}.jpg', 'rb'),
                anketa
            )    
        else:
            await bot.send_message(
                msg.from_user.id,
                rezult
            )
        await state.finish()
    except Exception as e:
        await bot.send_message(
            msg.from_user.id, 
            'Произошла ошибка, попробуйте отправить фотографию еще раз...'
        )
        return

@dp.message_handler(commands='add_university')
async def admin_add_university(msg: types.Message):
    user_id = str(msg.from_user.id)
    list_of_admins = await get_list_of_admins()
    if user_id in list_of_admins:
        await bot.send_message(
            msg.from_user.id,
            'Введите название университета'
        )
        await AdminAddUniversity.name.set()

@dp.message_handler(state=AdminAddUniversity.name)
async def state_admin_add_university_step1(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = msg.text
    await bot.send_message(
        msg.from_user.id,
        'Подтвердите действие "Да/Нет"'
    )
    await AdminAddUniversity.next()

@dp.message_handler(state=AdminAddUniversity.confirmation)
async def state_admin_add_university_step2(msg: types.Message, state: FSMContext):
    if msg.text.lower() == 'да':
        async with state.proxy() as data:
            data["confirmation"] = msg.text
        add = await add_university_db(data["name"])
        if add:
            await bot.send_message(
                msg.from_user.id,
                'Университет успешно добавлен!'
            )
        else:
            await bot.send_message(
                msg.from_user.id,
                'Что-то пошло не так'
            )
        await state.finish()
    elif msg.text.lower() == 'нет':
        async with state.proxy() as data:
            data["confirmation"] = msg.text
        await state.finish()
        await bot.send_message(
            msg.from_user.id,
            'Действие отменено'
        )
    else:
        await bot.send_message(
            msg.from_user.id,
            'Нет такого варианта ответа, введите "Да/Нет"'
        )
        return



@dp.message_handler(commands='delete_university')
async def admin_add_university(msg: types.Message):
    user_id = str(msg.from_user.id)
    list_of_admins = await get_list_of_admins()
    if user_id in list_of_admins:
        await bot.send_message(
            msg.from_user.id,
            'Введите название университета'
        )
        await AdminDeleteUniversity.name.set()

@dp.message_handler(state=AdminDeleteUniversity.name)
async def state_admin_add_university_step1(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = msg.text
    await bot.send_message(
        msg.from_user.id,
        'Подтвердите действие "Да/Нет"'
    )
    await AdminDeleteUniversity.next()

@dp.message_handler(state=AdminDeleteUniversity.confirmation)
async def state_admin_add_university_step2(msg: types.Message, state: FSMContext):
    if msg.text.lower() == 'да':
        async with state.proxy() as data:
            data["confirmation"] = msg.text
        add = await delete_university_db(data["name"])
        if add:
            await bot.send_message(
                msg.from_user.id,
                'Университет успешно удален!'
            )
        else:
            await bot.send_message(
                msg.from_user.id,
                'Что-то пошло не так'
            )
        await state.finish()
    elif msg.text.lower == 'нет':
        async with state.proxy() as data:
            data["confirmation"] = msg.text
        await state.finish()
        await bot.send_message(
            msg.from_user.id,
            'Действие отменено'
        )
    else:
        await bot.send_message(
            msg.from_user.id,
            'Нет такого варианта ответа, введите "Да/Нет"'
        )
        return

# @dp.message_handler(commands='1357')
# async def save_data(msg: types.Message):
#     if await dump_dict(dict_of_profiles):
#         await bot.send_message(
#             msg.from_user.id,
#             'Данные схранены'
#         )
#     else:
#         await bot.send_message(
#             msg.from_user.id,
#             'Данные не схранены'
#         )


def load_data():
    global dict_of_profiles
    try:
        with open('static/backups/dump.json', 'r') as file:
            dict_of_profiles = json.loads(file.read())
        logging.info('Успешная запись данных из dump в dict_of_profiles')
    except:
        logging.error('Ошибка записи данных из dump в dict_of_profiles')


# async def reminder():
#     global dict_of_profiles
#     for user in dict_of_profiles:
#         data = await get_user_by_id(user)
#         if not(data["is_blocked"]) and data["is_active"]:
#             if int(time.time()) - dict_of_profiles[user]['last_activity'] > 180:
#                 dict_of_profiles[user]['last_activity'] = int(time.time())
#                 await bot.send_message(
#                     int(user),
#                     'От вас давно не было никакой активности',
#                     reply_markup=reminder_kb()
#                 )
        

if __name__ == '__main__':
    start_db()
    load_data()
    scheduler = AsyncIOScheduler()
    logging.getLogger().setLevel(logging.INFO)

    # Настройка обработчика для info-сообщений
    info_handler = logging.FileHandler('utils/main_info.log')
    info_handler.setLevel(logging.INFO)
    info_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

    # Настройка обработчика для error-сообщений
    error_handler = logging.FileHandler('utils/main_errors.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))

    # Добавление обработчиков к глобальному логгеру
    logging.getLogger().addHandler(info_handler)
    logging.getLogger().addHandler(error_handler)

    # Запуск потока для бэкапов
    thread_backup_dict_of_profiles = threading.Thread(target=start_schedule, daemon=True, args=(scheduler, dict_of_profiles, bot))
    thread_backup_dict_of_profiles.start()
    scheduler.start()
    # Запуск бота
    executor.start_polling(dp, skip_updates=True)






    

    





