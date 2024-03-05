from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminDeleteUser(StatesGroup):
    user_id = State()
    cause = State()
    confirmation = State()