import logging
import re
import html
from selectolax.parser import HTMLParser
from config import settings

logger = logging.getLogger(__name__)

def parse_search_link_id(html_text):
    """Парсит Link_id из HTML страницы поиска или редиректа"""
    try:
        tree = HTMLParser(html_text)

        # 1. Поиск в ссылках
        links = tree.css('a[href*="Link_id="]')
        for link in links:
            href = link.attributes.get('href', '')
            match = re.search(r'Link_id=(\d+)', href)
            if match:
                return match.group(1)

        # 2. Поиск в скрытых полях форм
        inputs = tree.css('input[name="Link_id"]')
        for input_tag in inputs:
            value = input_tag.attributes.get('value')
            if value:
                return value

        # 3. Регрессия через регулярку по всему тексту
        match = re.search(r'Link_id=(\d+)', html_text)
        if match:
            return match.group(1)

        return None
    except Exception as e:
        logger.error(f"Ошибка парсинга Link_id: {e}")
        return None

def parse_ck(html_text):
    """Парсит CK (User ID) из ответов сервера"""
    # Ищем в ссылках или в тексте: CK=12345
    match = re.search(r'CK=(\d+)', html_text)
    if match:
        return match.group(1)
    return None

def parse_categories_from_html(html_text):
    """Парсит список категорий из HTML"""
    tree = HTMLParser(html_text)
    categories = []

    links = tree.css('a.list-link.list-link-darkblue, a.list-link-darkblue')

    if not links:
        links = tree.css('a.list-link, a[class*="darkblue"]')

    for link in links:
        try:
            href = link.attributes.get('href', '')

            if '/muzyka/' in href and '?Link_id=' in href:
                category_name = None

                js_text_span = link.css_first('span.t.js-text, span.js-text.t')
                if js_text_span:
                    category_name = js_text_span.text(strip=True)

                if not category_name:
                    all_spans = link.css('span.t')
                    for span in all_spans:
                        text = span.text(strip=True)
                        if text and 'тыс' not in text and len(text) > 2:
                            category_name = text
                            break

                if not category_name:
                    link_text = link.text(strip=True)
                    if link_text and 'тыс' not in link_text and len(link_text) > 2:
                        category_name = link_text.split('(')[0].strip()

                if category_name:
                    category_url = href if href.startswith('http') else f"{settings.spaces_base_url}{href}"
                    categories.append({
                        'name': category_name,
                        'url': category_url
                    })
                    logger.debug(f"Добавлена категория: {category_name} -> {category_url}")
        except Exception as e:
            logger.error(f"Ошибка парсинга категории: {e}")
            continue

    logger.debug(f"Всего найдено категорий: {len(categories)}")
    return categories

def parse_photo_info_from_view_page(html_text):
    """Парсит описание и информацию об авторе со страницы просмотра фото"""
    tree = HTMLParser(html_text)

    description = None
    author_name = None
    author_date = None

    desc_div = tree.css_first('div[itemprop="description"]')
    if desc_div:
        desc_inner = desc_div.css_first('div.pad_t_a.break-word')
        if desc_inner:
            description = desc_inner.text(strip=True)
        else:
            desc_inner = desc_div.css_first('div.break-word.pad_t_a')
            if desc_inner:
                description = desc_inner.text(strip=True)
            else:
                description = desc_div.text(strip=True)

    author_div = tree.css_first('div.content-item3.wbg.break-word')
    if author_div:
        added_div = author_div.css_first('div.grey')
        if added_div:
            added_text = added_div.text(strip=True)
            nick_elem = added_div.css_first('b.mysite-nick')
            if nick_elem:
                author_name = nick_elem.text(strip=True)

            # Ищем дату в формате (28 июн 2016) или (28 июн в 12:34) или просто (вчера в 12:34)
            date_match = re.search(r'\(([^)]+)\)', added_text)
            if date_match:
                author_date = date_match.group(1).strip()
                # Убираем "в 12:34", если оно есть, чтобы оставить только дату
                author_date = re.sub(r'\s+в\s+\d+:\d+', '', author_date).strip()

    return {
        'description': description,
        'author_name': author_name,
        'author_date': author_date
    }

