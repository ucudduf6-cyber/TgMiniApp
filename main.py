
import asyncio
import logging
import os
import sqlite3
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    CallbackQuery,
    BusinessConnection,
    BusinessMessagesDeleted,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

TOKEN = os.getenv("BOT_TOKEN")
DB_PATH = os.getenv("DB_PATH", "bot.sqlite3")

if not TOKEN:
    raise RuntimeError("Добавь BOT_TOKEN в GitHub Secrets")

dp = Dispatcher()


def db():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            auto_reply INTEGER NOT NULL DEFAULT 0,
            reply_text TEXT NOT NULL DEFAULT
                'Здравствуйте! Спасибо за сообщение. Я отвечу вам позже.',
            history_enabled INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS connections (
            connection_id TEXT PRIMARY KEY,
            owner_id INTEGER NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 0,
            can_reply INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            connection_id TEXT NOT NULL,
            chat_id INTEGER,
            message_id INTEGER,
            event_type TEXT NOT NULL,
            message_text TEXT,
            created_at TEXT NOT NULL
        );
        """)


def register_user(user_id, username=None):
    with db() as conn:
        conn.execute("""
            INSERT INTO users (user_id, username)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username = COALESCE(excluded.username, users.username)
        """, (user_id, username))


def get_user(user_id):
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()

    if row is None:
        register_user(user_id)
        return get_user(user_id)

    return dict(row)


def save_event(owner_id, connection_id, event_type,
               chat_id=None, message_id=None, message_text=None):
    with db() as conn:
        conn.execute("""
            INSERT INTO events (
                owner_id, connection_id, chat_id, message_id,
                event_type, message_text, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            owner_id, connection_id, chat_id, message_id,
            event_type, message_text,
            datetime.now(timezone.utc).isoformat(),
        ))


def get_connection(connection_id):
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM connections WHERE connection_id = ?",
            (connection_id,),
        ).fetchone()

    return dict(row) if row else None


def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔗 Business-подключение",
                callback_data="business",
            )
        ],
        [
            InlineKeyboardButton(
                text="🤖 Автоответ",
                callback_data="autoreply",
            ),
            InlineKeyboardButton(
                text="📚 История",
                callback_data="history",
            )
        ],
        [
            InlineKeyboardButton(
                text="📊 Статистика",
                callback_data="stats",
            )
        ],
        [
            InlineKeyboardButton(
                text="ℹ️ Инструкция",
                callback_data="help",
            )
        ]
    ])


def back_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="⬅️ Главное меню",
            callback_data="home",
        )]
    ])


def toggle_menu(user):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=(
                "🔴 Выключить автоответ"
                if user["auto_reply"]
                else "🟢 Включить автоответ"
            ),
            callback_data="toggle_auto",
        )],
        [InlineKeyboardButton(
            text=(
                "🔴 Выключить журнал"
                if user["history_enabled"]
                else "🟢 Включить журнал"
            ),
            callback_data="toggle_history",
        )],
        [InlineKeyboardButton(
            text="⬅️ Главное меню",
            callback_data="home",
        )],
    ])


@dp.message(CommandStart())
async def start(message: Message):
    register_user(message.from_user.id, message.from_user.username)

    await message.answer(
        "👋 Добро пожаловать!\n\n"
        "Это бот для управления разрешёнными функциями "
        "Telegram Business.\n\n"
        "Подключение выполняется через настройки Telegram, "
        "а не через передачу кода входа или пароля.",
        reply_markup=main_menu(),
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Команды:\n"
        "/start — главное меню\n"
        "/settings — настройки\n"
        "/status — состояние Business-подключения"
    )


@dp.message(Command("settings"))
async def settings_command(message: Message):
    user = get_user(message.from_user.id)
    await message.answer(
        "⚙️ Настройки:",
        reply_markup=toggle_menu(user),
    )


@dp.message(Command("status"))
async def status_command(message: Message):
    with db() as conn:
        rows = conn.execute(
            "SELECT enabled, can_reply FROM connections "
            "WHERE owner_id = ?",
            (message.from_user.id,),
        ).fetchall()

    if not rows:
        await message.answer(
            "Business-подключение пока не обнаружено.",
            reply_markup=back_menu(),
        )
        return

    active = sum(row["enabled"] for row in rows)
    reply_allowed = sum(
        row["enabled"] and row["can_reply"] for row in rows
    )

    await message.answer(
        f"Подключений в базе: {len(rows)}\n"
        f"Активных: {active}\n"
        f"С правом ответа: {reply_allowed}",
        reply_markup=back_menu(),
    )


