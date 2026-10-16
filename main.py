
import asyncio
import logging
import os
import re
import sqlite3
from datetime import datetime, timezone

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    Message,
    BusinessConnection,
    BusinessMessagesDeleted,
)

TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
DB_PATH = os.getenv("DB_PATH", "bot.sqlite3")

if not TOKEN:
    raise RuntimeError("Set BOT_TOKEN in GitHub Secrets")

if not OWNER_ID:
    raise RuntimeError("Set OWNER_ID in GitHub Secrets")

dp = Dispatcher()
MAX_REPEAT = 3
MAX_TEXT_LENGTH = 1000


def connect_db():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with connect_db() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS connections (
            connection_id TEXT PRIMARY KEY,
            owner_id INTEGER NOT NULL,
            enabled INTEGER NOT NULL DEFAULT 0,
            can_reply INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS saved_messages (
            connection_id TEXT NOT NULL,
            chat_id INTEGER NOT NULL,
            message_id INTEGER NOT NULL,
            sender_id INTEGER,
            message_text TEXT,
            saved_at TEXT NOT NULL,
            PRIMARY KEY (connection_id, chat_id, message_id)
        );
        """)


def get_connection(connection_id):
    with connect_db() as conn:
        row = conn.execute(
            """SELECT * FROM connections
               WHERE connection_id = ?""",
            (connection_id,),
        ).fetchone()
    return dict(row) if row else None


def save_message(connection_id, chat_id, message_id,
                 sender_id, text):
    with connect_db() as conn:
        conn.execute("""
            INSERT INTO saved_messages (
                connection_id, chat_id, message_id,
                sender_id, message_text, saved_at
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(connection_id, chat_id, message_id)
            DO UPDATE SET
                sender_id = excluded.sender_id,
                message_text = excluded.message_text,
                saved_at = excluded.saved_at
        """, (
            connection_id,
            chat_id,
            message_id,
            sender_id,
            text[:4000],
            datetime.now(timezone.utc).isoformat(),
        ))


def get_saved_message(connection_id, chat_id, message_id):
    with connect_db() as conn:
        row = conn.execute("""
            SELECT message_text FROM saved_messages
            WHERE connection_id = ?
              AND chat_id = ?
              AND message_id = ?
        """, (connection_id, chat_id, message_id)).fetchone()

    return row["message_text"] if row else None


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Бот запущен.\n\n"
        "Команды:\n"
        "/repeat 3 Текст — повторить сообщение до 3 раз\n"
        "/help — инструкция\n\n"
        "Business-сообщения обрабатываются только "
        "при активном разрешённом подключении."
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Использование:\n"
        "/repeat 3 Привет!\n\n"
        "Повторение ограничено тремя сообщениями за команду. "
        "Команда работает только в личном чате с ботом "
        "и не рассылает сообщения другим пользователям.\n\n"
        "Business-журнал сохраняет тексты сообщений, "
        "которые бот получил через разрешённое подключение."
    )


@dp.message(Command("repeat"))
async def repeat_command(message: Message, bot: Bot):
    # Repeat commands are accepted only in a private chat
    # with this bot, not in chats with other people.
    if message.chat.type != "private":
        await message.answer(
            "Используй /repeat в личном чате с ботом."
        )
        return

    if message.from_user.id != OWNER_ID:
        await message.answer("Эта команда недоступна.")
        return

    raw = message.text or ""
    match = re.match(r"^/repeat(?:@\w+)?\s+(\d+)\s+(.+)$",
                     raw, flags=re.DOTALL)

    if not match:
        await message.answer(
            "Формат: /repeat 3 Текст сообщения"
        )
        return

    count = int(match.group(1))
    text = match.group(2).strip()

    if not 1 <= count <= MAX_REPEAT:
        await message.answer(
            f"Количество должно быть от 1 до {MAX_REPEAT}."
        )
        return

    if not text or len(text) > MAX_TEXT_LENGTH:
        await message.answer(
            f"Текст должен содержать не более "
            f"{MAX_TEXT_LENGTH} символов."
        )
        return

    for _ in range(count):
        await bot.send_message(
            chat_id=message.chat.id,
            text=text,
        )
        await asyncio.sleep(1)

    await message.answer(f"Готово: отправлено {count} сообщений.")


@dp.business_connection()
async def business_connection_update(
    connection: BusinessConnection,
):
    rights = connection.rights

    can_reply = bool(
        rights and getattr(rights, "can_reply", False)
    )

    with connect_db() as conn:
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
            connection.user.id,
            int(connection.is_enabled),
            int(can_reply),
        ))

    logging.info(
        "Business connection updated: enabled=%s",
        connection.is_enabled,
    )


@dp.business_message()
async def handle_business_message(message: Message):
    connection_id = message.business_connection_id

    if not connection_id:
        return

    connection = get_connection(connection_id)

    if not connection or not connection["enabled"]:
        return

    # Save only messages from the Business connection
    # that the bot is permitted to receive.
    text = message.text or message.caption

    if text:
        save_message(
            connection_id,
            message.chat.id,
            message.message_id,
            message.from_user.id if message.from_user else None,
            text,
        )


@dp.edited_business_message()
async def handle_edited_business_message(message: Message):
    connection_id = message.business_connection_id

    if not connection_id:
        return

    connection = get_connection(connection_id)

    if not connection or not connection["enabled"]:
        return

    text = message.text or message.caption

    if text:
        save_message(
            connection_id,
            message.chat.id,
            message.message_id,
            message.from_user.id if message.from_user else None,
            text,
        )


@dp.deleted_business_messages()
async def handle_deleted_business_messages(
    event: BusinessMessagesDeleted,
    bot: Bot,
):
    connection_id = event.business_connection_id
    connection = get_connection(connection_id)

    if not connection or not connection["enabled"]:
        return

    # Only notify the configured owner of this bot.
    if connection["owner_id"] != OWNER_ID:
        return

    for message_id in event.message_ids:
        saved_text = get_saved_message(
            connection_id,
            event.chat.id,
            message_id,
        )

        if saved_text is None:
            body = (
                "Telegram сообщил об удалении сообщения, "
                "но его текст не был сохранён заранее.\n"
                f"Chat ID: {event.chat.id}\n"
                f"Message ID: {message_id}"
            )
        else:
            body = (
                "Получено уведомление об удалении сообщения.\n\n"
                f"Chat ID: {event.chat.id}\n"
                f"Message ID: {message_id}\n\n"
                "Сохранённый текст:\n"
                f"{saved_text}"
            )

        try:
            await bot.send_message(OWNER_ID, body[:4000])
        except Exception:
            logging.exception("Could not send deletion notification")


async def main():
    logging.basicConfig(level=logging.INFO)
    init_db()

    bot = Bot(TOKEN)

    try:
        await dp.start_polling(
            bot,
            allowed_updates=[
                "message",
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
