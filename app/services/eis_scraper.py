"""
EIS Scraper — автоматическое скачивание документов с zakupki.gov.ru

Поддерживает любой формат URL с ЕИС:
  - https://zakupki.gov.ru/epz/order/notice/ea20/view/common-info.html?regNumber=0142200001326018834
  - https://zakupki.gov.ru/epz/order/notice/ea20/view/documents.html?regNumber=...
  - https://zakupki.gov.ru/epz/order/notice/ea/view/common-info.html?regNumber=...
  - https://zakupki.gov.ru/epz/order/notice/printForm/viewByVersionNumber.html?regNumber=...

Паттерн файлов ЕИС:
  https://zakupki.gov.ru/44fz/filestore/public/1.0/download/priz/file.html?uid=XXXXXXXX
"""

import re
import logging
from typing import List, Tuple, Optional
from urllib.parse import urljoin, urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Заголовки браузера для обхода простых проверок User-Agent
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": "https://zakupki.gov.ru/",
}

# URL шаблоны страницы документов для различных типов извещений
_DOCS_TEMPLATES = [
    "https://zakupki.gov.ru/epz/order/notice/ea20/view/documents.html?regNumber={reg}",
    "https://zakupki.gov.ru/epz/order/notice/ea/view/documents.html?regNumber={reg}",
    "https://zakupki.gov.ru/epz/order/notice/zk20/view/documents.html?regNumber={reg}",
    "https://zakupki.gov.ru/epz/order/notice/ok20/view/documents.html?regNumber={reg}",
    "https://zakupki.gov.ru/epz/order/notice/outBid/view/documents.html?regNumber={reg}",
    "https://zakupki.gov.ru/epz/order/notice/print223/view/documents.html?regNumber={reg}",
]

# Паттерн ссылок на файлы в ЕИС (filestore download URL)
_FILE_URL_PATTERN = re.compile(
    r"https?://zakupki\.gov\.ru/(?:44fz|epz)/filestore/public/[\d\.]+/download/[^\"'\s]+",
    re.IGNORECASE
)

# Допустимые расширения файлов (которые умеет читать extractor.py)
_ALLOWED_EXTENSIONS = {".docx", ".pdf", ".doc", ".txt", ".zip"}

# Content-Type → расширение (для файлов без расширения в URL)
_CONTENT_TYPE_EXT = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/msword": ".doc",
    "application/pdf": ".pdf",
    "text/plain": ".txt",
    "application/zip": ".zip",
    "application/x-zip-compressed": ".zip",
}


def extract_reg_number(url: str) -> Optional[str]:
    """Извлекает regNumber из любого URL ЕИС/ЕАТ/zakupki.gov.ru."""
    # Из query-параметра ?regNumber=...
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    if "regNumber" in qs:
        return qs["regNumber"][0]

    # Из пути URL (например, /notice/view/<regNumber>)
    match = re.search(r"[?&/](\d{19,})", url)
    if match:
        return match.group(1)

    return None


def _guess_filename(url: str, content_type: str, link_text: str) -> str:
    """Угадывает имя файла из URL, Content-Type или текста ссылки."""
    # Из самого URL (если есть uid= параметр — используем его)
    uid_match = re.search(r"uid=([A-Za-z0-9]+)", url)
    uid = uid_match.group(1)[:12] if uid_match else "file"

    # Определяем расширение
    ext = ""
    for mime, file_ext in _CONTENT_TYPE_EXT.items():
        if mime in content_type.lower():
            ext = file_ext
            break

    if not ext:
        # Попробуем из URL напрямую
        path = urlparse(url).path
        for allowed in _ALLOWED_EXTENSIONS:
            if path.lower().endswith(allowed):
                ext = allowed
                break

    if not ext:
        ext = ".docx"  # По умолчанию DOCX (самый частый формат на zakupki.gov.ru)

    # Красивое название через текст ссылки
    safe_label = re.sub(r"[^\w\s\-]", "", link_text.strip())[:50].strip()
    safe_label = re.sub(r"\s+", "_", safe_label) if safe_label else uid

    return f"{safe_label}{ext}"