def parse_video_info_from_view_page(html_text):
    """Парсит описание и информацию об авторе со страницы просмотра видео"""
    tree = HTMLParser(html_text)

    description = None
    author_name = None
    author_date = None

    desc_div = tree.css_first('div[itemprop="description"]')
    if desc_div:
        desc_inner = desc_div.css_first('div.pad_t_a.break-word')
        if desc_inner:
            description = desc_inner.text(strip=True)
        else:
            desc_inner = desc_div.css_first('div.break-word.pad_t_a')
            if desc_inner:
                description = desc_inner.text(strip=True)
            else:
                description = desc_div.text(strip=True)

    author_div = tree.css_first('div.content-item3.wbg.break-word')
    if author_div:
        added_div = author_div.css_first('div.grey')
        if added_div:
            added_text = added_div.text(strip=True)
            nick_elem = added_div.css_first('b.mysite-nick')
            if nick_elem:
                author_name = nick_elem.text(strip=True)

            # Универсальный поиск даты в скобках
            date_match = re.search(r'\(([^)]+)\)', added_text)
            if date_match:
                date_text = date_match.group(1).strip()
                # Очищаем от времени
                author_date = re.sub(r'\s+в\s+\d+:\d+', '', date_text).strip()

    return {
        'description': description,
        'author_name': author_name,
        'author_date': author_date
    }

def parse_pagination_info(html_text):
    """Парсит информацию о пагинации из HTML"""
    tree = HTMLParser(html_text)

    pgn_div = tree.css_first('div.pgn')
    if pgn_div:
        total = pgn_div.attributes.get('data-total')
        if total:
            try:
                max_pages = int(total)
                logger.debug(f"Найдено страниц через data-total: {max_pages}")
                return max_pages
            except ValueError:
                pass

    counter_elem = tree.css_first('div.pgn__counter.pgn__range')
    if counter_elem:
        counter_text = counter_elem.text(strip=True)
        if 'из' in counter_text:
            try:
                parts = counter_text.split('из')
                if len(parts) == 2:
                    max_pages = int(parts[1].strip())
                    logger.debug(f"Найдено страниц через счетчик: {max_pages}")
                    return max_pages
            except (ValueError, IndexError):
                pass

    logger.warning("Не удалось определить количество страниц из HTML")
    return None

def parse_search_link_id(html_text):
    """Парсит Link_id из страницы поиска"""
    tree = HTMLParser(html_text)

    all_link = tree.css_first('a.b-title__all')
    if not all_link:
        all_link = tree.css_first('a.list-link-blue')
    if not all_link:
        all_links = tree.css('a[class*="list-link-blue"]')
        if all_links:
            all_link = all_links[0]
    if not all_link:
        all_links = tree.css('a[href*="music-online/search"]')
        for link in all_links:
            href = link.attributes.get('href', '')
            if 'Link_id=' in href:
                all_link = link
                break

    if all_link:
        href = all_link.attributes.get('href', '')
        href = html.unescape(href)

        if 'Link_id=' in href:
            try:
                parts = href.split('Link_id=')
                if len(parts) == 2:
                    link_id = parts[1].split('&')[0].split('?')[0]
                    return link_id
            except (ValueError, IndexError):
                pass

    link_id_match = re.search(r'Link_id=(\d+)', html_text)
    if link_id_match:
        return link_id_match.group(1)

    return None

def parse_files_search_link(html_text):
    """Парсит ссылку на фото из результатов поиска (из списка категорий)"""
    tree = HTMLParser(html_text)

    photo_links = tree.css('a.list-link')
    for link in photo_links:
        link_text = link.text(strip=True)
        href = link.attributes.get('href', '')

        if ('Фото' in link_text or 'картинки' in link_text.lower() or 'Фото и картинки' in link_text) and 'Slist=1690' in href:
            href = href.replace('&amp;', '&')
            return href if href.startswith('http') else f"{settings.spaces_base_url}{href}"

    all_links = tree.css('a[href*="Slist=1690"]')
    for link in all_links:
        href = link.attributes.get('href', '')
        if 'files/search' in href and 'Link_id=' in href:
            href = href.replace('&amp;', '&')
            return href if href.startswith('http') else f"{settings.spaces_base_url}{href}"

    return None

