from aiogram.fsm.state import State, StatesGroup


class FSMGroups(StatesGroup):
    view_groups = State()
    view_current_group = State()
    view_groups_to_remove = State()