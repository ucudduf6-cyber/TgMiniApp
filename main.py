import os
import logging
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, ChatMemberUpdated
from database import init_db, log_event, get_events
import aiosqlite
from datetime import datetime

logging.basicConfig(level=logging.INFO)
TOKEN = "СЮДА_ВСТАВЬ_ТОКЕН" # Вставь токен напрямую для простоты
ADMIN_ID = ТВОЙ_ID_ТЕЛЕГРАМ # Твой ID для тестов

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.startup()
async def on_startup(bot: Bot):
    await init_db()
    logging.info("Business Monitor Bot запущен.")

# Логирование удаления сообщений
@dp.deleted_message()
async def handle_delete(event: types.DeletedMessage):
    user = event.from_user
    chat = event.chat
    text = event.text or "[Медиа/Файл]"
    
    msg = f"🗑 Удалено: {user.full_name} ({user.id})\nЧат: {chat.title}\nТекст: {text}"
    await log_event(chat.id, "DELETE", user.id, user.full_name, text)
    
    # Можно дублировать админу чата (если он известен), но пока пишем в БД

# Логирование редактирования сообщений
@dp.edited_message()
async def handle_edit(message: Message):
    user = message.from_user
    chat = message.chat
    old_text = "..." # В aiogram сложно получить старый текст без кэша, но факт редактирования важен
    new_text = message.text or "[Медиа]"
    
    await log_event(chat.id, "EDIT", user.id, user.full_name, f"Изменено на: {new_text}")

# Логирование входа/выхода
@dp.chat_member()
async def handle_chat_member_update(update: ChatMemberUpdated):
    if update.new_chat_member.status in ["member", "administrator"]:
        action = "JOIN"
    else:
        action = "LEAVE"
    
    user = update.new_chat_member.user
    await log_event(update.chat.id, action, user.id, user.full_name, f"Статус: {update.new_chat_member.status}")

# Команда /start с кнопкой Дашборда
@dp.message(Command("start"))
async def cmd_start(message: Message):
    # Ссылка на твой сайт-дашборд
    dashboard_url = "https://твой-ник.github.io/remember-bot/dashboard.html"
    
    kb = [[types.InlineKeyboardButton(text=" Открыть Дашборд логов", url=dashboard_url)]]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=kb)
    
    await message.answer(
        "Я Business Monitor. Я слежу за порядком в чате.\n"
        "Все удаления и изменения сохраняются.\n"
        "Нажмите кнопку ниже, чтобы посмотреть отчет.",
        reply_markup=keyboard
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
