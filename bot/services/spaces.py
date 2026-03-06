import logging
import os
import json
import random
import httpx
import uuid
import aiofiles
from config import settings
from utils.cache import (
    categories_cache,
    tracks_cache,
    picture_search_cache,
    video_files_search_cache,
    music_files_search_cache,
    search_cache
)
from parsers.spaces import (
    parse_categories_from_html,
    parse_pagination_info,
    parse_tracks_from_html,
    parse_files_search_link,
    parse_video_search_link,
    parse_music_search_link,
    parse_videos_from_search,
    parse_music_tracks_from_search,
    parse_pictures_from_html,
    parse_search_form_params,
    get_video_download_url_from_html,
    parse_search_link_id,
    parse_ck
)

logger = logging.getLogger(__name__)

# Dynamic state
SPACES_COOKIES = {}
SPACES_CK = "1"
cookies_loaded = False

async def load_cookies_from_json():
    """Загружает куки из JSON файла (асинхронно)"""
    if not os.path.exists(settings.cookies_json_file):
        return None
    try:
        async with aiofiles.open(settings.cookies_json_file, mode='r', encoding='utf-8') as f:
            content = await f.read()
            cookies = json.loads(content)
            logger.info(f"Куки загружены из JSON: {len(cookies)} шт")
            return cookies
    except Exception as e:
        logger.warning(f"Ошибка загрузки куки из JSON: {e}")
        return None

async def save_cookies_to_json(cookies_dict):
    """Сохраняет куки в JSON файл (асинхронно)"""
    try:
        async with aiofiles.open(settings.cookies_json_file, mode='w', encoding='utf-8') as f:
            await f.write(json.dumps(cookies_dict, indent=2, ensure_ascii=False))
        logger.info("Куки сохранены в JSON")
    except Exception as e:
        logger.error(f"Ошибка сохранения куки в JSON: {e}")

def format_cookies_header(cookies_dict):
    """Форматирует словарь куки в строку для заголовка Cookie"""
    return "; ".join([f"{name}={value}" for name, value in cookies_dict.items()])

def get_request_headers():
    """Возвращает headers с куками для запросов"""
    headers = settings.spaces_headers.copy()
    headers['Cookie'] = format_cookies_header(SPACES_COOKIES)
    return headers

async def fetch_user_ck():
    """Пробует получить CK пользователя с главной страницы"""
    global SPACES_CK
    try:
        async with httpx.AsyncClient(cookies=SPACES_COOKIES, timeout=15.0, follow_redirects=True) as client:
            response = await client.get(settings.spaces_base_url, headers=get_request_headers())
            if response.status_code == 200:
                ck = parse_ck(response.text)
                if ck:
                    SPACES_CK = ck
                    logger.info(f"Найден CK пользователя: {SPACES_CK}")
                    return True
    except Exception as e:
        logger.warning(f"Ошибка получения CK: {e}")
    return False

async def load_and_save_cookies():
    """Загружает куки из JSON или делает запрос для получения новых"""
    global SPACES_COOKIES, cookies_loaded

    loaded_cookies = await load_cookies_from_json()

    if loaded_cookies:
        SPACES_COOKIES.update(loaded_cookies)
        cookies_loaded = True
        await fetch_user_ck()
        return

    logger.info("Куки не найдены, получение через tm URL...")
    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(settings.tm_init_url, headers=settings.spaces_headers, timeout=30.0)
            response.raise_for_status()

            cookies_from_response = {cookie.name: cookie.value for cookie in client.cookies.jar}

            if cookies_from_response:
                SPACES_COOKIES.update(cookies_from_response)
                await save_cookies_to_json(SPACES_COOKIES)
                logger.info(f"Получено и сохранено куки из tm URL: {list(cookies_from_response.keys())}")
                await fetch_user_ck()
                cookies_loaded = True
            else:
                logger.warning("Не удалось получить куки из tm URL")
    except Exception as e:
        logger.error(f"Ошибка получения куки: {e}", exc_info=True)

async def get_final_download_url(url):
    """Получает финальный URL после всех редиректов"""
    try:
        async with httpx.AsyncClient(cookies=SPACES_COOKIES, follow_redirects=True, timeout=30.0) as client:
            response = await client.head(url, headers=get_request_headers())
            return str(response.url)
    except Exception as e:
        logger.error(f"Ошибка получения финального URL для {url}: {e}")
        return url

