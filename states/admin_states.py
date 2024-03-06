from aiogram.dispatcher.filters.state import State, StatesGroup


class AdminBlockUser(StatesGroup):
    user_id = State()
    cause = State()
    confirmation = State()

class AdminUnblockUser(StatesGroup):
    user_id = State()
    confirmation = State()

class AdminGetUserById(StatesGroup):
    user_id = State()

class AdminSpamHasPhoto(StatesGroup):
    has_photo = State()

class AdminSpamWithPhoto(StatesGroup):
    path = State()
    spam_text = State()
    confirmation = State()

class AdminSpamOnlyText(StatesGroup):
    spam_text = State()
    confirmation = State()

class AdminGetUserByPhoto(StatesGroup):
    path = State()