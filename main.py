import asyncio
import os
import logging
import colorlog
import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv
from collections import OrderedDict
from datetime import datetime, timedelta

load_dotenv()

MAX_DIALOG_HISTORY = 10
DIALOG_TIMEOUT = timedelta(hours=1)
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

def setup_logger():
    logger = logging.getLogger("lainairun_bot")
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    formatter = colorlog.ColoredFormatter(
        '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'bold_red',
        }
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler("bot.log", encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()

try:
    openrouter_api_key = os.getenv("openrouter_api_key")
    don_prompt = os.getenv("don_prompt", "")
    if not don_prompt:
        logger.warning("Промпт пустой! Проверьте .env файл")
    else:
        logger.info(f"Длина промпта: {len(don_prompt)} символов")
    bot = Bot(token=os.getenv("tg_token"))
    dp = Dispatcher()
    logger.info(f"Токен бота: {'Установлен' if os.getenv('tg_token') else 'Отсутствует'}")
    logger.info(f"API ключ: {'Установлен' if openrouter_api_key else 'Отсутствует'}")
    logger.info(f"Промпт: {'Установлен' if don_prompt else 'Отсутствует'}")
except Exception as e:
    logger.critical(f"Ошибка инициализации: {e}")
    raise

class DialogMemory:
    def __init__(self, max_size=MAX_DIALOG_HISTORY):
        self.memory = OrderedDict()
        self.max_size = max_size

    def add(self, user_id: int, message: str):
        self.memory[user_id] = {
            'message': message,
            'timestamp': datetime.now()
        }
        if len(self.memory) > self.max_size:
            self.memory.popitem(last=False)

    def get(self, user_id: int) -> str:
        if user_id in self.memory:
            data = self.memory[user_id]
            if datetime.now() - data['timestamp'] > DIALOG_TIMEOUT:
                del self.memory[user_id]
                return ""
            return data['message']
        return ""

    def clear(self, user_id: int = None):
        if user_id:
            self.memory.pop(user_id, None)
        else:
            self.memory.clear()

dialog_memory = DialogMemory()

async def generate_response(prompt: str) -> str:
    if not prompt or len(prompt) > 4000:
        logger.warning("Сообщение слишком длинное или пустое")
        return "Сообщение слишком длинное или пустое"
    
    logger.info("Подготовка запроса к API")
    try:
        headers = {
            "Authorization": f"Bearer {openrouter_api_key}",
            "HTTP-Referer": "https://github.com/cryptexctl/openlain",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "openai/gpt-4.1",
            "messages": [
                {"role": "system", "content": don_prompt},
                {"role": "user", "content": prompt}
            ]
        }
        
        logger.info("Отправка запроса к API")
        async with aiohttp.ClientSession() as session:
            async with session.post(OPENROUTER_API_URL, headers=headers, json=data) as response:
                logger.info(f"Получен ответ от API, статус: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    logger.info("Ответ успешно получен и распарсен")
                    return result["choices"][0]["message"]["content"]
                else:
                    error_text = await response.text()
                    logger.error(f"Ошибка API: {error_text}")
                    return "Произошла ошибка при получении ответа. Пожалуйста, попробуйте позже."
    except Exception as e:
        logger.exception("Ошибка при генерации ответа: %s", e)
        return "Произошла ошибка при получении ответа. Пожалуйста, попробуйте позже."

async def handle_dialog(message: types.Message):
    logger.info("Начало обработки диалога")
    user_id = message.from_user.id
    user_message = message.text
    previous_dialog = dialog_memory.get(user_id)
    logger.info(f"Предыдущий диалог: {previous_dialog}")
    dialog_prompt = f"{don_prompt}\nПредыдущий запрос: {previous_dialog}\nЗапрос пользователя: {user_message}"
    logger.info("Отправка запроса на генерацию ответа")
    response_text = await generate_response(dialog_prompt)
    logger.info(f"Получен ответ: {response_text[:100]}...")
    dialog_memory.add(user_id, user_message)
    return response_text

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.reply("qq, отвечаю только на 'Лейн'+фраза")

@dp.message(Command("clear"))
async def cmd_clear(message: types.Message):
    dialog_memory.clear(message.from_user.id)
    await message.reply("История диалога очищена")

@dp.message()
async def handle_all_messages(message: types.Message):
    logger.info(f"Получено сообщение от {message.from_user.id}: {message.text}")
    if message.text and "лейн" in message.text.lower():
        logger.info("Найдено слово 'лейн', начинаю обработку")
        try:
            response_text = await handle_dialog(message)
            logger.info("Отправка ответа пользователю")
            await message.reply(response_text)
            logger.info("Ответ отправлен")
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
            await message.reply("Произошла ошибка при обработке сообщения")

async def main():
    try:
        logger.info("Бот запущен и ожидает команды...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