async def download_video_to_file(video_url, max_size_mb=50):
    """Загружает видео локально во временный файл"""
    try:
        temp_dir = "temp_videos"
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir, mode=0o755)

        async with httpx.AsyncClient(cookies=SPACES_COOKIES, follow_redirects=True, timeout=60.0) as client:
            async with client.stream('GET', video_url, headers=get_request_headers()) as response:
                response.raise_for_status()
                total_size = 0
                max_size_bytes = max_size_mb * 1024 * 1024

                tmp_filename = f"{uuid.uuid4().hex}.mp4"
                tmp_path = os.path.join(temp_dir, tmp_filename)

                with open(tmp_path, 'wb') as tmp_file:
                    async for chunk in response.aiter_bytes():
                        total_size += len(chunk)
                        if total_size > max_size_bytes:
                            os.unlink(tmp_path)
                            logger.warning(f"Видео слишком большое: {total_size / 1024 / 1024:.2f} МБ")
                            return None
                        tmp_file.write(chunk)

                os.chmod(tmp_path, 0o644)
                logger.info(f"Видео загружено: {total_size / 1024 / 1024:.2f} МБ, путь: {tmp_path}")
                return tmp_path
    except Exception as e:
        logger.error(f"Ошибка загрузки видео {video_url}: {e}", exc_info=True)
        return None

def load_categories_from_json():
    """Загружает категории из JSON файла"""
    global categories_cache
    if os.path.exists(settings.categories_json_file):
        try:
            with open(settings.categories_json_file, 'r', encoding='utf-8') as f:
                categories = json.load(f)
                for cat in categories:
                    if 'url' in cat:
                        cat['url'] = cat['url'].replace("https://spaces.im", settings.spaces_base_url)
                return categories
        except Exception as e:
            logger.warning(f"Ошибка загрузки категорий из файла: {e}")
    return None

def save_categories_to_json(categories):
    """Сохраняет категории в JSON файл"""
    try:
        with open(settings.categories_json_file, 'w', encoding='utf-8') as f:
            json.dump(categories, f, indent=2, ensure_ascii=False)
        logger.info(f"Категории сохранены в {settings.categories_json_file}")
    except Exception as e:
        logger.error(f"Ошибка сохранения категорий: {e}")

async def get_categories():
    """Получает список категорий"""
    global categories_cache
    if categories_cache:
        return categories_cache

    loaded = load_categories_from_json()
    if loaded:
        categories_cache = loaded
        return loaded

    try:
        async with httpx.AsyncClient(cookies=SPACES_COOKIES, timeout=30.0) as client:
            response = await client.get(settings.categories_base_url, headers=get_request_headers())
            response.raise_for_status()

            html_text = response.text
            if len(html_text) < 1000:
                logger.error("HTML слишком короткий")
                return []

            categories = parse_categories_from_html(html_text)
            categories_cache = categories
            save_categories_to_json(categories)
            return categories
    except Exception as e:
        logger.error(f"Ошибка получения категорий: {e}", exc_info=True)
        return []

def get_page_url(category_url, page_num):
    """Формирует URL для конкретной страницы"""
    if page_num == 1:
        return category_url

    if 'music-online/search' in category_url:
        import re
        if 'P=' in category_url:
            if category_url.startswith('?'):
                return re.sub(r'[?&]P=\d+', f'P={page_num}', category_url)
            else:
                return re.sub(r'[?&]P=\d+', f'&P={page_num}', category_url)
        else:
            return f"{category_url}&P={page_num}" if '?' in category_url else f"{category_url}?P={page_num}"

    if '?' in category_url:
        base_url, query_params = category_url.split('?', 1)
        sep = '' if base_url.endswith('/') else '/'
        return f"{base_url}{sep}p{page_num}/?{query_params}"
    else:
        sep = '' if category_url.endswith('/') else '/'
        return f"{category_url}{sep}p{page_num}/"

async def get_tracks_from_category(category_url, use_random_page=True):
    """Получает список треков из категории"""
    try:
        async with httpx.AsyncClient(cookies=SPACES_COOKIES, timeout=30.0, follow_redirects=True) as client:
            response = await client.get(category_url, headers=get_request_headers())
            response.raise_for_status()

            html_text = response.text
            max_pages = parse_pagination_info(html_text)

            if use_random_page and max_pages and max_pages > 1:
                random_page = random.randint(1, min(max_pages, 1000))
                if random_page > 1:
                    page_url = get_page_url(category_url, random_page)
                    response = await client.get(page_url, headers=get_request_headers())
                    response.raise_for_status()
                    html_text = response.text

            tracks = parse_tracks_from_html(html_text)
            return tracks
    except Exception as e:
        logger.error(f"Ошибка получения треков из {category_url}: {e}", exc_info=True)
        return []

