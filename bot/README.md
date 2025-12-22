# Vibe Spaces Bot

A Telegram inline bot for searching and sharing music, images, and videos from spaces.im.

## Features

- Search music tracks by query
- Browse music by categories
- Search images and videos
- Inline query support for easy sharing

## Requirements

- Python 3.8+
- Telegram Bot Token

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd vibe_spcs
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the bot:
   - Set your `BOT_TOKEN` in `main.py`
   - Add cookies to `spaces_cookies.json` if needed

## Usage

Run the bot:
```bash
python main.py
```

The bot supports inline queries. Users can search for music, images, and videos directly from any chat.

## Files

- `main.py` - Main bot application
- `categories.json` - Music categories configuration
- `spaces_cookies.json` - Cookies for spaces.im authentication
- `requirements.txt` - Python dependencies

## License

MIT

---

# Vibe Spaces Bot

Telegram inline бот для поиска и обмена музыкой, изображениями и видео с spaces.im.

## Возможности

- Поиск музыкальных треков по запросу
- Просмотр музыки по категориям
- Поиск изображений и видео
- Поддержка inline запросов для удобного обмена

## Требования

- Python 3.8+
- Токен Telegram бота

## Установка

1. Клонируйте репозиторий:
```bash
git clone <repository-url>
cd vibe_spcs
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Настройте бота:
   - Установите `BOT_TOKEN` в `main.py`
   - Добавьте cookies в `spaces_cookies.json` при необходимости

## Использование

Запустите бота:
```bash
python main.py
```

Бот поддерживает inline запросы. Пользователи могут искать музыку, изображения и видео прямо из любого чата.

## Файлы

- `main.py` - Основное приложение бота
- `categories.json` - Конфигурация категорий музыки
- `spaces_cookies.json` - Cookies для аутентификации на spaces.im
- `requirements.txt` - Python зависимости

## Лицензия

MIT
