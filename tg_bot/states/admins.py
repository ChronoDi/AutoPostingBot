from aiogram.fsm.state import StatesGroup, State


class FSMAdmins(StatesGroup):
    view_admins = State()
    view_current_admin = State()
    take_user_info = State()
    view_users = State()
    confirmation_add_user = State()
    role_changed = State()
