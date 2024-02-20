import json
from datetime import datetime

from dataBase.db_commands import (
    create_user, 
    has_register, 
    get_university_id_by_name, 
    get_university_name_by_id,
    get_user_by_id,
    delete_profile, 
    get_list_of_profiles,
    update_active
)
from keyboards import (
    select_sex, 
    select_university, 
    select_education, 
    end_registration_kb, 
    menu_kb,
    reg_menu,
    my_profile_kb,
    select_search,
    search_kb,
    show_like_kb,
    like_kb
    
)
from dataBase.dump import dump_dict
from dataBase.models import start_db
from states.user_states import Register_new_user


from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage


bot = Bot(token='6874586651:AAFeVAJ4fOIR_z2uWcG1Og5kaWOhkNCH3U0')
dp = Dispatcher(bot, storage=MemoryStorage())

cached_data = {}

dict_of_profiles = {}

@dp.message_handler(commands='start')
async def cmd_start(msg: types.Message):
    await bot.send_message(
            msg.from_user.id, 
            'Привет, ты попал в ... Мы поможем тебе кого-нибудь найти.'
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
                'Для начала, давай создадим аккаунт!\nКак тебя зовут?'
                )
        await Register_new_user.name.set()
    else:
        await bot.send_message(
                msg.from_user.id, 
                'Давай создадим анкету заново.\nКак тебя зовут?'
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
                'Хорошо, теперь придумая описание профиля, если хочешь, чтобы описание было пустым, отправь просто 0'
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
                data['description'] = msg.text
    await bot.send_message(
        msg.from_user.id, 
        'Отлично, давай теперь определимся с учебным заведением!',
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
         'На каком курсе ты учишься?'
    )
    await Register_new_user.next()

@dp.message_handler(state=Register_new_user.course)
async def register_course(msg: types.Message, state: FSMContext):
    if msg.text.isdigit() and 1 <= int(msg.text) <= 5:
            async with state.proxy() as data:
                data['course'] = msg.text

            await bot.send_message(
                msg.from_user.id, 
                'Отправь одну фотографию!'
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
        print(error)
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

@dp.message_handler(Text('Главное меню'))
@dp.message_handler(commands='menu')
async def menu(msg: types.Message):
    try:
        user = await get_user_by_id(str(msg.from_user.id))
        
        if user != 'Error' and user != 'User not found':
            await bot.send_message(
                msg.from_user.id,
                f'Привет, {user["name"]}, ты попал в главное меню, выбери действие;)',
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
        
@dp.message_handler(Text('Моя анкета'))
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

########################################################################################
    
################################### Смотреть анкеты ######################################
    
@dp.message_handler(Text('Cмотреть анкеты'))
async def search_love_reg(msg: types.Message):
    user_id = str(msg.from_user.id)
    if user_id not in dict_of_profiles:
        list_of_profiles = await get_list_of_profiles(user_id)
        dict_of_profiles[user_id] = {
                "profiles_list": list_of_profiles,
                "last_activity": str(datetime.now()),
                "like": [],
                "dislike": [],
                "who_like": [],
            }
        print(dict_of_profiles[user_id])
        await search_love_step1(msg)
    else:
        if len(dict_of_profiles[user_id]["profiles_list"]) == 0:
            list_of_profiles = await get_list_of_profiles(user_id)
            if len(list_of_profiles) != 0:
                dict_of_profiles[user_id]["profiles_list"] = list_of_profiles
                await search_love_step1(msg)
            else:
                await bot.send_message(
                    msg.from_user.id,
                    'Пользователи не найдены'
                )

    

        

    
         
async def search_love_step1(msg: types.Message):
    user_id = str(msg.from_user.id)
    list_of_profiles = dict_of_profiles[user_id]["profiles_list"]

    if list_of_profiles == 'Пользователи не найдены':
        await bot.send_message(
            msg.from_user.id,
            'Пользователи не найдены'
        )
        
    else:
        if len(list_of_profiles) != 0:
            next_profile_id = list_of_profiles[-1]
            next_profile = await get_user_by_id(next_profile_id, Anketa=True)
            print(list_of_profiles)
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
    liked_profile = await get_user_by_id(user_id, Anketa=True)
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
    dict_of_profiles[str(msg.from_user.id)]["profiles_list"].pop()
    await search_love_step1(msg)


@dp.message_handler(Text('Показать'))
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
    if len(dict_of_profiles[str(msg.from_user.id)]["profiles_list"]) != 0:
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
        await search_love_reg(msg)

















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








    

    





