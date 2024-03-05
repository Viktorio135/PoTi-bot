import json
from datetime import datetime

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
    change_age_by_id, get_list_of_admins, block_user_db
)
from keyboards import (
    select_sex, select_university, select_education, 
    end_registration_kb, menu_kb, reg_menu,
    my_profile_kb, select_search, search_kb,
    show_like_kb, like_kb, filters_main_kb,
    filter_cource_age_kb, history_dislike_kb, report_kb, 
    change_profile_kb
)
from dataBase.dump import dump_dict
from dataBase.models import start_db
from states.user_states import (
    Register_new_user, Filter_age, Filter_university, 
    Filter_course, Change_age, Change_description, 
    Change_photo
)

from states.admin_states import (
    AdminDeleteUser
)



bot = Bot(token='6874586651:AAFeVAJ4fOIR_z2uWcG1Og5kaWOhkNCH3U0')
dp = Dispatcher(bot, storage=MemoryStorage())

cached_data = {}

dict_of_profiles = {}

@dp.message_handler(commands='start')
async def cmd_start(msg: types.Message):
    await bot.send_message(
            msg.from_user.id, 
            'Привет, ты попал в ... Мы поможем тебе найти кого-нибудь найти.'
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
   
    if msg.text.isdigit() and 15 <= int(msg.text) < 100:
            async with state.proxy() as data:
                data['age'] = msg.text

            await bot.send_message(
                msg.from_user.id, 
                'Хорошо, теперь придумая описание профиля'
                )

            await Register_new_user.next()
    else:
        await bot.send_message(
                msg.from_user.id, 
                'Пожалуйста, введите корректный возраст, от 15 лет'
            )
        return
    
@dp.message_handler(state=Register_new_user.description)
async def register_description(msg: types.Message, state: FSMContext):
    async with state.proxy() as data:
                data['description'] = '' if msg.text == '0' else msg.text
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
                'И напоследок, Пришлите мне вашу фотографию!'
                )

            await Register_new_user.next()
    else:
        await bot.send_message(
                msg.from_user.id, 
                'Пожалуйста, введите корректный номер курса'
            )
        return


@dp.message_handler(content_types=['photo'], state=Register_new_user.photos)
async def register_description(msg: types.Message, state: FSMContext):
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
        
        await end_registration(msg, data)
        await state.finish()
    except Exception as error:    
        await bot.send_message(
            msg.from_user.id, 
            'Произошла ошибка сохранения, попробуйте снова'
            )
        return
    
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
                'Ваш профиль успешно создан!',
                reply_markup=reg_menu()
            )
            
        else:
            await bot.send_message(
                callback_query.from_user.id, 
                'Ошибка базы данных!!'
            )

    except Exception as e:
            print(e)
            await bot.send_message(
                 callback_query.from_user.id,
                 'Что-то пошло не так, давай попробуем снова('
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
                f'{user["name"]}, ты попал в главное меню, выбери действие;)',
                reply_markup=menu_kb()
            )
        else: 
            await bot.send_message(
                msg.from_user.id,
                f'Ошибка базы данных',
            )
             
    except Exception as e:
        await bot.send_message(
                msg.from_user.id,
                f'Ошибка базы данных: {e}',
            )
        

############# Анкета #############


@dp.message_handler(Text('👤 Моя анекта'))
async def my_profile(msg: types.Message):
     
    await bot.send_message(
          msg.from_user.id,
          'Ваша анкета выглядит вот так:'
    )

    user = await get_user_by_id(msg.from_user.id, Anketa=True)

    if user != 'User not found':
        await bot.send_photo(
            msg.from_user.id, 
            open(f'static/users_photo/{msg.from_user.id}.jpg', 'rb'),
            user,
            reply_markup=my_profile_kb()
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
                'Отправьте фотографию'
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
            'Фотография успешно добавлена'
            )
        await my_profile(msg)
    except Exception as e:
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
    await update_active_to_false(user_id)
    for user in dict_of_profiles.copy():
        if user_id in user["profiles_list"]:
            user["profiles_list"].remove(user_id)
    await bot.send_message(
        callback_query.from_user.id,
        'Мы отключили вашу анкету, надеюсь вы кого-нибудь нашли)'
    )