async def search_pictures(query, page_num=1):
    """Ищет картинки по запросу"""
    try:
        cache_key = f"pic_search_{query}"
        base_photo_search_url = None
        cached_max_pages = None

        if cache_key in picture_search_cache:
            cache_data = picture_search_cache[cache_key]
            if isinstance(cache_data, dict):
                base_photo_search_url = cache_data.get('base_url')
                cached_max_pages = cache_data.get('max_pages')
            else:
                base_photo_search_url = cache_data

        if not base_photo_search_url:
            search_form_url = f"{settings.spaces_base_url}/files/search/"
            async with httpx.AsyncClient(cookies=SPACES_COOKIES, timeout=30.0, follow_redirects=True) as client:
                form_response = await client.get(search_form_url, headers=get_request_headers())
                form_response.raise_for_status()
                form_params = parse_search_form_params(form_response.text) or {'Link_id': '497973', 'stt': 'bfM5ACPv_pw'}

                search_response = await client.post(search_form_url, data={'word': query, **form_params}, headers=get_request_headers())
                search_response.raise_for_status()

                base_photo_search_url = parse_files_search_link(search_response.text)
                if not base_photo_search_url:
                    return [], None, None

                first_page_response = await client.get(base_photo_search_url, headers=get_request_headers())
                cached_max_pages = parse_pagination_info(first_page_response.text)

                picture_search_cache[cache_key] = {
                    'base_url': base_photo_search_url,
                    'max_pages': cached_max_pages
                }

        photo_search_url = base_photo_search_url
        if page_num > 1:
            sep = '&' if '?' in photo_search_url else '?'
            photo_search_url = f"{photo_search_url}{sep}P={page_num}"

        async with httpx.AsyncClient(cookies=SPACES_COOKIES, timeout=30.0, follow_redirects=True) as client:
            results_response = await client.get(photo_search_url, headers=get_request_headers())
            results_response.raise_for_status()
            html_text = results_response.text
            pictures = parse_pictures_from_html(html_text)
            max_pages = parse_pagination_info(html_text) or cached_max_pages
            return pictures, max_pages, page_num
    except Exception as e:
        logger.error(f"Ошибка поиска картинок: {e}", exc_info=True)
        return [], None, None

async def search_video_files(query, page_num=1):
    """Ищет видео по запросу"""
    try:
        cache_key = f"video_files_search_{query}"
        base_video_search_url = None
        cached_max_pages = None

        if cache_key in video_files_search_cache:
            cache_data = video_files_search_cache[cache_key]
            if isinstance(cache_data, dict):
                base_video_search_url = cache_data.get('base_url')
                cached_max_pages = cache_data.get('max_pages')

        if not base_video_search_url:
            search_form_url = f"{settings.spaces_base_url}/files/search/"
            async with httpx.AsyncClient(cookies=SPACES_COOKIES, timeout=30.0, follow_redirects=True) as client:
                form_response = await client.get(search_form_url, headers=get_request_headers())
                form_params = parse_search_form_params(form_response.text) or {'Link_id': '497973', 'stt': 'bfM5ACPv_pw'}
                search_response = await client.post(search_form_url, data={'word': query, **form_params}, headers=get_request_headers())

                base_video_search_url = parse_video_search_link(search_response.text)
                if not base_video_search_url:
                    return [], None, None

                first_page_response = await client.get(base_video_search_url, headers=get_request_headers())
                cached_max_pages = parse_pagination_info(first_page_response.text)
                video_files_search_cache[cache_key] = {'base_url': base_video_search_url, 'max_pages': cached_max_pages}

        video_search_url = base_video_search_url
        if page_num > 1:
            sep = '&' if '?' in video_search_url else '?'
            video_search_url = f"{video_search_url}{sep}P={page_num}"

        async with httpx.AsyncClient(cookies=SPACES_COOKIES, timeout=30.0, follow_redirects=True) as client:
            results_response = await client.get(video_search_url, headers=get_request_headers())
            videos = parse_videos_from_search(results_response.text)
            max_pages = parse_pagination_info(results_response.text) or cached_max_pages
            return videos, max_pages, page_num
    except Exception as e:
        logger.error(f"Ошибка поиска видео: {e}", exc_info=True)
        return [], None, None

