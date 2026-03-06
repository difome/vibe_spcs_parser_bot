import logging
import random
from aiogram.exceptions import TelegramBadRequest
from aiogram import Router, F
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InlineQueryResultAudio,
    InlineQueryResultPhoto,
    InputTextMessageContent,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChosenInlineResult,
    InputMediaPhoto,
    InputMediaVideo,
    InputMediaAudio,
    FSInputFile,
    BufferedInputFile
)
import os
from aiogram import Bot
from config import settings
from services.spaces import (
    load_and_save_cookies,
    cookies_loaded,
    search_video_files,
    search_music_files,
    search_pictures,
    search_music,
    get_random_tracks,
    SPACES_COOKIES,
    get_request_headers,
    get_final_download_url,
    download_video_to_file
)
from parsers.spaces import (
    parse_photo_info_from_view_page,
    get_video_download_url_from_html
)
from selectolax.parser import HTMLParser
import httpx
import re
from utils.cache import (
    track_info_cache,
    video_info_cache,
    picture_info_cache
)

logger = logging.getLogger(__name__)
router = Router()
import html as html_module

@router.inline_query()
async def inline_query_handler(inline_query: InlineQuery):
    """Обработчик inline запросов"""
    # if not cookies_loaded:
    #     await load_and_save_cookies()

    try:
        query = inline_query.query.strip() if inline_query.query else ""
        offset = inline_query.offset
        page_num = 1
        if offset:
            try:
                page_num = int(offset)
            except ValueError:
                page_num = 1

        if not query:
            # При открытии инлайна сразу показываем подсказку
            results = []

            # 1. Подсказка о префиксах (только на 1-й странице)
            if page_num == 1:
                results.append(InlineQueryResultArticle(
                    id="inline_hint",
                    title="💡 Подсказки по поиску",
                    description="Нажми, чтобы увидеть как пользоваться ботом",
                    input_message_content=InputTextMessageContent(
                        message_text=(
                            "🔎 <b>Доступные префиксы для поиска:</b>\n\n"
                            f"🎧 <code>@{settings.bot_username} -м1</code> ваш запрос — Поиск музыки (файлы)\n"
                            f"🎬 <code>@{settings.bot_username} -в1</code> ваш запрос — Поиск видео\n"
                            f"🖼 <code>@{settings.bot_username} -к1</code> ваш запрос — Поиск картинок\n"
                            f"🎵 <code>@{settings.bot_username}</code> запрос — Общий музыкальный поиск"
                        ),
                        parse_mode="HTML"
                    ),
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔎 Попробовать поиск", switch_inline_query_current_chat="")]
                    ])
                ))

            # 2. Рандомные треки убраны по требованию пользователя

            await inline_query.answer(results=results, cache_time=1)
            return

        is_picture_search = query.startswith('-к1') or query.startswith('-к1 ')
        if is_picture_search:
            query = query.replace('-к1', '').strip()
            if not query:
                await inline_query.answer(results=[], cache_time=1)
                return

        is_music_files_search = query.startswith('-м1') or query.startswith('-м1 ')
        if is_music_files_search:
            query = query.replace('-м1', '').strip()
            if not query:
                await inline_query.answer(results=[], cache_time=1)
                return

        is_video_files_search = query.startswith('-в1') or query.startswith('-в1 ')
        if is_video_files_search:
            query = query.replace('-в1', '').strip()
            if not query:
                await inline_query.answer(results=[], cache_time=1)
                return

        # Для поиска видео через files/search
        if is_video_files_search and query and len(query) >= 1:
            logger.info(f"Поиск видео (files) по запросу: '{query}' (страница {page_num})")
            videos, max_pages, current_page = await search_video_files(query, page_num)

            if not isinstance(videos, list):
                videos = []

            videos = [v for v in videos if isinstance(v, dict) and 'name' in v and 'view_url' in v]

            if not videos and page_num == 1:
                result = InlineQueryResultArticle(
                    id="not_found_video_files",
                    title="❌ Видео не найдены",
                    description=f"По запросу '{query}' ничего не найдено",
                    input_message_content=InputTextMessageContent(
                        message_text=f"❌ По запросу <b>{query}</b> видео не найдены.\n\nПопробуйте другой запрос.",
                        parse_mode="HTML"
                    )
                )
                await inline_query.answer(results=[result], cache_time=1)
                return
            elif not videos:
                await inline_query.answer(results=[], cache_time=1, next_offset="")
                return

            results = []
            for i, video in enumerate(videos[:50]):
                result_id = f"vid_{page_num}_{i}_{random.randint(1000, 9999)}"
                video['search_query'] = query
                video_info_cache[result_id] = video

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔍 Найти еще", switch_inline_query_current_chat=f"-в1 {query}")],
                    [InlineKeyboardButton(text="📹 Страница видео", url=video.get('view_url'))] if video.get('view_url') else [],
                    [InlineKeyboardButton(text="Перейти в бота", url=settings.bot_link)]
                ])

                video_title = video['name'][:64] if len(video['name']) > 64 else video['name']
                preview_url = video.get('preview_url', '')

                if not preview_url or not preview_url.startswith('http'):
                    continue

                results.append(InlineQueryResultArticle(
                    id=result_id,
                    title=f"📹 {video_title}",
                    description=f"📹 ВИДЕО: {video_title}\n🔍 Поиск: {query}",
                    thumbnail_url=preview_url,
                    input_message_content=InputTextMessageContent(
                        message_text=f"📹 <b>{video_title}</b>\n🔍 Поиск: {query}",
                        parse_mode="HTML"
                    ),
                    reply_markup=keyboard
                ))

            await inline_query.answer(
                results=results,
                cache_time=0,
                next_offset=str(current_page + 1) if max_pages and current_page < max_pages else None
            )
            return

        # Для поиска музыки через files/search
        if is_music_files_search and query and len(query) >= 1:
            logger.info(f"Поиск музыки (files) по запросу: '{query}' (страница {page_num})")
            tracks, max_pages, current_page = await search_music_files(query, page_num)

            if not isinstance(tracks, list): tracks = []
            tracks = [t for t in tracks if isinstance(t, dict) and 'name' in t and 'url' in t]

            if not tracks and page_num == 1:
                result = InlineQueryResultArticle(
                    id="not_found_music_files",
                    title="❌ Треки не найдены",
                    description=f"По запросу '{query}' ничего не найдено",
                    input_message_content=InputTextMessageContent(
                        message_text=f"❌ По запросу <b>{query}</b> треки не найдены.\n\nПопробуйте другой запрос.",
                        parse_mode="HTML"
                    )
                )
                await inline_query.answer(results=[result], cache_time=1)
                return
            elif not tracks:
                await inline_query.answer(results=[], cache_time=1, next_offset="")
                return

            results = []
            for track in tracks[:50]:
                result_id = str(random.randint(1000000, 9999999))
                track_info_cache[result_id] = track
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔍 Найти еще", switch_inline_query_current_chat=f"-м1 {query}")],
                    [InlineKeyboardButton(text="Перейти в бота", url=settings.bot_link)]
                ])
                results.append(InlineQueryResultAudio(
                    id=result_id,
                    audio_url=track['url'],
                    title=track['name'],
                    caption=f"🎵 {track['name']}\n📁 Поиск: {query}",
                    reply_markup=keyboard
                ))

            await inline_query.answer(
                results=results,
                cache_time=0,
                next_offset=str(current_page + 1) if max_pages and current_page < max_pages else None
            )
            return

        # Для поиска картинок
        if is_picture_search and query and len(query) >= 1:
            logger.info(f"Поиск картинок по запросу: '{query}' (страница {page_num})")
            pictures, max_pages, current_page = await search_pictures(query, page_num)

            if not isinstance(pictures, list): pictures = []
            pictures = [p for p in pictures if isinstance(p, dict) and p.get('photo_url', '').startswith('http')]

            if not pictures and page_num == 1:
                result = InlineQueryResultArticle(
                    id="not_found_pics",
                    title="❌ Картинки не найдены",
                    input_message_content=InputTextMessageContent(
                        message_text=f"❌ По запросу <b>{query}</b> картинки не найдены.",
                        parse_mode="HTML"
                    )
                )
                await inline_query.answer(results=[result], cache_time=1)
                return

            results = []
            for i, picture in enumerate(pictures[:50]):
                result_id = f"pic_{page_num}_{i}_{random.randint(1000, 9999)}"
                picture_info_cache[result_id] = {**picture, 'search_query': query}

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔍 Найти еще", switch_inline_query_current_chat=f"-к1 {query}")],
                    [InlineKeyboardButton(text="📷 Страница фото", url=picture['view_url'])] if picture.get('view_url') else [],
                    [InlineKeyboardButton(text="Перейти в бота", url=settings.bot_link)]
                ])

                results.append(InlineQueryResultPhoto(
                    id=result_id,
                    photo_url=picture['photo_url'],
                    thumbnail_url=picture['thumb_url'],
                    photo_width=600,
                    photo_height=600,
                    title=picture['title'][:64],
                    description=f"🔍 Поиск: {query}\n📷 {picture['title']}"[:128],
                    reply_markup=keyboard
                ))

            await inline_query.answer(
                results=results,
                cache_time=0,
                next_offset=str(current_page + 1) if max_pages and current_page < max_pages else None
            )
            return

        # Основной поиск музыки (когда query точно не пустой)
        logger.info(f"Поиск музыки по запросу: '{query}' (страница {page_num})")
        cache_key = f"search_{query}"
        tracks, max_pages, current_page = await search_music(query, page_num, cache_key)

        if not tracks:
            await inline_query.answer(results=[], cache_time=1)
            return

        results = []
        for track in tracks[:50]:
            result_id = str(random.randint(1000000, 9999999))
            track_info_cache[result_id] = track
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="Перейти в бота", url=settings.bot_link)]
            ])
            caption = f"🎵 {track['name']}"
            if track.get('category'): caption += f"\n📁 {track['category']}"

            results.append(InlineQueryResultAudio(
                id=result_id,
                audio_url=track['url'],
                title=track['name'],
                caption=caption,
                reply_markup=keyboard
            ))

        await inline_query.answer(
            results=results,
            cache_time=1,
            next_offset=str(current_page + 1) if max_pages and current_page < max_pages else None
        )

    except Exception as e:
        logger.error(f"Ошибка в inline_query_handler: {e}", exc_info=True)
        await inline_query.answer(results=[], cache_time=1)