def parse_music_search_link(html_text):
    """Парсит ссылку на музыку из результатов поиска (из списка категорий)"""
    tree = HTMLParser(html_text)

    music_links = tree.css('a.list-link')
    for link in music_links:
        link_text = link.text(strip=True)
        href = link.attributes.get('href', '')

        if ('Музыка' in link_text or 'музыка' in link_text.lower()) and 'Slist=61' in href:
            href = href.replace('&amp;', '&')
            return href if href.startswith('http') else f"{settings.spaces_base_url}{href}"

    all_links = tree.css('a[href*="Slist=61"]')
    for link in all_links:
        href = link.attributes.get('href', '')
        if 'files/search' in href and 'Link_id=' in href:
            href = href.replace('&amp;', '&')
            return href if href.startswith('http') else f"{settings.spaces_base_url}{href}"

    return None

def parse_video_search_link(html_text):
    """Парсит ссылку на видео из результатов поиска (из списка категорий)"""
    tree = HTMLParser(html_text)

    video_links = tree.css('a.list-link')
    for link in video_links:
        link_text = link.text(strip=True)
        href = link.attributes.get('href', '')

        if ('Видео' in link_text or 'видео' in link_text.lower()) and 'Slist=4' in href:
            href = href.replace('&amp;', '&')
            return href if href.startswith('http') else f"{settings.spaces_base_url}{href}"

    all_links = tree.css('a[href*="Slist=4"]')
    for link in all_links:
        href = link.attributes.get('href', '')
        if 'files/search' in href and 'Link_id=' in href:
            href = href.replace('&amp;', '&')
            return href if href.startswith('http') else f"{settings.spaces_base_url}{href}"

    return None

def parse_size_to_mb(size_text):
    """Преобразует размер из текста (Kб, Мб) в МБ"""
    if not size_text:
        return None

    match = re.search(r'([\d.]+)\s*(Кб|Мб|Kб|Mб|KB|MB)', size_text)
    if match:
        value = float(match.group(1))
        unit = match.group(2).lower()

        if 'кб' in unit or 'kb' in unit:
            return value / 1024
        elif 'мб' in unit or 'mb' in unit:
            return value

    return None

def parse_videos_from_search(html_text):
    """Парсит список видео из результатов поиска (виджет)"""
    tree = HTMLParser(html_text)
    videos = []

    items = tree.css('div.list-item.content-item3.wbg.content-bl__sep.js-file_item.oh[data-type="25"]')

    if not items:
        items = tree.css('div[data-type="25"]')

    for i, item in enumerate(items):
        try:
            video_name = None
            view_url = None
            preview_url = None
            size_mb = None

            title_elem = item.css_first('b.darkblue.break-word')
            if title_elem:
                video_name = title_elem.text(strip=True)

            view_link = item.css_first('a.arrow_link.strong_link')
            if not view_link:
                view_link = item.css_first('a.arrow_link')

            if view_link:
                view_href = view_link.attributes.get('href', '')
                if view_href:
                    view_url = view_href.replace('&amp;', '&')
                    if not view_url.startswith('http'):
                        view_url = f"{settings.spaces_base_url}{view_url}" if view_url.startswith('/') else f"{settings.spaces_base_url}/{view_url}"

            img_elem = item.css_first('img.preview')
            if img_elem:
                srcset = img_elem.attributes.get('srcset', '')
                if srcset:
                    all_urls = re.findall(r'(https?://[^\s,]+)', srcset)
                    if all_urls:
                        preview_url = all_urls[-1]
                else:
                    preview_url = img_elem.attributes.get('src', '')

                if preview_url and not preview_url.startswith('http'):
                    preview_url = f"{settings.spaces_base_url}{preview_url}" if preview_url.startswith('/') else f"{settings.spaces_base_url}/{preview_url}"

            size_elem = item.css_first('span.right.t-padd_left')
            if size_elem:
                size_text = size_elem.text(strip=True)
                size_mb = parse_size_to_mb(size_text)

            if size_mb and size_mb > 50:
                continue

            if video_name and view_url:
                videos.append({
                    'name': video_name,
                    'view_url': view_url,
                    'preview_url': preview_url,
                    'size_mb': size_mb
                })
        except Exception as e:
            logger.error(f"Ошибка парсинга видео: {e}")
            continue

    return videos

