import os
import sqlite3
import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    BusinessConnection,
    BusinessMessagesDeleted,
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


# =========================
# НАСТРОЙКИ
# =========================

TOKEN = os.getenv("BOT_TOKEN", "")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
DB_PATH = os.getenv("DB_PATH", "bot.db")

if not TOKEN:
    raise RuntimeError("Добавь BOT_TOKEN в Secrets.")

if not OWNER_ID:
    raise RuntimeError("Добавь OWNER_ID в Secrets.")

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)
dp = Dispatcher()


# =========================
# БАЗА ДАННЫХ
# =========================

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                chat_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                connection_id TEXT,
                text TEXT,
                saved_at TEXT,
                PRIMARY KEY (chat_id, message_id)
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS connections (
                connection_id TEXT PRIMARY KEY,
                user_id INTEGER,
                is_enabled INTEGER,
                updated_at TEXT
            )
        """)


def save_message(
    chat_id: int,
    message_id: int,
    connection_id: str,
    text: str,
):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO messages
            (chat_id, message_id, connection_id, text, saved_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            chat_id,
            message_id,
            connection_id,
            text,
            datetime.utcnow().isoformat(),
        ))


def get_saved_message(chat_id: int, message_id: int):
    with sqlite3.connect(DB_PATH) as conn:
        row = conn.execute("""
            SELECT text FROM messages
            WHERE chat_id = ? AND message_id = ?
        """, (chat_id, message_id)).fetchone()

    return row[0] if row else None


def save_connection(connection: BusinessConnection):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT OR REPLACE INTO connections
            (connection_id, user_id, is_enabled, updated_at)
            VALUES (?, ?, ?, ?)
        """, (
            connection.id,
            connection.user.id,
            int(connection.is_enabled),
            datetime.utcnow().isoformat(),
        ))


# =========================
# КЛАВИАТУРЫ
# =========================

def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔗 Telegram Business",
                    callback_data="business_info",
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Статус бота",
                    callback_data="bot_status",
                )
            ],
            [
                InlineKeyboardButton(
                    text="ℹ️ Помощь",
                    callback_data="help",
                )
            ],
        ]
    )


def back_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="main_menu",
                )
            ]
        ]
    )


# =========================
# КОМАНДЫ
# =========================

@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.answer(
        "👋 <b>Привет!</b>\n\n"
        "Бот запущен.\n"
        "Выбери нужный раздел в меню:",
        reply_markup=main_menu(),
    )


@dp.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "ℹ️ <b>Помощь</b>\n\n"
        "/start — открыть меню\n"
        "/help — помощь\n"
        "/repeat 2 текст — повторить текст до 3 раз "
        "в этом личном чате с ботом.\n\n"
        "Функции Telegram Business работают только "
        "в пределах выданных Telegram разрешений."
    )


# =========================
# ПОВТОР ТЕКСТА
# Только в личном чате с ботом
# =========================

@dp.message(Command("repeat"))
async def repeat_handler(message: Message):
    if message.from_user is None or message.from_user.id != OWNER_ID:
        await message.answer("⛔ Эта команда недоступна.")
        return

    if message.chat.type != "private":
        await message.answer(
            "Используй /repeat только в личном чате с ботом."
        )
        return

    parts = (message.text or "").split(maxsplit=2)

    if len(parts) < 3:
        await message.answer(
            "Формат команды:\n"
            "<code>/repeat 3 Привет!</code>\n\n"
            "Максимум — 3 повтора."
        )
        return

    try:
        count = int(parts[1])
    except ValueError:
        await message.answer("Укажи число от 1 до 3.")
        return

    if not 1 <= count <= 3:
        await message.answer("Можно повторить текст от 1 до 3 раз.")
        return

    text_to_repeat = parts[2]

    for _ in range(count):
        await message.answer(text_to_repeat)
        await asyncio.sleep(0.3)


# =========================
# CALLBACK-КНОПКИ
# =========================

@dp.callback_query(F.data == "main_menu")
async def main_menu_handler(callback: CallbackQuery):
    if callback.message:
        await callback.message.edit_text(
            "🏠 <b>Главное меню</b>\n\nВыбери раздел:",
            reply_markup=main_menu(),
        )
    await callback.answer()


