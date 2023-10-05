from aiogram.fsm.state import StatesGroup, State


class FSMPosts(StatesGroup):
    view_post_groups = State()
    view_post = State()
    take_name_post = State()
    take_post = State()
    remove_post = State()
    back_to_posts = State()