def parse_music_tracks_from_search(html_text):
    """Парсит список треков из результатов поиска музыки (виджет)"""
    tree = HTMLParser(html_text)
    tracks = []

    items = tree.css('div.list-item.content-item3.wbg.content-bl__sep.js-file_item.oh.__adv_list_track')

    if not items:
        items = tree.css('div.list-item.__adv_list_track, div.__adv_list_track, div.light_border_bottom.t-bg3.__adv_list_track')

    if not items:
        items = tree.css('div.list-item, div[data-type="6"]')

    for i, item in enumerate(items):
        try:
            track_name = None
            download_link = None

            if item.css_first('div.light_border_bottom'):
                artist_elem = item.css_first('div.oh.t-padd_left > div.oh')
                if artist_elem:
                    artist_text = artist_elem.text(strip=True)
                    if ':' in artist_text:
                        parts = artist_text.split(':', 1)
                        artist = parts[0].strip()
                        title_link = item.css_first('a.arrow_link')
                        if title_link:
                            span = title_link.css_first('span')
                            if span:
                                title = span.text(strip=True)
                                track_name = f"{artist}: {title}"
                        else:
                            track_name = artist_text.strip()
                    else:
                        title_link = item.css_first('a.arrow_link')
                        if title_link:
                            span = title_link.css_first('span')
                            if span:
                                track_name = span.text(strip=True)

            if not track_name:
                title_elem = item.css_first('b.darkblue.break-word')
                if not title_elem:
                    title_elem = item.css_first('b.break-word.darkblue')
                if not title_elem:
                    title_elem = item.css_first('b.darkblue')
                if title_elem:
                    track_name = title_elem.text(strip=True)

            player_div = item.css_first('div.player_item')
            if player_div:
                data_src = player_div.attributes.get('data-src', '')
                if data_src:
                    download_link = data_src if data_src.startswith('http') else f"{settings.spaces_base_url}{data_src}"

            if not download_link:
                download_a = item.css_first('a.__adv_download')
                if download_a:
                    download_link = download_a.attributes.get('href', '')
                    if download_link:
                        download_link = download_link.replace('&amp;', '&')
                        if not download_link.startswith('http'):
                            download_link = f"{settings.spaces_base_url}{download_link}"

            if track_name and download_link:
                tracks.append({
                    'name': track_name,
                    'url': download_link
                })
        except Exception as e:
            logger.error(f"Ошибка парсинга трека: {e}")
            continue

    return tracks

