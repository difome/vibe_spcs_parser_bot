# Vibe Spaces

Collection of tools for working with spaces.im platform.

## Projects

### backup-app

Web application for backing up files from spaces.im. Built with Vue 3, TypeScript, and Pinia.

**Features:**
- File backup from user sections (Photos, Music, Video, Files)
- Recursive folder scanning
- Two save modes (folder structure or flat)
- Progress tracking and error handling

See [backup-app/README.md](./backup-app/README.md) for details.

### bot

Telegram inline bot for searching and sharing content from spaces.im.

**Features:**
- Music search by query
- Browse music by categories
- Search images and videos
- Inline query support

See [bot/README.md](./bot/README.md) for details.

## Requirements

- Node.js 18+ (for backup-app)
- Python 3.8+ (for bot)

## Installation

### backup-app

```bash
cd backup-app
npm install
npm start
```

### bot

```bash
cd bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## License

MIT

---

# Vibe Spaces

Набор инструментов для работы с платформой spaces.im.

## Проекты

### backup-app

Веб-приложение для резервного копирования файлов с spaces.im. Построено на Vue 3, TypeScript и Pinia.

**Возможности:**
- Резервное копирование файлов из разделов пользователя (Фотографии, Музыка, Видео, Файлы)
- Рекурсивное сканирование папок
- Два режима сохранения (структура папок или плоская структура)
- Отслеживание прогресса и обработка ошибок

Подробности в [backup-app/README.md](./backup-app/README.md).

### bot

Telegram inline бот для поиска и обмена контентом с spaces.im.

**Возможности:**
- Поиск музыки по запросу
- Просмотр музыки по категориям
- Поиск изображений и видео
- Поддержка inline запросов

Подробности в [bot/README.md](./bot/README.md).

## Требования

- Node.js 18+ (для backup-app)
- Python 3.8+ (для bot)

## Установка

### backup-app

```bash
cd backup-app
npm install
npm start
```

### bot

```bash
cd bot
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Лицензия

MIT

