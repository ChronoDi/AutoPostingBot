from fluentogram import TranslatorRunner

from tg_bot.keyboards.fabric import get_inline_keyboards


async def get_main_menu_keyboard(lexicon: TranslatorRunner):
    callback_names = {'posts': lexicon.view.posts(),
                      'groups' : lexicon.view.groups(),
                      'mailing' : lexicon.view.mailing()}
    return get_inline_keyboards(callback_names=callback_names, width=1)