import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def _fetch_html(url: str, timeout: int = 20) -> Optional[str]:
    """Скачивает HTML страницы с обработкой ошибок (включая Минцифры SSL CA fallback)."""
    try:
        # Сначала пробуем со стандартной верификацией сертификатов
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=timeout, allow_redirects=True, verify=True)
        except requests.exceptions.SSLError:
            # zakupki.gov.ru использует сертификаты Минцифры (Russian Trusted Root CA)
            resp = requests.get(url, headers=_HEADERS, timeout=timeout, allow_redirects=True, verify=False)

        resp.raise_for_status()
        # zakupki.gov.ru иногда возвращает windows-1251
        if "charset=windows-1251" in resp.headers.get("content-type", "").lower():
            return resp.content.decode("windows-1251")
        return resp.text
    except requests.RequestException as e:
        logger.warning("Не удалось получить HTML страницы %s: %s", url, e)
        return None


def _extract_file_links(html: str, page_url: str) -> List[Tuple[str, str]]:
    """
    Извлекает пары (текст_ссылки, абсолютный_url) для файлов-вложений на странице документов.
    Возвращает только допустимые типы файлов.
    """
    soup = BeautifulSoup(html, "html.parser")
    results: List[Tuple[str, str]] = []
    seen_urls: set = set()

    # 1. Ищем по прямому паттерну filestore URL в атрибутах href
    for a_tag in soup.find_all("a", href=True):
        href: str = a_tag["href"]

        # Строим абсолютный URL
        if href.startswith("//"):
            href = "https:" + href
        elif href.startswith("/"):
            href = urljoin("https://zakupki.gov.ru", href)
        elif not href.startswith("http"):
            href = urljoin(page_url, href)

        # Фильтруем: только filestore ссылки
        if "filestore" not in href and "download" not in href:
            continue

        if href in seen_urls:
            continue
        seen_urls.add(href)

        link_text = a_tag.get_text(strip=True) or "Документ"
        results.append((link_text, href))

    # 2. Fallback: ищем filestore URL прямо в тексте HTML (иногда JS-рендеринг делает ссылки без <a>)
    if not results:
        for url_match in _FILE_URL_PATTERN.finditer(html):
            file_url = url_match.group(0)
            if file_url not in seen_urls:
                seen_urls.add(file_url)
                results.append(("Документ", file_url))

    logger.info("Найдено ссылок на файлы: %d на странице %s", len(results), page_url)
    return results


def _download_file(url: str, link_text: str, timeout: int = 60) -> Optional[Tuple[str, bytes]]:
    """Скачивает файл по URL и возвращает (имя_файла, байты) или None при ошибке."""
    try:
        try:
            resp = requests.get(url, headers=_HEADERS, timeout=timeout, stream=True, verify=True)
        except requests.exceptions.SSLError:
            resp = requests.get(url, headers=_HEADERS, timeout=timeout, stream=True, verify=False)
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        filename = _guess_filename(url, content_type, link_text)

        # Получаем из Content-Disposition если есть
        cd = resp.headers.get("Content-Disposition", "")
        cd_match = re.search(r'filename[*]?=["\']?([^"\';\r\n]+)["\']?', cd)
        if cd_match:
            raw_name = cd_match.group(1).strip().strip('"\'')
            # Декодируем RFC 5987 (filename*=UTF-8''...)
            if raw_name.upper().startswith("UTF-8''"):
                from urllib.parse import unquote
                raw_name = unquote(raw_name[7:])
            elif raw_name.upper().startswith("WINDOWS-1251''"):
                from urllib.parse import unquote
                raw_name = unquote(raw_name[14:]).encode("latin-1").decode("windows-1251")
            
            if raw_name:
                # Если имя в Content-Disposition было в UTF-8, но прочитано как latin-1 (частая проблема RFC 2616):
                try:
                    fixed_name = raw_name.encode("latin-1").decode("utf-8")
                    if any("\u0400" <= c <= "\u04ff" for c in fixed_name):
                        raw_name = fixed_name
                except Exception:
                    pass

                # Проверяем что расширение допустимо
                _, ext = raw_name.rsplit(".", 1) if "." in raw_name else (raw_name, "")
                if f".{ext.lower()}" in _ALLOWED_EXTENSIONS:
                    filename = raw_name

        file_bytes = resp.content
        if not file_bytes:
            logger.warning("Пустой ответ при скачивании файла: %s", url)
            return None

        # Проверяем расширение итогового файла
        _, final_ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        if f".{final_ext.lower()}" not in _ALLOWED_EXTENSIONS:
            # Пробуем угадать по content-type
            for mime, ext_guess in _CONTENT_TYPE_EXT.items():
                if mime in content_type.lower():
                    filename = filename + ext_guess
                    break

        logger.info("Скачан файл: %s (%d байт)", filename, len(file_bytes))
        return filename, file_bytes

    except requests.RequestException as e:
        logger.error("Ошибка скачивания %s: %s", url, e)
        return None


