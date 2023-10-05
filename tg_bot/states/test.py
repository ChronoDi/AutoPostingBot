from aiogram.fsm.state import StatesGroup, State


class TestState(StatesGroup):
    main = State()
    take_post = State()
    show_save_post = State()

