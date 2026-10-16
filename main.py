# Добавь это в main.py перед функцией main()

from aiogram.types import WebAppInfo

# Обновленная команда /start с кнопкой открытия сайта
@dp.message(Command("start"))
async def cmd_start(message: Message):
    # Ссылка на твой сайт (замени на свою реальную ссылку из Шага 2)
    site_url = "https://твой-ник.github.io/remember-bot/" 
    
    kb = [
        [types.KeyboardButton(text="🚀 Открыть Remember", web_app=WebAppInfo(url=site_url))]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)
    
    await message.answer(
        "Привет! Я Remember.\nНажми кнопку ниже, чтобы открыть приложение.",
        reply_markup=keyboard
    )

# Обработка данных, пришедших от сайта
@dp.message(lambda msg: msg.web_app_data is not None)
async def handle_webapp_data(message: Message):
    data = message.web_app_data.data
    # Здесь можно парсить JSON и выполнять действия
    await message.answer(f"Получено действие из приложения: {data}")
