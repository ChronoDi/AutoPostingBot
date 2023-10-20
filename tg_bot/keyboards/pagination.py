from fluentogram import TranslatorRunner

from tg_bot.keyboards.fabric import get_inline_keyboards


async def get_add_back_keyboard(callback_names: dict[str, str], lexicon: TranslatorRunner, width: int = 1):
    second_last_buttons = {'add' : lexicon.add(), 'back' : lexicon.back()}
    first_last_buttons = {'previous' : '<<', 'next' : '>>'}

    return get_inline_keyboards(width=width, callback_names=callback_names,
                                first_last_buttons=first_last_buttons, second_last_buttons=second_last_buttons)


async def get_add_back_remove_keyboard(callback_names: dict[str, str] | None, lexicon: TranslatorRunner, width: int = 1):
    second_last_buttons = {'add' : lexicon.add(), 'back' : lexicon.back(), 'remove' : lexicon.remove()}
    first_last_buttons = {'previous' : '<<', 'next' : '>>'}

    return get_inline_keyboards(width=width, callback_names=callback_names,
                                first_last_buttons=first_last_buttons, second_last_buttons=second_last_buttons)


async def get_back_to_post_groups_keyboard(lexicon: TranslatorRunner):
    return get_inline_keyboards(width=1, callback_names={'post_groups' : lexicon.to.post.groups()})


async def get_back_remove_keyboard(callback_names: dict[str: str], lexicon: TranslatorRunner,
                                   special_symbol: str = None, width: int = 1):
    last_buttons = {'previous': '<<', 'remove': lexicon.remove(), 'back': lexicon.back(), 'next': '>>'}

    return get_inline_keyboards(width=width, callback_names=callback_names,
                                first_last_buttons=last_buttons, special_symbol=special_symbol)


async def get_back_keyboad(lexicon: TranslatorRunner):
    return get_inline_keyboards(width=1, callback_names={'back' : lexicon.back()})


async def get_only_add_back_keyboad(lexicon: TranslatorRunner):
    return get_inline_keyboards(width=2, callback_names={'add' : lexicon.add(), 'back' : lexicon.back()})


async def get_only_remove_back_keyboad(lexicon: TranslatorRunner):
    return get_inline_keyboards(width=2, callback_names={'remove' : lexicon.remove(), 'back' : lexicon.back()})


async def get_back_scroll_keyboard(callback_names: dict[str: str], lexicon: TranslatorRunner,
                                   special_symbol: str = None, width: int = 1):
    last_buttons = {'previous': '<<', 'back': lexicon.back(), 'next': '>>'}

    return get_inline_keyboards(width=width, callback_names=callback_names,
                                first_last_buttons=last_buttons, special_symbol=special_symbol)


async def get_next_keyboard():
    last_buttons = {'next': '>>'}

    return get_inline_keyboards(width=1, first_last_buttons=last_buttons)


async def get_add_scroll_keyboard(callback_names: dict[str: str], lexicon: TranslatorRunner,
                                   special_symbol: str = None, width: int = 1):
    last_buttons = {'previous': '<<', 'add': lexicon.add(), 'next': '>>'}

    return get_inline_keyboards(width=width, callback_names=callback_names,
                                first_last_buttons=last_buttons, special_symbol=special_symbol)


async def get_refresh_back_remove_keyboard(callback_names: dict[str, str] | None, lexicon: TranslatorRunner, width: int = 1):
    second_last_buttons = {'refresh' : lexicon.refresh(), 'back' : lexicon.back(), 'remove' : lexicon.remove()}
    first_last_buttons = {'previous' : '<<', 'next' : '>>'}

    return get_inline_keyboards(width=width, callback_names=callback_names,
                                first_last_buttons=first_last_buttons, second_last_buttons=second_last_buttons)

