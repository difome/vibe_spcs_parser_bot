import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from config import settings
from handlers.inline import router as inline_router
from handlers.messages import router as messages_router
from services.spaces import load_and_save_cookies

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Запуск бота"""
    logger.info("Инициализация бота...")

    # Инициализация бота и диспетчера
    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Подключение роутеров
    dp.include_router(messages_router)
    dp.include_router(inline_router)

    # Загрузка/обновление куки перед запуском
    logger.info("Загрузка куки...")
    await load_and_save_cookies()

    logger.info("Бот запущен и готов к работе")

    # Запуск поллинга
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен")
    except Exception as e:
        logger.critical(f"Критическая ошибка при запуске: {e}", exc_info=True)