def parse_pictures_from_html(html_text):
    """Парсит список картинок из страницы результатов поиска"""
    tree = HTMLParser(html_text)
    pictures = []

    items = tree.css('div.list-item.content-item3')

    for i, item in enumerate(items):
        try:
            img_elem = item.css_first('img.preview')
            if not img_elem:
                continue

            img_src = img_elem.attributes.get('src', '')
            if not img_src:
                continue

            gview_link = item.css_first('a.gview_link')
            thumb_url = None
            photo_url = None

            if gview_link:
                g_attr = gview_link.attributes.get('g', '')
                if g_attr:
                    urls = re.findall(r'https?://[^\|]+\.(?:p|f)\.\d+\.\d+\.[^\|]+', g_attr)
                    if len(urls) >= 2:
                        thumb_url = urls[0]
                        photo_url = urls[1]
                    elif len(urls) == 1:
                        thumb_url = urls[0]
                        photo_url = urls[0]

            srcset = img_elem.attributes.get('srcset', '')
            if srcset:
                all_urls = re.findall(r'(https?://[^\s,]+)', srcset)
                if all_urls:
                    photo_url = all_urls[-1]

                if not thumb_url:
                    thumb_matches = re.findall(r'(https?://[^\s,]+\.(?:p|f)\.(?:161\.160|160\.160)\.[^\s,]+)', srcset)
                    if thumb_matches:
                        thumb_url = thumb_matches[0]
                    elif photo_url:
                        thumb_url = photo_url
                elif not photo_url:
                    photo_url = thumb_url.replace('.161.160.', '.600.600.').replace('.160.160.', '.600.600.')

            if not thumb_url:
                thumb_url = img_src

            title_elem = item.css_first('b.darkblue.break-word')
            if not title_elem:
                title_elem = item.css_first('b.break-word.darkblue')
            if not title_elem:
                title_elem = item.css_first('a.arrow_link b.darkblue')

            title = title_elem.text(strip=True) if title_elem else "Изображение"

            if not photo_url:
                data_type = item.attributes.get('data-type', '7')

                if thumb_url.startswith('http'):
                    if data_type == '7':
                        photo_url = thumb_url.replace('.p.81.80.', '.p.600.600.')
                        photo_url = photo_url.replace('.p.161.160.', '.p.600.600.')
                        photo_url = photo_url.replace('.p.160.160.', '.p.600.600.')
                        if '.p.600.600.' not in photo_url:
                            photo_url = re.sub(r'\.p\.\d+\.\d+\.', '.p.600.600.', photo_url)
                    else:
                        photo_url = thumb_url.replace('.f.81.80.', '.f.600.600.')
                        photo_url = photo_url.replace('.f.161.160.', '.f.600.600.')
                        photo_url = photo_url.replace('.f.160.160.', '.f.600.600.')
                        if '.f.600.600.' not in photo_url:
                            photo_url = re.sub(r'\.f\.\d+\.\d+\.', '.f.600.600.', photo_url)
                else:
                    thumb_url = f"{settings.spaces_base_url}{thumb_url}" if thumb_url.startswith('/') else f"https://{thumb_url}"
                    photo_url = thumb_url

            view_link = item.css_first('a.arrow_link')
            view_url = None
            if view_link:
                view_href = view_link.attributes.get('href', '')
                if view_href:
                    view_url = view_href.replace('&amp;', '&')
                    if not view_url.startswith('http'):
                        view_url = f"{settings.spaces_base_url}{view_url}" if view_url.startswith('/') else f"{settings.spaces_base_url}/{view_url}"

            if title and photo_url and thumb_url:
                pictures.append({
                    'title': title,
                    'thumb_url': thumb_url,
                    'photo_url': photo_url,
                    'view_url': view_url
                })
        except Exception as e:
            logger.error(f"Ошибка парсинга картинки: {e}")
            continue

    return pictures

