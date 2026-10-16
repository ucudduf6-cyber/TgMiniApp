
import os
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

TOKEN = os.getenv("BOT_TOKEN")
DB_NAME = "remember.db"

if not TOKEN:
    raise RuntimeError("Не задан BOT_TOKEN в Secrets")

bot = Bot(token=TOKEN)
dp = Dispatcher()


def init_db():
    with sqlite3.connect(DB_NAME) as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS saved (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL
            )
        """)


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет! Я Remember 🧠\n\n"
        "Отправь мне текст, ссылку или перешли сообщение — "
        "я сохраню его.\n\n"
        "/my — мои сохранения\n"
        "/get ID — открыть сохранение\n"
        "/delete ID — удалить сохранение"
    )


@dp.message(Command("help"))
async def help_command(message: Message):
    await start(message)


@dp.message(Command("my"))
async def my_saves(message: Message):
    with sqlite3.connect(DB_NAME) as db:
        rows = db.execute(
            "SELECT id, content FROM saved "
            "WHERE user_id = ? ORDER BY id DESC LIMIT 20",
            (message.from_user.id,)
        ).fetchall()

    if not rows:
        await message.answer("Пока сохранений нет.")
        return

    result = ["Твои последние сохранения:"]
    for item_id, content in rows:
        preview = content.replace("\n", " ")[:100]
        result.append(f"{item_id}. {preview}")

    await message.answer("\n".join(result))


@dp.message(Command("get"))
async def get_save(message: Message):
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Использование: /get ID")
        return

    item_id = int(parts[1])
    with sqlite3.connect(DB_NAME) as db:
        row = db.execute(
            "SELECT content FROM saved WHERE id = ? AND user_id = ?",
            (item_id, message.from_user.id)
        ).fetchone()

    if row:
        await message.answer(row[0])
    else:
        await message.answer("Сохранение не найдено.")


@dp.message(Command("delete"))
async def delete_save(message: Message):
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Использование: /delete ID")
        return

    with sqlite3.connect(DB_NAME) as db:
        cursor = db.execute(
            "DELETE FROM saved WHERE id = ? AND user_id = ?",
            (int(parts[1]), message.from_user.id)
        )
        deleted = cursor.rowcount
        db.commit()

    await message.answer(
        "Удалено." if deleted else "Сохранение не найдено."
    )


@dp.message(F.text)
async def save_text(message: Message):
    content = message.text or ""
    if content.startswith("/"):
        return

    with sqlite3.connect(DB_NAME) as db:
        cursor = db.execute(
            "INSERT INTO saved (user_id, content) VALUES (?, ?)",
            (message.from_user.id, content)
        )
        item_id = cursor.lastrowid
        db.commit()

    await message.answer(f"Сохранено ✅ ID: {item_id}")


async def main():
    init_db()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
