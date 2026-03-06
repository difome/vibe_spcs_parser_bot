import logging
from aiogram import Router, types
from aiogram.filters import Command
from config import settings

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("start"))
async def start_handler(message: types.Message):
    """Обработчик команды /start"""
    text = (
        "👋 <b>Привет! Я бот для поиска медиа-контента из Spaces.</b>\n\n"
        "Я работаю преимущественно в <b>Inline-режиме</b>. Это значит, что ты можешь искать музыку, видео и фото прямо в любом чате!\n\n"
        "🔍 <b>Как пользоваться:</b>\n"
        "Просто напиши в поле ввода сообщения юзернейм бота и свой запрос:\n"
        f"<code>@{settings.bot_username} твой запрос</code>\n\n"
        "⌨️ <b>Префиксы для поиска:</b>\n"
        f"🎧 <code>@{settings.bot_username} музыка </code> ваш запрос — Поиск музыки (файлы)\n"
        f"🎬 <code>@{settings.bot_username} видео </code> ваш запрос — Поиск видео\n"
        f"🖼 <code>@{settings.bot_username} фото </code> ваш запрос — Поиск картинок и фото\n"
        f"🎵<code>@{settings.bot_username}</code> <i>Без префикса</i> — Общий поиск музыки\n\n"
        "Попробуй прямо сейчас!"
    )

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="🔎 Попробовать поиск", switch_inline_query_current_chat="")]
    ])

    await message.answer(text, reply_markup=keyboard, parse_mode="HTML")

@router.message(Command("help"))
async def help_handler(message: types.Message):
    """Обработчик команды /help"""
    await start_handler(message)
