from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from datetime import datetime

from loader import dp
from db_mysql import get_tadbirkor_by_phone, get_mahalla_text


class Search(StatesGroup):
    phone_search = State()


@dp.message_handler(Text(equals="🔎 Murojaatni tekshirish"))
async def ask_phone(message: types.Message):
    await message.answer("Iltimos, ro'yxatdan o'tilgan telefon raqamini kiriting.", reply_markup=ReplyKeyboardRemove())
    await Search.phone_search.set()


@dp.message_handler(state=Search.phone_search)
async def search_phone(message: types.Message, state: FSMContext):
    phone_number = message.text
    results = await get_tadbirkor_by_phone(phone_number)

    if results:
        for result in results:
            (ariza_id, arizachi_tel, created_at, id_, javob_ilova, javob_mazmuni, tashkilot_id, updated_at) = result
            created_at_formatted = created_at.strftime("%Y-%m-%d %H:%M:%S") if created_at else "Noma'lum vaqt"
            confirmation_message = f"""
            <b>📨 Sizning murojaatlaringiz!</b>
            <b>📞 Tel number</b>: {arizachi_tel}
            <b>📄 Mazmuni</b>: {javob_mazmuni}
            <b>🕐 Ro'yxatga olingan vaqti:</b> {created_at_formatted}
            """

            await message.answer(confirmation_message, parse_mode="HTML")

            # Send the document if javob_ilova is not empty
            if javob_ilova:
                try:
                    await message.answer_document(open(javob_ilova, 'rb'))
                except FileNotFoundError:
                    await message.answer("Ilova fayli topilmadi.")
    else:
        await message.answer("Kiritilgan telefon raqam ro'yxatdan o'tmagan.")
    await state.finish()


# Echo bot
@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    await message.answer(message.text)
