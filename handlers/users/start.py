import os
import uuid
from datetime import datetime

from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart, Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from loader import dp
from db_mysql import get_mahallas_by_id_tuman, insert_tadbirkor, get_tadbirkors_column_info, get_mahalla_text
from utils.misc import logging

# Define the directory to save files
UPLOAD_DIR = ".././upload/files"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Define states
class Registration(StatesGroup):
    first_name = State()
    last_name = State()
    fathers_name = State()
    region = State()
    mahalla = State()
    korxona = State()
    korxona_nomi = State()
    inn = State()
    phone = State()
    mazmun = State()
    ilova = State()

dp.middleware.setup(LoggingMiddleware())

@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await get_tadbirkors_column_info()
    button_qoldirish = KeyboardButton('📃 Murojaat qoldirish')
    button_tekshirish = KeyboardButton('🔎 Murojaatni tekshirish')
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(button_qoldirish, button_tekshirish)
    await message.answer("<b>Xush kelibsiz!</b> \n Botimiz siznig arizaggizni qabul qiladi va holati haqida ma'lumot berib boradi.", reply_markup=keyboard)

@dp.message_handler(Text(equals="📃 Murojaat qoldirish"))
async def ask_first_name(message: types.Message):
    await message.answer("<b>👨‍🦱 Iltimos, familiyangizni kiriting:</b>", reply_markup=ReplyKeyboardRemove())
    await Registration.last_name.set()

@dp.message_handler(state=Registration.last_name)
async def process_first_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['last_name'] = message.text
    await message.answer("<b>👨‍🦳 Iltimos, ismingizni kiriting:</b>")
    await Registration.first_name.set()

@dp.message_handler(state=Registration.first_name)
async def process_last_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['first_name'] = message.text
    await message.answer("<b>👨‍🦰 Iltimos, Sharifingizni kiriting:</b>")
    await Registration.fathers_name.set()

@dp.message_handler(state=Registration.fathers_name)
async def process_fathers_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['fathers_name'] = message.text
    regions = [
        "Buxoro shahri", "Kogon shahar", "Buxoro tumani", "Vobkent tumani", "Jondor tumani",
        "Kogon tumani", "Olot tumani", "Peshku tumani", "Romitan tumani", "Shofirkon tumani",
        "Qorako'l tumani", "Qorovulbozor tumani", "G'ijduvon tumani"
    ]
    keyboard = InlineKeyboardMarkup(row_width=2)
    for i in range(0, len(regions), 2):
        if i + 1 < len(regions):
            keyboard.add(
                InlineKeyboardButton(text=regions[i], callback_data=str(i + 1)),
                InlineKeyboardButton(text=regions[i + 1], callback_data=str(i + 2))
            )
        else:
            # print(regions[i])
            keyboard.add(InlineKeyboardButton(text=regions[i], callback_data=str(i+1)))
    await message.answer("<b>📍 Tumanni tanlang </b>", reply_markup=keyboard)
    await Registration.region.set()

def create_pagination_keyboard(items, page, items_per_page=14):
    total_pages = (len(items) + items_per_page - 1) // items_per_page
    keyboard = InlineKeyboardMarkup(row_width=2)
    start = (page - 1) * items_per_page
    end = min(start + items_per_page, len(items))
    for i in range(start, end, 2):
        if i + 1 < end:
            keyboard.add(
                InlineKeyboardButton(text=items[i][2], callback_data=f"mahalla_{items[i][0]}"),
                InlineKeyboardButton(text=items[i + 1][2], callback_data=f"mahalla_{items[i + 1][0]}")
            )
        else:
            keyboard.add(
                InlineKeyboardButton(text=items[i][2], callback_data=f"mahalla_{items[i][0]}")
            )
    if total_pages > 1:
        if page > 1:
            keyboard.add(InlineKeyboardButton("⬅️ ", callback_data=f"page_{page - 1}"))
        if page < total_pages:
            keyboard.add(InlineKeyboardButton(" ➡️", callback_data=f"page_{page + 1}"))
    return keyboard