@dp.callback_query(F.data == "business_info")
async def business_info_handler(callback: CallbackQuery):
    # Обновлённый текст: нежелательная фраза удалена.
    if callback.message:
        await callback.message.edit_text(
            "🔗 <b>TELEGRAM BUSINESS</b>\n\n"
            "1. Открой настройки Telegram Business.\n"
            "2. Найди раздел чат-ботов.\n"
            "3. Выбери своего бота.\n"
            "4. Выдай необходимые разрешения.\n"
            "5. Выбери чаты, к которым разрешён доступ.",
            reply_markup=back_menu(),
        )

    await callback.answer()


@dp.callback_query(F.data == "bot_status")
async def bot_status_handler(callback: CallbackQuery):
    if callback.message:
        await callback.message.edit_text(
            "📊 <b>Статус бота</b>\n\n"
            "Бот работает, если он запущен на хостинге.\n"
            "Проверить запуск можно в журнале выполнения.",
            reply_markup=back_menu(),
        )

    await callback.answer()


@dp.callback_query(F.data == "help")
async def help_callback_handler(callback: CallbackQuery):
    if callback.message:
        await callback.message.edit_text(
            "ℹ️ <b>Помощь</b>\n\n"
            "/start — главное меню\n"
            "/help — помощь\n"
            "/repeat 2 текст — повторить текст до 3 раз "
            "в личном чате с ботом.",
            reply_markup=back_menu(),
        )

    await callback.answer()


# =========================
# TELEGRAM BUSINESS:
# ОБНОВЛЕНИЯ ПОДКЛЮЧЕНИЯ
# =========================

@dp.business_connection()
async def business_connection_handler(
    connection: BusinessConnection,
):
    save_connection(connection)

    if connection.user.id == OWNER_ID:
        status = (
            "включено"
            if connection.is_enabled
            else "отключено"
        )

        try:
            await bot.send_message(
                OWNER_ID,
                "🔗 <b>Обновление Telegram Business</b>\n\n"
                f"Подключение: <code>{connection.id}</code>\n"
                f"Статус: {status}",
            )
        except Exception:
            pass


# =========================
# СОХРАНЕНИЕ ДОСТУПНЫХ BUSINESS-СООБЩЕНИЙ
# =========================

@dp.business_message()
async def business_message_handler(message: Message):
    connection_id = message.business_connection_id

    if not connection_id:
        return

    text_content = message.text or message.caption or ""

    if text_content:
        save_message(
            chat_id=message.chat.id,
            message_id=message.message_id,
            connection_id=connection_id,
            text=text_content,
        )


# =========================
# ОБНОВЛЁННЫЕ BUSINESS-СООБЩЕНИЯ
# =========================

@dp.edited_business_message()
async def edited_business_message_handler(message: Message):
    connection_id = message.business_connection_id

    if not connection_id:
        return

    text_content = message.text or message.caption or ""

    if text_content:
        save_message(
            chat_id=message.chat.id,
            message_id=message.message_id,
            connection_id=connection_id,
            text=text_content,
        )


# =========================
# УДАЛЁННЫЕ BUSINESS-СООБЩЕНИЯ
# =========================

@dp.deleted_business_messages()
async def deleted_business_messages_handler(
    event: BusinessMessagesDeleted,
):
    if not event.message_ids:
        return

    for message_id in event.message_ids:
        saved_text = get_saved_message(
            event.chat.id,
            message_id,
        )

        if saved_text:
            notification = (
                "🗑 <b>Сообщение удалено</b>\n\n"
                f"Чат ID: <code>{event.chat.id}</code>\n"
                f"ID сообщения: <code>{message_id}</code>\n\n"
                f"Сохранённый текст:\n{saved_text}"
            )
        else:
            notification = (
                "🗑 <b>Сообщение удалено</b>\n\n"
                f"Чат ID: <code>{event.chat.id}</code>\n"
                f"ID сообщения: <code>{message_id}</code>\n\n"
                "Текст сообщения не был сохранён ранее."
            )

        try:
            await bot.send_message(
                OWNER_ID,
                notification,
            )
        except Exception:
            pass


# =========================
# ЗАПУСК
# =========================

async def main():
    init_db()
    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
    )


if __name__ == "__main__":
    asyncio.run(main())
