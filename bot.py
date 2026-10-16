
import asyncio
import os
import re
import aiosqlite

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

TOKEN = os.getenv("8809988539:AAEtJ7IJJMTx1Ibcxi-XeWorIGbjiFEUIrw")
if not TOKEN:
    raise RuntimeError("Set the BOT_TOKEN environment variable first.")

DB_PATH = "remember.db"

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS saved_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                kind TEXT NOT NULL,
                content TEXT NOT NULL DEFAULT '',
                file_id TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE INDEX IF NOT EXISTS idx_saved_user
            ON saved_items(user_id, id DESC)
        """)
        await db.commit()


def get_media(message: Message):
    if message.photo:
        return "photo", message.photo[-1].file_id
    for kind in (
        "video", "document", "audio", "voice",
        "animation", "video_note", "sticker"
    ):
        obj = getattr(message, kind, None)
        if obj:
            return kind, obj.file_id
    return None, None


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в Remember!\n\n"
        "Отправь мне ссылку, текст, фото, видео или файл — "
        "и я сохраню запись в твоём личном архиве.\n\n"
        "/my — последние записи\n"
        "/get ID — получить запись\n"
        "/delete ID — удалить запись\n"
        "/help — помощь"
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await message.answer(
        "Как пользоваться Remember:\n\n"
        "• Отправляй текст и ссылки для сохранения.\n"
        "• Отправляй фото, видео, голосовые и документы.\n"
        "• /my — посмотреть последние записи.\n"
        "• /get ID — открыть сохранённую запись.\n"
        "• /delete ID — удалить свою запись.\n\n"
        "Записи доступны только тому Telegram-пользователю, "
        "который их сохранил."
    )


@dp.message(Command("my"))
async def my_items(message: Message):
    user_id = message.from_user.id

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT id, kind, content, created_at
            FROM saved_items
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 10
        """, (user_id,))
        rows = await cursor.fetchall()

    if not rows:
        await message.answer("Пока записей нет. Отправь мне что-нибудь!")
        return

    lines = ["📚 Твои последние записи:\n"]
    for item_id, kind, content, created_at in rows:
        preview = (content or "").replace("\n", " ")[:100]
        if not preview:
            preview = f"[{kind}]"
        lines.append(f"#{item_id} · {kind}\n{preview}\n")
    lines.append("Открыть: /get ID\nУдалить: /delete ID")

    await message.answer("\n".join(lines))


@dp.message(Command("get"))
async def get_item(message: Message):
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Используй: /get ID")
        return

    item_id = int(parts[1])
    user_id = message.from_user.id

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            SELECT kind, content, file_id
            FROM saved_items
            WHERE id = ? AND user_id = ?
        """, (item_id, user_id))
        row = await cursor.fetchone()

    if not row:
        await message.answer("Запись не найдена в твоём архиве.")
        return

    kind, content, file_id = row

    if file_id:
        try:
            if kind == "photo":
                await message.answer_photo(file_id, caption=content or None)
            elif kind == "video":
                await message.answer_video(file_id, caption=content or None)
            elif kind == "document":
                await message.answer_document(file_id, caption=content or None)
            elif kind == "audio":
                await message.answer_audio(file_id, caption=content or None)
            elif kind == "voice":
                await message.answer_voice(file_id, caption=content or None)
            elif kind == "animation":
                await message.answer_animation(file_id, caption=content or None)
            elif kind == "video_note":
                await message.answer_video_note(file_id)
            elif kind == "sticker":
                await message.answer_sticker(file_id)
            else:
                await message.answer(content or f"Тип записи: {kind}")
        except Exception:
            await message.answer(
                "Не удалось отправить этот файл. Возможно, "
                "Telegram больше не принимает сохранённый file_id."
            )
    else:
        await message.answer(content or "(Пустая запись)")


@dp.message(Command("delete"))
async def delete_item(message: Message):
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Используй: /delete ID")
        return

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            DELETE FROM saved_items
            WHERE id = ? AND user_id = ?
        """, (int(parts[1]), message.from_user.id))
        await db.commit()

    if cursor.rowcount:
        await message.answer("🗑 Запись удалена.")
    else:
        await message.answer("Запись не найдена в твоём архиве.")


@dp.message()
async def save_item(message: Message):
    if not message.from_user:
        return

    kind, file_id = get_media(message)
    content = message.text or message.caption or ""

    if not content and not file_id:
        await message.answer("Этот тип сообщения пока не поддерживается.")
        return

    # Не сохраняем команды как обычные записи.
    if message.text and message.text.startswith("/"):
        return

    if not kind:
        kind = "text"

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute("""
            INSERT INTO saved_items (user_id, kind, content, file_id)
            VALUES (?, ?, ?, ?)
        """, (message.from_user.id, kind, content, file_id))
        await db.commit()
        item_id = cursor.lastrowid

    await message.answer(
        f"✅ Сохранено в Remember!\nID записи: {item_id}\n"
        f"Открыть: /get {item_id}"
    )


async def main():
    await init_db()
    print("Remember запущен.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
