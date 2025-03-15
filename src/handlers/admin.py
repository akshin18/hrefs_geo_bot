import asyncio
import os

from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from src.builders.admin import get_main_menu
from src.filters.admin import AdminFilter
from src.stastes.admin import AdminStates
from src.utils import generate_random_filename, geo_process

router = Router()
router.message.filter(AdminFilter())


@router.message(F.text == "Get Token")
async def get_token(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    token = data.get("token", "No token")
    await message.answer(token)

@router.message(F.text == "Set token")
async def set_token(message: Message, state: FSMContext) -> None:
    await state.set_state(AdminStates.token)
    await message.answer("Send token")

@router.message(AdminStates.token)
async def set_token(message: Message, state: FSMContext) -> None:
    token = message.text
    await state.update_data({"token":token})
    await state.set_state()
    await message.answer("Token set")

@router.message(F.text == "Geo")
async def admin_cancel(message: Message, state: FSMContext) -> None:
    await state.set_state(AdminStates.file)
    await message.answer("Send file")

@router.message(AdminStates.file, F.content_type == ContentType.DOCUMENT)
async def handle_file(message: Message, state: FSMContext) -> None:
    document = message.document
    file_extension = os.path.splitext(document.file_name)[1]
    random_filename = generate_random_filename(file_extension)
    file_path = f"files/{random_filename}"
    await message.bot.download(document, destination=file_path)
    await message.answer(f"File saved as {random_filename}")
    await state.update_data({"random_filename":random_filename})

    await state.set_state(AdminStates.geo)
    await message.answer("Write geo or cancel if you do not want. Example: us,ca,de")

@router.message(AdminStates.geo)
async def handle_geo(message: Message, state: FSMContext) -> None:
    if message.text.lower() == "cancel":
        await state.set_state()
        data = await state.get_data()
        await geo_process(data, message=message)
        return

    geos = message.text.replace(" ","").split(",")
    await state.update_data({"geos":geos})


@router.message(AdminStates.top)
async def handle_top(message: Message, state: FSMContext) -> None:
    await message.answer("Top count. Example: 5")
    await state.set_state(AdminStates.top)
    data = await state.get_data()
    await state.set_state()
    await geo_process(data, message=message)


@router.message()
async def main_menu(message: Message) -> None:
    await message.answer("Main:",reply_markup=get_main_menu())