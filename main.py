import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message
from database import init_db
import aiosqlite

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    print("ОШИБКА: Не найден токен бота!")
else:
    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    @dp.startup()
    async def on_startup(bot: Bot):
        await init_db()
        logging.info("Бот Remember запущен.")

    @dp.message(Command("start"))
    async def cmd_start(message: Message):
        await message.answer("👋 Привет! Я Remember.\nПерешли мне сообщение, чтобы сохранить.")

    @dp.message(F.forward_from)
    async def save_forwarded(message: Message):
        user_id = message.from_user.id
        fwd_message = message.forward_from
        
        content_type = "text"
        text_content = message.text or message.caption or ""
        file_id = None
        
        if message.photo:
            content_type = "photo"
            file_id = message.photo[-1].file_id
        elif message.video:
            content_type = "video"
            file_id = message.video.file_id
            
        async with aiosqlite.connect('remember.db') as db:
            await db.execute(
                'INSERT INTO saved_items (user_id, message_id, content_type, text_content, file_id, tags) VALUES (?, ?, ?, ?, ?, ?)',
                (user_id, fwd_message.message_id, content_type, text_content, file_id, "")
            )
            await db.commit()
        await message.answer("✅ Сохранено!")

    @dp.message(Command("help"))
    async def cmd_help(message: Message):
        await message.answer("/search [текст] - поиск\nПросто перешли сообщение для сохранения.")

    async def main():
        await dp.start_polling(bot)

    if __name__ == "__main__":
        import asyncio
        asyncio.run(main())