def parse_tracks_from_html(html_text):
    """Парсит список треков из страницы категории или поиска"""
    tree = HTMLParser(html_text)
    tracks = []

    items = tree.css('div.list-item.__adv_list_track, div.__adv_list_track, div.light_border_bottom.t-bg3.__adv_list_track')

    if not items:
        items = tree.css('div.list-item, div[data-type="6"]')

    for i, item in enumerate(items):
        try:
            track_name = None
            download_link = None

            if item.css_first('div.light_border_bottom'):
                artist_elem = item.css_first('div.oh.t-padd_left > div.oh')
                if artist_elem:
                    artist_text = artist_elem.text(strip=True)
                    if ':' in artist_text:
                        parts = artist_text.split(':', 1)
                        artist = parts[0].strip()
                        title_link = item.css_first('a.arrow_link')
                        if title_link:
                            span = title_link.css_first('span')
                            if span:
                                title = span.text(strip=True)
                                track_name = f"{artist}: {title}"
                        else:
                            track_name = artist_text.strip()
                    else:
                        title_link = item.css_first('a.arrow_link')
                        if title_link:
                            span = title_link.css_first('span')
                            if span:
                                track_name = span.text(strip=True)

                player_div = item.css_first('div.player_item')
                if player_div:
                    data_src = player_div.attributes.get('data-src', '')
                    if data_src:
                        download_link = data_src if data_src.startswith('http') else f"{settings.spaces_base_url}{data_src}"

                if not download_link:
                    download_a = item.css_first('a.__adv_download')
                    if download_a:
                        download_link = download_a.attributes.get('href', '')
                        if download_link:
                            if not download_link.startswith('http'):
                                download_link = f"{settings.spaces_base_url}{download_link}"
            else:
                title_elem = item.css_first('b.darkblue.break-word')
                if not title_elem:
                    title_elem = item.css_first('b.break-word.darkblue')
                if not title_elem:
                    title_elem = item.css_first('b.darkblue')

                if not title_elem:
                    continue

                track_name = title_elem.text(strip=True)

                player_div = item.css_first('div.player_item')
                if player_div:
                    data_src = player_div.attributes.get('data-src', '')
                    if data_src:
                        download_link = data_src if data_src.startswith('http') else f"{settings.spaces_base_url}{data_src}"

                if not download_link:
                    download_a = item.css_first('a.__adv_download')
                    if download_a:
                        download_link = download_a.attributes.get('href', '')
                        if download_link:
                            if not download_link.startswith('http'):
                                download_link = f"{settings.spaces_base_url}{download_link}"

            if track_name and download_link:
                tracks.append({
                    'name': track_name,
                    'url': download_link
                })
        except Exception as e:
            logger.error(f"Ошибка парсинга трека: {e}")
            continue

    return tracks

def parse_search_form_params(html_text):
    """Парсит параметры формы поиска из HTML"""
    tree = HTMLParser(html_text)

    form = tree.css_first('form[action*="files/search"]')
    if not form:
        return None

    params = {}

    sid_input = form.css_first('input[name="sid"]')
    if sid_input:
        params['sid'] = sid_input.attributes.get('value', '')

    link_id_input = form.css_first('input[name="Link_id"]')
    if link_id_input:
        params['Link_id'] = link_id_input.attributes.get('value', '')

    stt_input = form.css_first('input[name="stt"]')
    if stt_input:
        params['stt'] = stt_input.attributes.get('value', '')

    slist_input = form.css_first('input[name="Slist"]')
    if slist_input:
        params['Slist'] = slist_input.attributes.get('value', '')

    rli_input = form.css_first('input[name="Rli"]')
    if rli_input:
        params['Rli'] = rli_input.attributes.get('value', '')

    return params if params else None

def get_video_download_url_from_html(html_text):
    """Парсит URL скачивания видео и информацию о видео из HTML страницы просмотра"""
    try:
        tree = HTMLParser(html_text)
        download_url = None

        download_links = tree.css('a.list-link.list-link-blue')
        for link in download_links:
            link_text = link.text(strip=True)
            href = link.attributes.get('href', '')

            if 'Скачать' in link_text and 'mp4' in link_text.lower():
                if href.startswith('http'):
                    download_url = href
                else:
                    download_url = f"{settings.spaces_base_url}{href}" if href.startswith('/') else f"{settings.spaces_base_url}/{href}"
                break

        if not download_url:
            all_download_links = tree.css('a[href*="video/download"]')
            for link in all_download_links:
                href = link.attributes.get('href', '')
                if href and '.mp4' in href:
                    if href.startswith('http'):
                        download_url = href
                    else:
                        download_url = f"{settings.spaces_base_url}{href}" if href.startswith('/') else f"{settings.spaces_base_url}/{href}"
                    break

        video_info = parse_video_info_from_view_page(html_text)

        return {
            'download_url': download_url,
            'description': video_info.get('description'),
            'author_name': video_info.get('author_name'),
            'author_date': video_info.get('author_date')
        }
    except Exception as e:
        logger.error(f"Ошибка парсинга URL скачивания видео из HTML: {e}")
        return {'download_url': None, 'description': None, 'author_name': None, 'author_date': None}
