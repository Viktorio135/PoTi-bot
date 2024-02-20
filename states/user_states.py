from aiogram.dispatcher.filters.state import State, StatesGroup



class Register_new_user(StatesGroup):
    name = State()
    sex = State()
    search_to = State()
    age = State()
    description = State()
    university = State()
    education = State()
    speciality = State()
    course = State()
    photos = State()