@router.chosen_inline_result()
async def chosen_inline_result_handler(chosen_result: ChosenInlineResult, bot: Bot):
    """Обработчик выбора результата inline запроса"""
    result_id = chosen_result.result_id

    if not cookies_loaded:
        await load_and_save_cookies()

    try:
        if result_id.startswith('pic_'):
            picture = picture_info_cache.get(result_id)
            if picture and picture.get('view_url'):
                async with httpx.AsyncClient(cookies=SPACES_COOKIES, timeout=30.0, follow_redirects=True) as client:
                    response = await client.get(picture['view_url'], headers=get_request_headers())
                    html_text = response.text
                    tree = HTMLParser(html_text)

                    photo_info = parse_photo_info_from_view_page(html_text)
                    original_url = None

                    gview_link = tree.css_first('a.gview_link')
                    if gview_link and gview_link.attributes.get('g'):
                        urls = re.findall(r'https?://[^\|]+\.(?:p|f)\.800\.800\.[^\|]+', gview_link.attributes['g'])
                        if not urls:
                            urls = re.findall(r'https?://[^\|]+\.(?:p|f)\.600\.600\.[^\|]+', gview_link.attributes['g'])
                        if urls: original_url = urls[-1]

                    if not original_url:
                        original_url = picture.get('photo_url')

                    if original_url and chosen_result.inline_message_id:
                        search_query = html_module.escape(picture.get('search_query', ''))
                        photo_title = html_module.escape(picture.get('title', ''))

                        caption_parts = []
                        if search_query: caption_parts.append(f"🔍 Поиск: {search_query}")
                        if photo_title: caption_parts.append(f"📷 {photo_title}")

                        if photo_info.get('description'):
                            desc = html_module.escape(photo_info['description'])
                            if len(desc) > 700: desc = desc[:697] + "..."
                            caption_parts.append(f"\n{desc}")

                        author_text = ""
                        if photo_info.get('author_name'):
                            author_text = f"👤 {html_module.escape(photo_info['author_name'])}"
                            if photo_info.get('author_date'):
                                author_text += f" ({html_module.escape(photo_info['author_date'])})"
                        elif photo_info.get('author_date'):
                            author_text = f"📅 {html_module.escape(photo_info['author_date'])}"

                        if author_text:
                            caption_parts.append(f"<b>{author_text}</b>")

                        caption = "\n".join(caption_parts)

                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="🔍 Найти еще", switch_inline_query_current_chat=f"-к1 {picture.get('search_query', '')}")],
                            [InlineKeyboardButton(text="📷 Страница фото", url=picture['view_url'])],
                            [InlineKeyboardButton(text="Перейти в бота", url=settings.bot_link)]
                        ])

                        try:
                            await bot.edit_message_media(
                                inline_message_id=chosen_result.inline_message_id,
                                media=InputMediaPhoto(media=original_url, caption=caption, parse_mode="HTML"),
                                reply_markup=keyboard
                            )
                        except Exception as edit_e:
                            if "message is not modified" in str(edit_e):
                                logger.debug("Photo message already identical")
                            else:
                                raise edit_e

        elif result_id.startswith('vid_'):
            video = video_info_cache.get(result_id)
            if video and video.get('view_url'):
                async with httpx.AsyncClient(cookies=SPACES_COOKIES, timeout=30.0, follow_redirects=True) as client:
                    response = await client.get(video['view_url'], headers=get_request_headers())
                    video_data = get_video_download_url_from_html(response.text)

                    if video_data.get('download_url') and chosen_result.inline_message_id:
                        download_url = await get_final_download_url(video_data['download_url'])

                        caption_parts = []
                        if video.get('search_query'): caption_parts.append(f"🔍 Поиск: {html_module.escape(video['search_query'])}")
                        caption_parts.append(f"📹 {html_module.escape(video['name'])}")

                        if video_data.get('description'):
                            desc = html_module.escape(video_data['description'])
                            if len(desc) > 700: desc = desc[:697] + "..."
                            caption_parts.append(f"\n{desc}")

                        author_info = ""
                        if video_data.get('author_name'):
                            author_info = f"👤 {html_module.escape(video_data['author_name'])}"
                            if video_data.get('author_date'):
                                author_info += f" ({html_module.escape(video_data['author_date'])})"
                        elif video_data.get('author_date'):
                            author_info = f"📅 {html_module.escape(video_data['author_date'])}"

                        if author_info:
                            caption_parts.append(f"<b>{author_info}</b>")

                        caption = "\n".join(caption_parts)

                        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="🔍 Найти еще", switch_inline_query_current_chat=f"-в1 {video.get('search_query', '')}")],
                            [InlineKeyboardButton(text="📹 Страница видео", url=video['view_url'])],
                            [InlineKeyboardButton(text="Перейти в бота", url=settings.bot_link)]
                        ])

                        try:
                            await bot.edit_message_media(
                                inline_message_id=chosen_result.inline_message_id,
                                media=InputMediaVideo(media=download_url, caption=caption, parse_mode="HTML"),
                                reply_markup=keyboard
                            )
                        except TelegramBadRequest as e:
                            if "failed to get HTTP URL content" in str(e):
                                logger.info("Качаємо локально для отримання file_id...")
                                tmp_path = await download_video_to_file(video_data['download_url'])
                                if not tmp_path:
                                    return
                                try:
                                    with open(tmp_path, 'rb') as f:
                                        sent = await bot.send_video(
                                            chat_id=settings.cache_chat_id,
                                            video=BufferedInputFile(f.read(), filename="video.mp4")
                                        )
                                    file_id = sent.video.file_id

                                    await bot.edit_message_media(
                                        inline_message_id=chosen_result.inline_message_id,
                                        media=InputMediaVideo(media=file_id, caption=caption, parse_mode="HTML"),
                                        reply_markup=keyboard
                                    )

                                    await bot.delete_message(chat_id=settings.cache_chat_id, message_id=sent.message_id)
                                finally:
                                    if os.path.exists(tmp_path):
                                        os.unlink(tmp_path)

        else:
            track = track_info_cache.get(result_id)
            if track and track.get('url') and chosen_result.inline_message_id:
                final_url = await get_final_download_url(track['url'])

                caption = f"🎵 {html_module.escape(track['name'])}"
                if track.get('category'): caption += f"\n📁 {html_module.escape(track['category'])}"

                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="Перейти в бота", url=settings.bot_link)]
                ])

                try:
                    await bot.edit_message_media(
                        inline_message_id=chosen_result.inline_message_id,
                        media=InputMediaAudio(
                            media=final_url,
                            title=track['name'],
                            caption=caption
                        ),
                        reply_markup=keyboard
                    )
                except Exception as edit_e:
                    if "message is not modified" in str(edit_e):
                        logger.debug("Inline message for track already has the correct content")
                    else:
                        raise edit_e

    except Exception as e:
        if "message is not modified" in str(e):
            logger.debug("Message already modified or identical")
        else:
            logger.error(f"Ошибка в chosen_inline_result_handler: {e}", exc_info=True)
