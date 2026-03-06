from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Dict

class Settings(BaseSettings):
    # Bot settings
    bot_token: str = Field(alias="BOT_TOKEN")
    tm_init_url: str = Field(alias="TM_INIT_URL")
    bot_link: str = Field(alias="BOT_LINK")
    bot_username: str = Field(alias="BOT_USERNAME")
    cache_chat_id: int = Field(alias="CACHE_CHAT_ID", default=0)

    # Files
    cookies_json_file: str = "spaces_cookies.json"
    categories_json_file: str = "categories.json"

    # Base URLs
    spaces_base_url: str = Field(default="https://spaces.im", alias="SPACES_BASE_URL")
    categories_base_url: str = f"{spaces_base_url}/sz/muzyka/"
    search_base_url: str = f"{spaces_base_url}/music-online/search/"
    files_search_base_url: str = f"{spaces_base_url}/search/"
    files_search_results_url: str = f"{spaces_base_url}/files/search/"

    # Headers
    spaces_headers: Dict[str, str] = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
    }

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
