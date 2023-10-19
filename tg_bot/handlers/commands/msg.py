from pprint import pprint

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router: Router = Router()


@router.message(Command(commands='msg'))
async def process_start_command(message: Message):
    pprint(message)