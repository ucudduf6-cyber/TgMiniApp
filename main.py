
import asyncio
import logging
import os
import sqlite3

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise RuntimeError("Укажи BOT_TOKEN в файле .env")

dp = Dispatcher()
DB_PATH = "bot.sqlite3"


def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                history_enabled INTEGER NOT NULL DEFAULT 0
            )
        """)


def register_user(user_id: int, username: str | None):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO users (user_id, username)
            VALUES (?, ?)
            ON CONFLICT(user_id)
            DO UPDATE SET username = excluded.username
            """,
            (user_id, username),
        )


def get_user(user_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT user_id, username, history_enabled "
            "FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⚙️ Настройки",
                callback_data="settings",
            )
        ],
        [
            InlineKeyboardButton(
                text="ℹ️ О боте",
                callback_data="about",
            )
        ],
    ])


def settings_menu(history_enabled: bool):
    status = "Включена" if history_enabled else "Выключена"

    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f"История: {status}",
                callback_data="toggle_history",
            )
        ],
        [
            InlineKeyboardButton(
                text="⬅️ Главное меню",
                callback_data="home",
            )
        ],
    ])


@dp.message(CommandStart())
async def start(message: Message):
    user = message.from_user
    register_user(user.id, user.username)

    await message.answer(
        "Привет! 👋\n\n"
        "Это твой Telegram-бот-компаньон.\n"
        "Выбери нужный раздел:",
        reply_markup=main_menu(),
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "/start — главное меню\n"
        "/settings — настройки\n"
        "/help — помощь"
    )


@dp.message(Command("settings"))
async def settings_command(message: Message):
    user = get_user(message.from_user.id)

    if not user:
        register_user(
            message.from_user.id,
            message.from_user.username,
        )
        user = get_user(message.from_user.id)

    await message.answer(
        "Настройки:",
        reply_markup=settings_menu(bool(user[2])),
    )


@dp.callback_query(F.data == "home")
async def home(callback: CallbackQuery):
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=main_menu(),
    )
    await callback.answer()


@dp.callback_query(F.data == "settings")
async def settings(callback: CallbackQuery):
    user = get_user(callback.from_user.id)

    if not user:
        register_user(
            callback.from_user.id,
            callback.from_user.username,
        )
        user = get_user(callback.from_user.id)

    await callback.message.edit_text(
        "Настройки:",
        reply_markup=settings_menu(bool(user[2])),
    )
    await callback.answer()


@dp.callback_query(F.data == "toggle_history")
async def toggle_history(callback: CallbackQuery):
    user = get_user(callback.from_user.id)

    if not user:
        register_user(
            callback.from_user.id,
            callback.from_user.username,
        )
        user = get_user(callback.from_user.id)

    new_value = 0 if user[2] else 1

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            "UPDATE users SET history_enabled = ? "
            "WHERE user_id = ?",
            (new_value, callback.from_user.id),
        )

    await callback.message.edit_reply_markup(
        reply_markup=settings_menu(bool(new_value))
    )
    await callback.answer("Настройка сохранена")


@dp.callback_query(F.data == "about")
async def about(callback: CallbackQuery):
    await callback.message.edit_text(
        "Telegram-бот-компаньон.\n"
        "Функции добавляются по мере разработки.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Главное меню",
                    callback_data="home",
                )
            ]
        ]),
    )
    await callback.answer()


async def main():
    logging.basicConfig(level=logging.INFO)
    init_db()

    bot = Bot(token=BOT_TOKEN)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