@dp.callback_query_handler(lambda c: c.data.isdigit(), state=Registration.region)
async def handle_region_selection(callback_query: types.CallbackQuery, state: FSMContext):
    region_id = int(callback_query.data)
    async with state.proxy() as data:
        data['region_id'] = region_id
        data['page'] = 1
    mahallas = await get_mahallas_by_id_tuman(region_id)
    keyboard = create_pagination_keyboard(mahallas, data['page'])
    await callback_query.message.edit_text("<b>📍 Mahallangizni tanlang </b>", reply_markup=keyboard)
    await Registration.mahalla.set()

@dp.callback_query_handler(lambda c: c.data.startswith('page_'), state=Registration.mahalla)
async def handle_pagination(callback_query: types.CallbackQuery, state: FSMContext):
    current_page = int(callback_query.data.split('_')[1])
    async with state.proxy() as data:
        region_id = data.get('region_id')
        if not region_id:
            await callback_query.answer("Region not selected.")
            return
        data['page'] = current_page

        mahallas = await get_mahallas_by_id_tuman(region_id)
        keyboard = create_pagination_keyboard(mahallas, current_page)
        await callback_query.message.edit_text("<b>📍 Mahallangizni tanlang </b>", reply_markup=keyboard)
        await callback_query.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("mahalla_"), state=Registration.mahalla)
async def handle_mahalla_selection(callback_query: types.CallbackQuery, state: FSMContext):
    mahalla_id = int(callback_query.data.split("_")[1])
    async with state.proxy() as data:
        data['mahalla_id'] = mahalla_id
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton(text="Ha bor ✅", callback_data="korxona_bor"),
        InlineKeyboardButton(text="Yo'q ❌", callback_data="korxona_yoq")
    )
    await callback_query.message.edit_text("<b>Korxonangiz mavjudmi?</b>", reply_markup=keyboard)
    await Registration.korxona.set()