async def search_music_files(query, page_num=1):
    """Ищет музыку по запросу"""
    try:
        cache_key = f"music_files_search_{query}"
        base_music_search_url = None
        cached_max_pages = None

        if cache_key in music_files_search_cache:
            cache_data = music_files_search_cache[cache_key]
            if isinstance(cache_data, dict):
                base_music_search_url = cache_data.get('base_url')
                cached_max_pages = cache_data.get('max_pages')

        if not base_music_search_url:
            search_form_url = f"{settings.spaces_base_url}/files/search/"
            async with httpx.AsyncClient(cookies=SPACES_COOKIES, timeout=30.0, follow_redirects=True) as client:
                form_response = await client.get(search_form_url, headers=get_request_headers())
                form_params = parse_search_form_params(form_response.text) or {'Link_id': '497973', 'stt': 'bfM5ACPv_pw'}
                search_response = await client.post(search_form_url, data={'word': query, **form_params}, headers=get_request_headers())

                base_music_search_url = parse_music_search_link(search_response.text)
                if not base_music_search_url:
                    return [], None, None

                first_page_response = await client.get(base_music_search_url, headers=get_request_headers())
                cached_max_pages = parse_pagination_info(first_page_response.text)
                music_files_search_cache[cache_key] = {'base_url': base_music_search_url, 'max_pages': cached_max_pages}

        music_search_url = base_music_search_url
        if page_num > 1:
            sep = '&' if '?' in music_search_url else '?'
            music_search_url = f"{music_search_url}{sep}P={page_num}"

        async with httpx.AsyncClient(cookies=SPACES_COOKIES, timeout=30.0, follow_redirects=True) as client:
            results_response = await client.get(music_search_url, headers=get_request_headers())
            tracks = parse_music_tracks_from_search(results_response.text)
            max_pages = parse_pagination_info(results_response.text) or cached_max_pages
            return tracks, max_pages, page_num
    except Exception as e:
        logger.error(f"Ошибка поиска музыки: {e}", exc_info=True)
        return [], None, None

async def search_music_inline(query):
    """Ищет музыку через основной музыкальный поиск"""
    try:
        url = f"{settings.search_base_url}?word={query}&CK={SPACES_CK}"
        async with httpx.AsyncClient(cookies=SPACES_COOKIES, timeout=30.0) as client:
            response = await client.get(url, headers=get_request_headers())
            response.raise_for_status()
            link_id = parse_search_link_id(response.text)
            if not link_id:
                return []

            search_url = f"{settings.spaces_base_url}/music-online/search/?Link_id={link_id}"
            response = await client.get(search_url, headers=get_request_headers())
            return parse_tracks_from_html(response.text)
    except Exception as e:
        logger.error(f"Ошибка поиска музыки inline: {e}")
        return []

async def search_music(query, page_num=1, cache_key=None):
    """Ищет музыку по запросу и возвращает список треков"""
    try:
        import urllib.parse
        encoded_query = urllib.parse.quote(query)

        if cache_key and cache_key in search_cache:
            cache_data = search_cache[cache_key]
            link_id = cache_data['link_id']
            max_pages = cache_data['max_pages']
            encoded_query = cache_data['encoded_query']
        else:
            search_url = f"{settings.search_base_url}?T=0&sq={encoded_query}&CK={SPACES_CK}"

            async with httpx.AsyncClient(cookies=SPACES_COOKIES, timeout=30.0, follow_redirects=True) as client:
                response = await client.get(search_url, headers=get_request_headers())
                response.raise_for_status()

                html_text = response.text
                link_id = parse_search_link_id(html_text)
                if not link_id:
                    return [], None, None

                first_results_url = f"{settings.search_base_url}?Link_id={link_id}&T=28&sq={encoded_query}&CK={SPACES_CK}"
                first_results_response = await client.get(first_results_url, headers=get_request_headers())
                max_pages = parse_pagination_info(first_results_response.text)

                if cache_key:
                    search_cache[cache_key] = {
                        'link_id': link_id,
                        'max_pages': max_pages,
                        'encoded_query': encoded_query
                    }

        results_url = f"{settings.search_base_url}?Link_id={link_id}&T=28&sq={encoded_query}&CK={SPACES_CK}"
        if page_num > 1 and max_pages and page_num <= max_pages:
            results_url = f"{settings.search_base_url}?Link_id={link_id}&P={page_num}&T=28&sq={encoded_query}&CK={SPACES_CK}"

        async with httpx.AsyncClient(cookies=SPACES_COOKIES, timeout=30.0, follow_redirects=True) as client:
            response = await client.get(results_url, headers=get_request_headers())
            html_text = response.text

        if not max_pages:
            max_pages = parse_pagination_info(html_text)
            if max_pages and cache_key:
                search_cache[cache_key]['max_pages'] = max_pages

        tracks = parse_tracks_from_html(html_text)
        for track in tracks:
            track['category'] = f"Поиск: {query}"

        return tracks, max_pages, page_num
    except Exception as e:
        logger.error(f"Ошибка поиска музыки: {e}", exc_info=True)
        return [], None, None

async def get_random_tracks():
    """Получает список треков из случайной категории или поиска"""
    if random.random() < 0.5:
        search_queries = [
            "демо", "pop", "rock", "jazz", "electronic", "классика",
            "russian", "джаз", "рок", "электронная", "хит", "remix"
        ]
        query = random.choice(search_queries)
        tracks, _, _ = await search_music(query)
        if tracks:
            return tracks

    categories = await get_categories()
    if not categories:
        return []

    for _ in range(10):
        category = random.choice(categories)
        tracks = await get_tracks_from_category(category['url'])
        if tracks:
            for track in tracks:
                track['category'] = category['name']
            return tracks
    return []
