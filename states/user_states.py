from aiogram.dispatcher.filters.state import State, StatesGroup



class Register_new_user(StatesGroup):
    name = State()
    game_id = State()
    role1 = State()
    role2 = State()
    role3 = State()
    description = State()
    screenshot1 = State()
    screenshot2 = State()




################# Обновление профиля  #################

class Change_photo(StatesGroup):
    screenshot1 = State()
    screenshot2 = State()

class Change_description(StatesGroup):
    description = State()

#####################################


class ReportUserOther(StatesGroup):
    cause = State()