@dp.message_handler(Text('Последняя активность'))
async def last_activity(msg: types.Message, page=0):
    user_id = str(msg.from_user.id)
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

@dp.callback_query_handler(lambda c: 'history_like' in c.data)
async def like_history_dislike(callback_query: types.CallbackQuery):
    page = callback_query.data.split(':')[1]
    print('заход')
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
        'Сердечко успешно отправлено)))',
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
                "last_activity": str(datetime.now()),
                "like": [],
                "history_dislike": [],
                "who_like": [],
            }
        
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
                    'Пользователи не найдены'
                )
        else:
            await search_love_step1(msg)

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
                "last_activity": str(datetime.now()),
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
            'Пользователи не найдены',
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
        'Сердечко успешно отправлено)))',
    )

    await search_love_step1(msg)

@dp.message_handler(Text('👎'))
async def dislike_main(msg: types.Message):
    user_id = str(msg.from_user.id)
    if len(dict_of_profiles[user_id]["history_dislike"]) == 5:
        dict_of_profiles[user_id]["history_dislike"].pop(0)
    if dict_of_profiles[user_id]["profiles_list"][-1] not in dict_of_profiles[user_id]["history_dislike"]:
        dict_of_profiles[user_id]["history_dislike"].append(dict_of_profiles[user_id]["profiles_list"][-1])
    dict_of_profiles[user_id]["profiles_list"].pop()
    await search_love_step1(msg)


@dp.message_handler(Text('💤'))
async def sleep_main(msg: types.Message):
    await menu(msg)


@dp.message_handler(Text('🚀 Показать'))
async def show_like(msg: types.Message):
    who_like = dict_of_profiles[str(msg.from_user.id)]["who_like"][-1]
    profile = await get_user_by_id(who_like, Anketa=True)
    await bot.send_photo(
        msg.from_user.id,
        open(f'static/users_photo/{who_like}.jpg', 'rb'),
        profile,
        reply_markup=like_kb()
    )

@dp.message_handler(Text('💜'))
async def like_liked(msg: types.Message):
    who_like = dict_of_profiles[str(msg.from_user.id)]["who_like"]
    user = await get_user_by_id(who_like[-1])
    user_like = await get_user_by_id(str(msg.from_user.id))
    who_like_id = dict_of_profiles[str(msg.from_user.id)]["who_like"][-1]
    dict_of_profiles[str(msg.from_user.id)]["who_like"].pop()
    await bot.send_message(
        who_like_id,
        f'У вас взаимная симпатия,\n Надеюсь что-то у вас выйдет()()()(): @{user_like["user_name"]} '
    )
    await bot.send_message(
        msg.from_user.id, 
        f'Надеюсь что-то у вас выйдет()()()(): @{user["user_name"]}'
    )
    if len(dict_of_profiles[str(msg.from_user.id)]["who_like"]) != 0:
        await show_like(msg)
    else:
        await bot.send_message(
            msg.from_user.id,
            'Вы вернулись к просмотрю анкет)'
        )
    await search_love_step1(msg)

@dp.message_handler(Text('👎🏻'))
async def dislike_liked(msg: types.Message):
    dict_of_profiles[str(msg.from_user.id)]["who_like"].pop()
    if len(dict_of_profiles[str(msg.from_user.id)]["who_like"]) != 0:
        await show_like(msg)
    else:
        await bot.send_message(
            msg.from_user.id,
            'Вы вернулись к просмотрю анкет)'
        )
        await search_love_step1(msg)


@dp.message_handler(Text('⚠️'))
async def search_report(msg: types.Message):
    await bot.send_message(
        msg.from_user.id, 
        'Укажите причину жалобы:',
        reply_markup=report_kb()
    )

