from aiogram.fsm.state import State, StatesGroup

class AdminStates(StatesGroup):
    file = State()
    geo = State()
    top = State()
    token = State()