# Spaces.im Backup Tool

Web application for backing up files from spaces.im

## Features

### Implemented

- ✅ Authentication via cookies (Netscape Cookie File)
- ✅ Automatic detection of user sections (Photos, Music, Video, Files)
- ✅ Section selection for backup
- ✅ Recursive folder and subfolder scanning
- ✅ File parsing from all sections (photos, music, files)
- ✅ Pagination handling during scanning
- ✅ Password-protected folder skipping
- ✅ Download link extraction from file pages (if direct link is unavailable)
- ✅ Two save modes:
  - Folder structure (preserves hierarchy)
  - All files in one folder (flat structure)
- ✅ Direct file saving via server-side download
- ✅ Download progress with speed display
- ✅ Progress by file count and size
- ✅ File list with pagination
- ✅ Retry download for failed files
- ✅ Files saved immediately after download (doesn't wait for all to complete)
- ✅ Cookie and user data storage in localStorage
- ✅ Collapsible authorization panel
- ✅ Reset scan results button
- ✅ Debug console for troubleshooting

### Not Implemented

- ❌ Video downloading
- ❌ Resuming interrupted downloads
- ❌ Downloaded file integrity check

## Usage

### Installation

```bash
npm install
```

### Running

```bash
npm start
```

3. Open browser at `http://localhost:5173`

### How to Use

1. **Authentication:**
   - Copy the `sid` cookie value
   - Paste it into the "SID" field
   - Click "Войти" (Login)
   - The application will automatically detect your sections

2. **Section Selection:**
   - Select sections for backup (Photos, Music, Video, Files)
   - Multiple sections can be selected

3. **Scanning:**
   - Click "Сканировать файлы" (Scan Files)
   - Wait for scanning to complete
   - Review the list of found files

4. **Saving:**
   - Select save mode (Folder Structure or All Files in One Folder)
   - Click "Сохранить" (Save)
   - Wait for download to complete

5. **Retry on Errors:**
   - If a file failed to download, click "Повторить" (Retry) next to the file
   - The file will be downloaded and saved separately

## Technologies

- Vue 3 + TypeScript
- Pinia (state management)
- Vite
- Tailwind CSS
- Cheerio (HTML parsing)
- Express.js (proxy server)
- Vitest (testing)

## Project Structure

```
backup-app/
├── src/
│   ├── components/     # Vue components
│   ├── stores/         # Pinia stores
│   ├── utils/          # Utility functions
│   ├── types/          # TypeScript types
│   └── App.vue         # Main component
├── server.js           # Proxy server for CORS bypass
└── package.json
```

## Notes

- Cookies are saved in browser localStorage
- Modern browser required (Chrome, Edge, Firefox)
- Proxy server is necessary for CORS bypass
- Files are saved directly to server downloads folder

---

# Spaces.im Backup Tool

Веб-приложение для резервного копирования файлов с spaces.im

## Возможности

### Реализовано

- ✅ Авторизация через cookies (Netscape Cookie File)
- ✅ Автоматическое определение разделов пользователя (Фотографии, Музыка, Видео, Файлы)
- ✅ Выбор разделов для резервного копирования
- ✅ Рекурсивное сканирование папок и подпапок
- ✅ Парсинг файлов из всех разделов (фотографии, музыка, файлы)
- ✅ Обработка пагинации при сканировании
- ✅ Пропуск папок с паролем
- ✅ Извлечение ссылок на скачивание со страниц файлов (если прямой ссылки нет)
- ✅ Два режима сохранения:
  - Структура папок (сохраняет иерархию)
  - Все файлы в одну папку (плоская структура)
- ✅ Сохранение файлов напрямую через сервер
- ✅ Прогресс скачивания с отображением скорости
- ✅ Прогресс по количеству файлов и размеру
- ✅ Список файлов с пагинацией
- ✅ Повторная попытка скачивания для файлов с ошибками
- ✅ Сохранение файлов сразу после скачивания (не ждет завершения всех)
- ✅ Сохранение cookies и данных пользователя в localStorage
- ✅ Сворачиваемая панель авторизации
- ✅ Кнопка сброса результатов сканирования
- ✅ Консоль отладки для диагностики

### Не реализовано

- ❌ Скачивание видео
- ❌ Возобновление прерванного скачивания
- ❌ Проверка целостности скачанных файлов

## Использование

### Установка

```bash
npm install
```

### Запуск

```bash
npm start
```

3. Откройте браузер по адресу `http://localhost:5173`

### Как использовать

1. **Авторизация:**
   - Скопируйте cookie значение sid
   - Вставьте в поле "SID"
   - Нажмите "Войти"
   - Приложение автоматически определит ваши разделы

2. **Выбор разделов:**
   - Выберите разделы для резервного копирования (Фотографии, Музыка, Видео, Файлы)
   - Можно выбрать несколько разделов

3. **Сканирование:**
   - Нажмите "Сканировать файлы"
   - Дождитесь завершения сканирования
   - Просмотрите список найденных файлов

4. **Сохранение:**
   - Выберите режим сохранения (Структура папок или Все файлы в одну папку)
   - Нажмите "Сохранить"
   - Дождитесь завершения скачивания

5. **Повтор при ошибках:**
   - Если файл не скачался, нажмите кнопку "Повторить" рядом с файлом
   - Файл будет скачан и сохранен отдельно

## Технологии

- Vue 3 + TypeScript
- Pinia (управление состоянием)
- Vite
- Tailwind CSS
- Cheerio (парсинг HTML)
- Express.js (прокси-сервер)
- Vitest (тестирование)

## Структура проекта

```
backup-app/
├── src/
│   ├── components/     # Vue компоненты
│   ├── stores/         # Pinia stores
│   ├── utils/          # Вспомогательные функции
│   ├── types/          # TypeScript типы
│   └── App.vue         # Главный компонент
├── server.js           # Прокси-сервер для обхода CORS
└── package.json
```

## Примечания

- Cookies сохраняются в localStorage браузера
- Требуется современный браузер (Chrome, Edge, Firefox)
- Прокси-сервер необходим для обхода CORS ограничений
- Файлы сохраняются напрямую в папку downloads на сервере
