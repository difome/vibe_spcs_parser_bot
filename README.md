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

