import json

from dataBase.db_commands import create_user, has_register, get_university_id_by_name, get_university_name_by_id
from keyboards import select_sex, select_university, select_education, end_registration_kb
from dataBase.models import start_db
from states.user_states import Register_new_user

from datetime import date

from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage


bot = Bot(token='6874586651:AAFeVAJ4fOIR_z2uWcG1Og5kaWOhkNCH3U0')
dp = Dispatcher(bot, storage=MemoryStorage())

cached_data = {}

@dp.message_handler(commands='start')
async def cmd_start(msg: types.Message):

    if await has_register(str(msg.from_user.id)):
        await bot.send_message(
            msg.from_user.id, 
            'Привет, ты попал в ... Мы поможем тебе кого-нибудь найти.'
            )
    else:
        await register_or_update_user(msg)


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
        'Прекрасно, сколько тебе лет?'
        )
    
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
        await bot.send_message(msg.from_user.id, 'Произошла ошибка сохранения, попробуйте снова')
        return
    
async def end_registration(msg: types.Message, data):

    datas = {
        "name": data["name"],
        "sex": data["sex"], 
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
    await bot.send_photo(
            msg.from_user.id, 
            open(f'static/users_photo/{msg.from_user.id}.jpg', 'rb'),
            f'{datas["name"]}, {datas["age"]}, {datas["university"]} - {datas["speciality"]}({datas["course"]} курс, {datas["education"]})\n\n{datas["description"]}',
            reply_markup=end_registration_kb(file_id)
        ) 
    

@dp.callback_query_handler(lambda c: 'end_registration' in c.data)
async def save_user_to_bd(callback_query: types.CallbackQuery):

            file_id = int(callback_query.data.split(':')[1])
            data = cached_data.get(file_id)        

            user_name = callback_query.from_user.username
            id_user = callback_query.from_user.id

            await create_user(
                name=data["name"], 
                sex=data["sex"], 
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

            await bot.send_message(
                 callback_query.from_user.id, 
                 'Хайп'
            )


if __name__ == '__main__':
    start_db()
    executor.start_polling(dp, skip_updates=True)








    

    





