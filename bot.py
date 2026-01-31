# ================================
# bot.py
# Horror-Studio Bot V1.5 (Stable FINAL + Buttons Fix)
# ================================

import asyncio
import os

from aiohttp import web

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext

from config import BOT_TOKEN, ADMIN_ID
from states import StoryCreation
from db import (
    init_db,
    add_story,
    add_character,
    get_stories,
    get_story,
    get_characters
)

from groq_ai import generate_story_reply

# ================================
# Создание бота
# ================================
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Временное хранение персонажей при создании истории
temp_characters = {}

# Активная история игрока
active_story = {}


# ================================
# Мини-сервер для Render Free
# ================================
async def healthcheck(request):
    return web.Response(text="Horror-Studio Bot работает ✅")


async def start_webserver():
    """
    Render требует открытый порт.
    Этот сервер нужен только чтобы Render не выключал сервис.
    """
    app = web.Application()
    app.router.add_get("/", healthcheck)

    runner = web.AppRunner(app)
    await runner.setup()

    port = int(os.getenv("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

    print(f"Web-server запущен на порту {port}")


# ================================
# Главное меню
# ================================
def main_menu(is_admin=False):
    kb = InlineKeyboardBuilder()

    if is_admin:
        kb.button(text="➕ Создать историю", callback_data="create_story")

    kb.button(text="📚 Список историй", callback_data="list_stories")
    kb.button(text="▶️ Начать историю", callback_data="play_story")

    kb.adjust(1)
    return kb.as_markup()


# ================================
# Меню управления персонажами
# ================================
def character_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Добавить персонажа", callback_data="add_character")
    kb.button(text="📜 Список персонажей", callback_data="show_characters")
    kb.button(text="✅ Создать историю", callback_data="finish_story")
    kb.adjust(1)
    return kb.as_markup()


# ================================
# Команда /start
# ================================
@dp.message(CommandStart())
async def start(message: Message):
    is_admin = (message.from_user.id == ADMIN_ID)

    await message.answer(
        "👻 Добро пожаловать в нашу студию!\n"
        "Это панель автора, у вас нету права на ошибки или даже молитвы.\n\n"
        "Внизу есть кнопки:\n"
        "#1 Создать историю\n"
        "#2 Список историй\n"
        "#3 Начать историю",
        reply_markup=main_menu(is_admin)
    )


# ================================
# Создание истории (только автор)
# ================================
@dp.callback_query(F.data == "create_story")
async def create_story(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    if callback.from_user.id != ADMIN_ID:
        await callback.message.answer("❌ Только автор может создавать истории.")
        return

    await callback.message.answer("Введите название истории:")
    await state.set_state(StoryCreation.title)


@dp.message(StoryCreation.title)
async def set_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание истории (для ИИ):")
    await state.set_state(StoryCreation.description)


@dp.message(StoryCreation.description)
async def set_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите прошлое главного героя:")
    await state.set_state(StoryCreation.hero_past)


@dp.message(StoryCreation.hero_past)
async def set_hero_past(message: Message, state: FSMContext):
    await state.update_data(hero_past=message.text)
    await message.answer("Введите обстоятельства начала истории (вступление):")
    await state.set_state(StoryCreation.start_scene)


@dp.message(StoryCreation.start_scene)
async def set_start_scene(message: Message, state: FSMContext):
    await state.update_data(start_scene=message.text)

    temp_characters[message.from_user.id] = []

    await message.answer(
        "История почти готова.\nДобавьте персонажей (до 15).",
        reply_markup=character_menu()
    )


# ================================
# Добавление персонажа
# ================================
@dp.callback_query(F.data == "add_character")
async def add_char(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    chars = temp_characters.get(callback.from_user.id, [])

    if len(chars) >= 15:
        await callback.message.answer("❌ Лимит персонажей: 15.")
        return

    await callback.message.answer("Введите имя персонажа:")
    await state.set_state(StoryCreation.char_name)


@dp.message(StoryCreation.char_name)
async def char_name(message: Message, state: FSMContext):
    await state.update_data(char_name=message.text)
    await message.answer("Сколько вашему персонажу лет?")
    await state.set_state(StoryCreation.char_age)


@dp.message(StoryCreation.char_age)
async def char_age(message: Message, state: FSMContext):
    await state.update_data(char_age=message.text)
    await message.answer("Введите роль персонажа:")
    await state.set_state(StoryCreation.char_role)


@dp.message(StoryCreation.char_role)
async def char_role(message: Message, state: FSMContext):
    await state.update_data(char_role=message.text)
    await message.answer("Опишите характер персонажа:")
    await state.set_state(StoryCreation.char_personality)


@dp.message(StoryCreation.char_personality)
async def char_personality(message: Message, state: FSMContext):
    await state.update_data(char_personality=message.text)

    kb = InlineKeyboardBuilder()
    kb.button(text="Знакомый", callback_data="known_yes")
    kb.button(text="Незнакомый", callback_data="known_no")
    kb.adjust(2)

    await message.answer("Вы знакомы с ним?", reply_markup=kb.as_markup())


@dp.callback_query(F.data.startswith("known_"))
async def char_known(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    known_status = "знакомый" if callback.data == "known_yes" else "незнакомый"
    data = await state.get_data()

    temp_characters[callback.from_user.id].append({
        "name": data["char_name"],
        "age": data["char_age"],
        "role": data["char_role"],
        "personality": data["char_personality"],
        "known": known_status
    })

    await callback.message.answer("✅ Персонаж добавлен!")
    await callback.message.answer("Управление персонажами:", reply_markup=character_menu())


# ================================
# Список персонажей
# ================================
@dp.callback_query(F.data == "show_characters")
async def show_characters(callback: CallbackQuery):
    await callback.answer()

    chars = temp_characters.get(callback.from_user.id, [])

    if not chars:
        await callback.message.answer("Персонажей пока нет.")
        return

    text = "📜 Список персонажей:\n\n"

    for i, c in enumerate(chars, start=1):
        text += (
            f"{i}) Имя: {c['name']}\n"
            f"Возраст: {c['age']}\n"
            f"Роль: {c['role']}\n"
            f"Характер: {c['personality']}\n"
            f"Статус: {c['known']}\n\n"
        )

    await callback.message.answer(text)


# ================================
# Завершение истории
# ================================
@dp.callback_query(F.data == "finish_story")
async def finish_story(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    data = await state.get_data()

    story_id = add_story(
        data["title"],
        data["description"],
        data["hero_past"],
        data["start_scene"]
    )

    for c in temp_characters.get(callback.from_user.id, []):
        add_character(
            story_id,
            c["name"],
            f"{c['role']} ({c['age']} лет)",
            c["personality"],
            c["known"]
        )

    await callback.message.answer("История создана! ✔️")
    await callback.message.answer("Главное меню:", reply_markup=main_menu(True))

    await state.clear()


# ================================
# Список историй
# ================================
@dp.callback_query(F.data == "list_stories")
async def list_stories(callback: CallbackQuery):
    await callback.answer()

    stories = get_stories()

    if not stories:
        await callback.message.answer("Историй пока нет.")
        return

    text = "📚 Истории:\n\n"
    for sid, title in stories:
        text += f"{sid}. {title}\n"

    await callback.message.answer(text)


# ================================
# Начать историю (FIXED)
# ================================
@dp.callback_query(F.data == "play_story")
async def play_story(callback: CallbackQuery):
    await callback.answer()

    stories = get_stories()

    if not stories:
        await callback.message.answer("Историй пока нет.")
        return

    kb = InlineKeyboardBuilder()
    for sid, title in stories:
        kb.button(text=title, callback_data=f"start_{sid}")

    kb.adjust(1)

    await callback.message.answer("Выберите историю:", reply_markup=kb.as_markup())


@dp.callback_query(F.data.startswith("start_"))
async def start_story(callback: CallbackQuery):
    await callback.answer()

    story_id = int(callback.data.split("_")[1])
    story = get_story(story_id)

    active_story[callback.from_user.id] = story_id

    title, desc, past, start_scene = story

    await callback.message.answer(
        f"📖 История: {title}\n\n"
        f"{start_scene}\n\n"
        "✍️ Напишите первое сообщение..."
    )


# ================================
# Игровая переписка (AI)
# ================================
@dp.message()
async def game_chat(message: Message):
    user_id = message.from_user.id

    if user_id not in active_story:
        return

    story_id = active_story[user_id]
    story_data = get_story(story_id)
    characters = get_characters(story_id)

    reply = generate_story_reply(story_data, characters, message.text)

    await message.answer(reply)


# ================================
# Запуск бота
# ================================
async def main():
    init_db()
    print("Horror-Studio Bot V1.5 запущен!")

    await start_webserver()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