@dp.callback_query_handler(lambda c: c.data in ["korxona_bor", "korxona_yoq"], state=Registration.korxona)
async def handle_korxona_selection(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['korxona'] = callback_query.data
    if callback_query.data == "korxona_bor":
        await callback_query.message.answer("<b>🏭 Korxona nomini kiriting:</b>")
        await Registration.korxona_nomi.set()
    else:
        await ask_phone_number(callback_query.message, state)


@dp.message_handler(state=Registration.korxona_nomi)
async def process_korxona_nomi(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['korxona_nomi'] = message.text
    await message.answer("<b>💳 INN kiriting:</b>")
    await Registration.inn.set()


@dp.message_handler(state=Registration.inn)
async def process_inn(message: types.Message, state: FSMContext):
    try:
        inn = int(message.text)
        async with state.proxy() as data:
            data['inn'] = inn

        await ask_phone_number(message, state)
    except ValueError:
        await message.answer("<b>💳 INN notog'ri formatda kiritildi. Iltimos, qayta kiriting:</b>")


async def ask_phone_number(message: types.Message, state: FSMContext):
    await message.answer("<b>📞 Telefon raqamingizni kiriting +998901234567 ko'rinishida:</b>")
    await Registration.phone.set()


@dp.message_handler(state=Registration.phone)
async def process_phone(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['phone'] = message.text
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="next ➡️", callback_data="skip_mazmun")
    )
    sent_message = await message.answer("<b>Murojaat mazmunini kiriting:</b> ")
    async with state.proxy() as data:
        data['last_bot_message_id'] = sent_message.message_id
    await Registration.mazmun.set()

@dp.callback_query_handler(lambda c: c.data == "skip_mazmun", state=Registration.mazmun)
async def skip_mazmun(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        current_bot_message_id = data.get('last_bot_message_id', None)
        data['mazmun'] = ""
    if current_bot_message_id:
        try:
            await callback_query.message.bot.delete_message(
                chat_id=callback_query.message.chat.id,
                message_id=current_bot_message_id
            )
        except Exception as e:
            print(f"Failed to delete message: {e}")
    await ask_ilova(callback_query.message, state)

@dp.message_handler(state=Registration.mazmun)
async def process_mazmun(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        current_bot_message_id = data.get('last_bot_message_id', None)
        data['mazmun'] = message.text
    if current_bot_message_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id,
                message_id=current_bot_message_id
            )
        except Exception as e:
            print(f"Failed to delete message: {e}")
    await ask_ilova(message, state)

async def ask_ilova(message: types.Message, state: FSMContext):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton(text="next ➡️", callback_data="skip_ilova")
    )
    sent_message = await message.answer("<b>Ilova yuklang \n (Iltimos, faqat PDF faylni yuklang): </b> \n Agar ilova yo'q bo'lsa, (next ➡️) bosing", reply_markup=keyboard)
    async with state.proxy() as data:
        data['last_bot_message_id'] = sent_message.message_id
    await Registration.ilova.set()

@dp.callback_query_handler(lambda c: c.data == "skip_ilova", state=Registration.ilova)
async def skip_ilova(callback_query: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        current_bot_message_id = data.get('last_bot_message_id', None)
        data['ilova'] = None
    if current_bot_message_id:
        try:
            await callback_query.message.bot.delete_message(
                chat_id=callback_query.message.chat.id,
                message_id=current_bot_message_id
            )
        except Exception as e:
            print(f"Failed to delete message: {e}")
    await finish_registration(callback_query.message, state)

@dp.message_handler(content_types=types.ContentType.DOCUMENT, state=Registration.ilova)
async def process_ilova(message: types.Message, state: FSMContext):
    document = message.document
    async with state.proxy() as data:
        current_bot_message_id = data.get('last_bot_message_id', None)
    if document.mime_type == 'application/pdf':
        unique_filename = f"{uuid.uuid4()}.pdf"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        await document.download(destination=file_path)
        if current_bot_message_id:
            try:
                await message.bot.delete_message(
                    chat_id=message.chat.id,
                    message_id=current_bot_message_id
                )
            except Exception as e:
                print(f"Failed to delete message: {e}")
        async with state.proxy() as data:
            data['ilova'] = unique_filename
        await finish_registration(message, state)
    else:
        await ask_ilova(message, state)




async def finish_registration(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        button_qoldirish = KeyboardButton('📃 Murojaat qoldirish')
        button_tekshirish = KeyboardButton('🔎 Murojaatni tekshirish')
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(button_qoldirish, button_tekshirish)
        try:
            await insert_tadbirkor(data)
            regions = ["Buxoro shahri", "Kogon shahar", "Buxoro tumani", "Vobkent tumani", "Jondor tumani","Kogon tumani", "Olot tumani", "Peshku tumani", "Romitan tumani", "Shofirkon tumani", "Qorako'l tumani", "Qorovulbozor tumani", "G'ijduvon tumani"]
            region_text = regions[data['region_id']] if 0 <= data['region_id'] < len(regions) else "Noma'lum tuman"
            mahalla_text = await get_mahalla_text(data['mahalla_id'])
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            confirmation_message = f"""
            <b>📨 Murojaat qoldirish muvaffaqiyatli yakunlandi!</b>
            <b>👨‍🦰 FIO</b>: {data['last_name']}, {data['first_name']} {data['fathers_name']}
            <b>📍 Tuman</b>: {region_text}
            <b>📍 Mahalla</b>: {mahalla_text}
            <b>🏭 Korxona</b>: {"mavjud" if data['korxona_nomi'] else "mavjud emas"}
            <b>💳 INN</b>: {data['inn']}
            <b>📞 Tel number</b>: {data['phone']}
            <b>📄 Mazmuni</b>: {data['mazmun']}
            <b>Murojaat holati</b> 1
            <b>🕐 Ro'yxatga olingan vaqti:</b>  {current_time}
            """

            # Send the confirmation message
            await message.answer(confirmation_message, parse_mode="HTML")

            # Send the attached file if present
            if data.get('ilova'):
                file_path = os.path.join(UPLOAD_DIR, data['ilova'])
                if os.path.exists(file_path):
                    with open(file_path, 'rb') as file:
                        await message.answer_document(file)
                else:
                    await message.answer("Ilova topilmadi.", reply_markup=keyboard)

        except Exception as e:
            logging.error(f"Failed to save registration data: {e}")
            await message.answer("Murojaatni saqlashda xatolik yuz berdi. Iltimos, qayta urinib ko'ring.", reply_markup=keyboard)

        finally:
            # Finish the state regardless of success or failure
            await message.answer("Murojaat qoldirish tugatildi.", reply_markup=keyboard)
            await state.finish()