@dp.callback_query(F.data == "home")
async def home(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏠 Главное меню",
        reply_markup=main_menu(),
    )
    await callback.answer()


@dp.callback_query(F.data == "business")
async def business_info(callback: CallbackQuery):
    user = get_user(callback.from_user.id)

    with db() as conn:
        rows = conn.execute(
            "SELECT enabled, can_reply FROM connections "
            "WHERE owner_id = ?",
            (callback.from_user.id,),
        ).fetchall()

    active = sum(row["enabled"] for row in rows)
    can_reply = sum(
        row["enabled"] and row["can_reply"] for row in rows
    )

    await callback.message.edit_text(
        "🔗 TELEGRAM BUSINESS\n\n"
        f"Активных подключений: {active}\n"
        f"Подключений с правом ответа: {can_reply}\n\n"
        "1. Открой настройки Telegram Business.\n"
        "2. Найди раздел чат-ботов.\n"
        "3. Выбери своего бота.\n"
        "4. Выдай только необходимые разрешения.\n"
        "5. Выбери чаты, к которым разрешён доступ.\n\n"
        "После подключения Telegram отправит событие боту.\n"
        "Если подключение не появилось, проверь Business Mode "
        "в @BotFather и журнал GitHub Actions.",
        reply_markup=back_menu(),
    )
    await callback.answer()


@dp.callback_query(F.data == "autoreply")
async def autoreply_info(callback: CallbackQuery):
    user = get_user(callback.from_user.id)

    await callback.message.edit_text(
        "🤖 АВТООТВЕТ\n\n"
        f"Статус: {'Включён' if user['auto_reply'] else 'Выключен'}\n\n"
        "Текст ответа:\n"
        f"{user['reply_text']}\n\n"
        "Автоответ отправляется только на сообщения, "
        "полученные через активное Business-подключение, "
        "при наличии разрешения на ответ.",
        reply_markup=toggle_menu(user),
    )
    await callback.answer()


@dp.callback_query(F.data == "history")
async def history_info(callback: CallbackQuery):
    user = get_user(callback.from_user.id)

    with db() as conn:
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM events WHERE owner_id = ?",
            (callback.from_user.id,),
        ).fetchone()["n"]

    await callback.message.edit_text(
        "📚 ЖУРНАЛ СОБЫТИЙ\n\n"
        f"Журнал: {'Включён' if user['history_enabled'] else 'Выключен'}\n"
        f"Сохранённых событий: {count}\n\n"
        "При включении сохраняются новые события, "
        "доступные боту. Старые сообщения автоматически "
        "не загружаются.",
        reply_markup=toggle_menu(user),
    )
    await callback.answer()


