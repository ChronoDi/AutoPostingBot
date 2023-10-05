from fluent_compiler.bundle import FluentBundle
from fluentogram import TranslatorHub, FluentTranslator


def get_hub() -> TranslatorHub:
    translator_hub = TranslatorHub(
        {
            'ru' : ('ru',)
        },
        [
            FluentTranslator(locale='ru',
                             translator=FluentBundle.from_files('ru-RU',
                                                                filenames=['tg_bot/lexicon/locales/ru.ftl'])
                             ),
        ],
        root_locale='ru'
    )

    return translator_hub