class EISScraper:
    """Скрапер документов с портала ЕИС zakupki.gov.ru."""

    @staticmethod
    def fetch_documents(
        url: str,
        max_files: int = 10,
        timeout: int = 30,
    ) -> Tuple[List[Tuple[str, bytes]], str]:
        """
        Скачивает документы закупки по ссылке с zakupki.gov.ru.

        Args:
            url: Любая ссылка на закупку ЕИС (common-info, documents, printForm и т.д.)
            max_files: Максимальное количество скачиваемых файлов
            timeout: Таймаут HTTP-запросов в секундах

        Returns:
            Tuple:
                - List[(имя_файла, байты)] — список скачанных файлов (может быть пустым)
                - reg_number (str) — извлечённый номер реестровой записи

        Raises:
            ValueError: если URL не является ссылкой zakupki.gov.ru или regNumber не найден
            RuntimeError: если страница документов недоступна ни по одному шаблону URL
        """
        # Валидируем URL
        if "zakupki.gov.ru" not in url:
            raise ValueError(
                f"Ссылка должна быть на zakupki.gov.ru. Получено: {url}"
            )

        # Извлекаем регистрационный номер
        reg_number = extract_reg_number(url)
        if not reg_number:
            raise ValueError(
                "Не удалось извлечь регистрационный номер закупки из ссылки. "
                "Убедитесь, что URL содержит параметр ?regNumber=... или номер в пути."
            )

        logger.info("Обрабатываем закупку №%s", reg_number)

        # Если ссылка уже является страницей документов — пробуем её первой
        docs_urls_to_try = []
        if "view/documents" in url:
            docs_urls_to_try.append(url)

        # Добавляем шаблоны для различных типов процедур
        for template in _DOCS_TEMPLATES:
            candidate = template.format(reg=reg_number)
            if candidate not in docs_urls_to_try:
                docs_urls_to_try.append(candidate)

        # Пробуем по очереди, пока не найдём страницу с файлами
        file_links: List[Tuple[str, str]] = []
        successful_page_url = ""

        for docs_url in docs_urls_to_try:
            logger.info("Пробуем URL документов: %s", docs_url)
            html = _fetch_html(docs_url, timeout=timeout)
            if html is None:
                continue

            links = _extract_file_links(html, docs_url)
            if links:
                file_links = links
                successful_page_url = docs_url
                break
            # Если страница загрузилась, но файлов нет — всё равно продолжаем поиск
            # (мог быть не тот тип извещения)

        if not file_links:
            raise RuntimeError(
                f"Документы для закупки №{reg_number} не найдены на портале ЕИС. "
                f"Попробуйте скачать файлы вручную со страницы «Документы» на zakupki.gov.ru."
            )

        logger.info(
            "Найдено %d ссылок на файлы на странице %s",
            len(file_links),
            successful_page_url,
        )

        # Скачиваем файлы (ограничиваем количество)
        downloaded: List[Tuple[str, bytes]] = []
        for link_text, file_url in file_links[:max_files]:
            result = _download_file(file_url, link_text, timeout=timeout)
            if result:
                downloaded.append(result)

        logger.info(
            "Скачано %d файлов из %d доступных",
            len(downloaded),
            len(file_links),
        )
        return downloaded, reg_number