@dp.callback_query(F.data == "toggle_auto")
async def toggle_auto(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    new_value = 0 if user["auto_reply"] else 1

    with db() as conn:
        conn.execute(
            "UPDATE users SET auto_reply = ? WHERE user_id = ?",
            (new_value, callback.from_user.id),
        )

    user = get_user(callback.from_user.id)

    await callback.message.edit_reply_markup(
        reply_markup=toggle_menu(user)
    )
    await callback.answer(
        "Автоответ включён" if new_value else "Автоответ выключен"
    )


@dp.callback_query(F.data == "toggle_history")
async def toggle_history(callback: CallbackQuery):
    user = get_user(callback.from_user.id)
    new_value = 0 if user["history_enabled"] else 1

    with db() as conn:
        conn.execute(
            "UPDATE users SET history_enabled = ? WHERE user_id = ?",
            (new_value, callback.from_user.id),
        )

    user = get_user(callback.from_user.id)

    await callback.message.edit_reply_markup(
        reply_markup=toggle_menu(user)
    )
    await callback.answer(
        "Журнал включён" if new_value else "Журнал выключен"
    )


@dp.callback_query(F.data == "stats")
async def stats(callback: CallbackQuery):
    with db() as conn:
        users = conn.execute(
            "SELECT COUNT(*) AS n FROM users"
        ).fetchone()["n"]

        connections = conn.execute(
            "SELECT COUNT(*) AS n FROM connections WHERE enabled = 1"
        ).fetchone()["n"]

        events = conn.execute(
            "SELECT COUNT(*) AS n FROM events WHERE owner_id = ?",
            (callback.from_user.id,),
        ).fetchone()["n"]

    await callback.message.edit_text(
        "📊 СТАТИСТИКА\n\n"
        f"Пользователей бота: {users}\n"
        f"Активных Business-подключений: {connections}\n"
        f"Событий в твоём журнале: {events}",
        reply_markup=back_menu(),
    )
    await callback.answer()


@dp.callback_query(F.data == "help")
async def help_info(callback: CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ ИНСТРУКЦИЯ\n\n"
        "1. Нажми /start.\n"
        "2. Открой настройки Telegram Business.\n"
        "3. Подключи этого бота и выбери разрешённые чаты.\n"
        "4. Проверь подключение в разделе Business.\n"
        "5. Включи автоответ, если он нужен.\n\n"
        "Не отправляй боту пароль Telegram, код входа "
        "или QR-код авторизации.",
        reply_markup=back_menu(),
    )
    await callback.answer()


@dp.business_connection()
async def business_connection_update(
    connection: BusinessConnection,
):
    owner_id = connection.user.id

    register_user(owner_id, connection.user.username)

    rights = connection.rights
    can_reply = bool(rights and getattr(rights, "can_reply", False))

    with db() as conn:
        conn.execute("""
            INSERT INTO connections (
                connection_id, owner_id, enabled, can_reply
            ) VALUES (?, ?, ?, ?)
            ON CONFLICT(connection_id) DO UPDATE SET
                owner_id = excluded.owner_id,
                enabled = excluded.enabled,
                can_reply = excluded.can_reply
        """, (
            connection.id,
            owner_id,
            int(connection.is_enabled),
            int(can_reply),
        ))

    logging.info(
        "Business connection updated: owner=%s enabled=%s",
        owner_id,
        connection.is_enabled,
    )


@dp.business_message()
async def business_message(message: Message, bot: Bot):
    connection_id = message.business_connection_id

    if not connection_id:
        return

    connection = get_connection(connection_id)

    if not connection or not connection["enabled"]:
        return

    owner_id = connection["owner_id"]
    user = get_user(owner_id)

    text = message.text or message.caption or ""

    if user["history_enabled"]:
        save_event(
            owner_id,
            connection_id,
            "new_message",
            message.chat.id,
            message.message_id,
            text[:4000],
        )

    if not user["auto_reply"]:
        return

    if not connection["can_reply"]:
        logging.warning(
            "Auto-reply skipped: missing reply permission"
        )
        return

    # Avoid replying to outgoing messages sent by the account owner.
    if message.from_user and message.from_user.id == owner_id:
        return

    # Basic safeguard: reply only to incoming private messages.
    if message.chat.type != "private":
        return

    try:
        await bot.send_message(
            chat_id=message.chat.id,
            text=user["reply_text"],
            business_connection_id=connection_id,
        )
    except Exception:
        logging.exception("Failed to send Business auto-reply")


@dp.edited_business_message()
async def edited_business_message(message: Message):
    connection_id = message.business_connection_id

    if not connection_id:
        return

    connection = get_connection(connection_id)

    if not connection or not connection["enabled"]:
        return

    user = get_user(connection["owner_id"])

    if user["history_enabled"]:
        save_event(
            connection["owner_id"],
            connection_id,
            "edited_message",
            message.chat.id,
            message.message_id,
            (message.text or message.caption or "")[:4000],
        )


@dp.deleted_business_messages()
async def deleted_business_messages(
    deleted: BusinessMessagesDeleted,
):
    connection_id = deleted.business_connection_id
    connection = get_connection(connection_id)

    if not connection or not connection["enabled"]:
        return

    user = get_user(connection["owner_id"])

    if not user["history_enabled"]:
        return

    for message_id in deleted.message_ids:
        save_event(
            connection["owner_id"],
            connection_id,
            "deleted_message",
            deleted.chat.id,
            message_id,
            None,
        )


async def main():
    logging.basicConfig(level=logging.INFO)
    init_db()

    bot = Bot(token=TOKEN)

    try:
        await dp.start_polling(
            bot,
            allowed_updates=[
                "message",
                "callback_query",
                "business_connection",
                "business_message",
                "edited_business_message",
                "deleted_business_messages",
            ],
        )
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