@dp.callback_query_handler(lambda c: 'report' in c.data)
async def report_callback(callback_query: types.CallbackQuery):
    user_id = str(callback_query.from_user.id)
    report = callback_query.data.split(':')[1]
    report_user_id = dict_of_profiles[user_id]["profiles_list"][-1] 
    if report != 'cancel':
        dict_of_profiles[user_id]["profiles_list"].pop()
        match report:
            case 'adults':
                #жалоба с номером id админу
                pass
            case 'drugs':
                #жалоба с номером id админу
                pass
            case 'scum':
                #жалоба с номером id админу
                pass
            case 'other':
                #жалоба с номером id админу
                pass
        await bot.send_message(
            callback_query.from_user.id, 
            'Жалоба успешно отправлена'
        )     
    await search_love_step1(callback_query)

            



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
        f'Ваши фильтры:\n\n\
Учебное заведение - {university}\n\
Форма обучения - {data["to_education"]}\n\
Курс обучения - {"Любой" if data["to_course"] == 0 else data["to_course"]}\n\
Максимальный возраст - {"Любой" if data["max_age"] == 0 else data["max_age"]}\n\
Минимальный возраст - {"Любой" if data["min_age"] == 0 else data["min_age"]}\n\n\
Что вы хотите поменять?' ,
        reply_markup=filters_main_kb()
    )

@dp.message_handler(Text('Возраст'))
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
            print(e)
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



@dp.message_handler(Text('Уч. заведение'))
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

@dp.message_handler(Text('Курс'))
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



@dp.message_handler(Text('Форма обучения'))
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
"/check_user"\n\
"/unblock_user"\n\
"/get_active_users"\n\
"/total_users\n\
"/spam"\n\
"/get_user_by_photo"\n\
'
        )


@dp.message_handler(commands=['block_user'])
async def admin_block_user(msg: types.Message):
    user_id = str(msg.from_user.id)
    list_of_admins = await get_list_of_admins()
    if user_id in list_of_admins:
        await AdminDeleteUser.user_id.set()
        await bot.send_message(
            msg.from_user.id, 
            'Введите id пользователя, которого хотите заблокировать.\nЕсли вы хотите отменить действие, введите "Отмена"'
        )

@dp.message_handler(state=AdminDeleteUser.user_id)
async def state_admin_block_user_step1(msg: types.Message, state: FSMContext):
    if msg.text.lower() != 'отмена':
        async with state.proxy() as data:
            data["user_id"] = msg.text
        await bot.send_message(
            msg.from_user.id, 
            'Введите причину блокировки, если вы хотите отменить действие, введите "отмена"'
        )
        await AdminDeleteUser.next()
    else:
        await state.finish()
        await bot.send_message(
            msg.from_user.id,
            'Действие отменено'
        )
        
@dp.message_handler(state=AdminDeleteUser.cause)
async def state_admin_block_user_step2(msg: types.Message, state: FSMContext):
    print('заход')
    if msg.text.lower() != 'отмена':
            async with state.proxy() as data:
                data["cause"] = msg.text
            await AdminDeleteUser.next()
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

@dp.message_handler(state=AdminDeleteUser.confirmation)
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
            await bot.send_message(
                data["user_id"],
                f'Вы были заблокированы по причине:\n"{data["cause"]}"\nВы можете обратиться в поддержку и оспорить решение: @sliv_kursov_admin'
            )
        elif not block:
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










@dp.message_handler(commands='1357')
async def save_data(msg: types.Message):
    if await dump_dict(dict_of_profiles):
        await bot.send_message(
            msg.from_user.id,
            'Данные схранены'
        )
    else:
        await bot.send_message(
            msg.from_user.id,
            'Данные не схранены'
        )

@dp.message_handler(commands='2468')
async def load_data(msg: types.Message):
    global dict_of_profiles
    try:
        with open('static/load_data/dump.json', 'r') as file:
            dict_of_profiles = json.loads(file.read())
        await bot.send_message(
            msg.from_user.id,
            'Данные схранены'
        )
    except:
        await bot.send_message(
            msg.from_user.id,
            'Данные не схранены'
        )

if __name__ == '__main__':
    start_db()
    executor.start_polling(dp, skip_updates=True)








    

    





