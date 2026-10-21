"""
EIS Scraper — Сервис автоматического извлечения и скачивания документов с портала ЕИС (zakupki.gov.ru).

Принимает любую ссылку на закупку (например, раздел сведений, печатную форму или вкладку документов),
автоматически находит раздел прикреплённых документов и скачивает их напрямую в оперативную память
(без промежуточного сохранения на диск) в формате List[Tuple[имя_файла, байты]].
"""

import logging
import re
from typing import List, Optional, Tuple, Union
from urllib.parse import urlparse, parse_qs, urljoin
import urllib3
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Отключаем предупреждения об отключенной SSL-верификации для портала ЕИС
# (zakupki.gov.ru использует сертификаты Национального удостоверяющего центра Минцифры РФ)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Браузерные заголовки для обхода анти-бот защиты ЕИС
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

# Шаблоны URL страниц документов для разных типов извещений на zakupki.gov.ru
_DOCS_TEMPLATES = [
    "https://zakupki.gov.ru/epz/order/notice/ea20/view/documents.html?regNumber={reg}",
    "https://zakupki.gov.ru/epz/order/notice/zk20/view/documents.html?regNumber={reg}",
    "https://zakupki.gov.ru/epz/order/notice/ok20/view/documents.html?regNumber={reg}",
    "https://zakupki.gov.ru/epz/order/notice/ea/view/documents.html?regNumber={reg}",
    "https://zakupki.gov.ru/epz/order/notice/outBid/view/documents.html?regNumber={reg}",
    "https://zakupki.gov.ru/epz/order/notice/print223/view/documents.html?regNumber={reg}",
]

# Паттерн ссылок на файлы в ЕИС (filestore download URL)
_FILE_URL_PATTERN = re.compile(
    r"https?://zakupki\.gov\.ru/(?:44fz|epz)/filestore/public/[\d\.]+/download/[^\"'\s]+",
    re.IGNORECASE
)

# Допустимые расширения файлов
_ALLOWED_EXTENSIONS = {".docx", ".pdf", ".doc", ".txt", ".zip", ".xlsx", ".xls"}

# Content-Type → расширение
_CONTENT_TYPE_EXT = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.ms-excel": ".xls",
    "application/msword": ".doc",
    "application/pdf": ".pdf",
    "text/plain": ".txt",
    "application/zip": ".zip",
    "application/x-zip-compressed": ".zip",
}


def extract_reg_number(url: str) -> Optional[str]:
    """Извлекает regNumber из любого URL ЕИС/ЕАТ/zakupki.gov.ru."""
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)

    # 1. ?regNumber=...
    if "regNumber" in qs and qs["regNumber"]:
        return qs["regNumber"][0].strip()

    # 2. ?noticeNumber=...
    if "noticeNumber" in qs and qs["noticeNumber"]:
        return qs["noticeNumber"][0].strip()

    # 3. 19-значный номер в пути
    match_19 = re.search(r"\b(\d{19})\b", url)
    if match_19:
        return match_19.group(1)

    # 4. 11-значный номер
    match_11 = re.search(r"\b(\d{11})\b", url)
    if match_11:
        return match_11.group(1)

    return None


def _guess_filename(url: str, content_type: str, link_text: str) -> str:
    """Определяет понятное имя файла на основе параметров запроса."""
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    uid = qs.get("uid", ["doc"])[0]

    clean_text = link_text.strip()
    match_ext = re.search(r'\.(docx|xlsx|pdf|doc|xls|zip|txt)\b', clean_text, re.IGNORECASE)
    ext = ""
    if match_ext:
        ext = f".{match_ext.group(1).lower()}"
        clean_text = clean_text[:match_ext.start()].strip()
    else:
        for mime, e in _CONTENT_TYPE_EXT.items():
            if mime in content_type.lower():
                ext = e
                break
        if not ext:
            ext = ".docx"

    safe_label = re.sub(r"[^\w\s\-]", "", clean_text)[:60].strip()
    safe_label = re.sub(r"\s+", "_", safe_label) if safe_label else uid

    return f"{safe_label}{ext}"


def _fetch_html(session: requests.Session, url: str, timeout: int = 10) -> Optional[str]:
    """Скачивает HTML страницы с использованием сессии и cookie."""
    try:
        resp = session.get(url, headers=_HEADERS, timeout=timeout, allow_redirects=True, verify=False)
        resp.raise_for_status()
        if "charset=windows-1251" in resp.headers.get("content-type", "").lower():
            return resp.content.decode("windows-1251", errors="replace")
        return resp.text
    except Exception as e:
        logger.warning("Не удалось получить HTML страницы %s: %s", url, e)
        return None


def _extract_file_links(html: str, page_url: str) -> List[Tuple[str, str]]:
    """Извлекает пары (текст_ссылки, абсолютный_url) для файлов-вложений."""
    soup = BeautifulSoup(html, "html.parser")
    results: List[Tuple[str, str]] = []
    seen_urls: set = set()

    for a_tag in soup.find_all("a", href=True):
        href: str = a_tag["href"]

        if href.startswith("//"):
            href = "https:" + href
        elif href.startswith("/"):
            href = urljoin("https://zakupki.gov.ru", href)
        elif not href.startswith("http"):
            href = urljoin(page_url, href)

        if "filestore" not in href and "download" not in href:
            continue

        if href in seen_urls:
            continue
        seen_urls.add(href)

        link_text = a_tag.get_text(strip=True) or "Документ"
        results.append((link_text, href))

    if not results:
        for url_match in _FILE_URL_PATTERN.finditer(html):
            file_url = url_match.group(0)
            if file_url not in seen_urls:
                seen_urls.add(file_url)
                results.append(("Документ", file_url))

    logger.info("Найдено ссылок на файлы: %d на странице %s", len(results), page_url)
    return results


def _download_file(
    session_or_url: Union[requests.Session, str],
    url_or_link_text: str = "",
    link_text: str = "",
    page_url: str = "",
    timeout: int = 20
) -> Optional[Tuple[str, bytes]]:
    """Скачивает файл по URL в рамках сессии с передачей Referer и Cookie."""
    if isinstance(session_or_url, str):
        session = requests.Session()
        url = session_or_url
        if not link_text and url_or_link_text:
            link_text = url_or_link_text
    else:
        session = session_or_url
        url = url_or_link_text

    try:
        headers = {**_HEADERS}
        if page_url:
            headers["Referer"] = page_url
        resp = session.get(url, headers=headers, timeout=timeout, stream=True, verify=False)
        resp.raise_for_status()

        content_type = resp.headers.get("content-type", "")
        file_bytes = resp.content

        # Проверка на HTML 404/ошибку
        if not file_bytes or (len(file_bytes) < 300 and b"<html" in file_bytes.lower()):
            logger.warning("Ответ является HTML-ошибкой, а не файлом: %s", url)
            return None

        filename = _guess_filename(url, content_type, link_text)

        # Получаем из Content-Disposition если есть
        cd = resp.headers.get("Content-Disposition", "")
        cd_match = re.search(r'filename[*]?=["\']?([^"\';\r\n]+)["\']?', cd)
        if cd_match:
            raw_name = cd_match.group(1).strip().strip('"\'')
            if raw_name.upper().startswith("UTF-8''"):
                from urllib.parse import unquote
                raw_name = unquote(raw_name[7:])
            elif raw_name.upper().startswith("WINDOWS-1251''"):
                from urllib.parse import unquote
                raw_name = unquote(raw_name[14:]).encode("latin-1", errors="replace").decode("windows-1251", errors="replace")
            
            if raw_name:
                try:
                    fixed_name = raw_name.encode("latin-1").decode("utf-8")
                    if any("\u0400" <= c <= "\u04ff" for c in fixed_name):
                        raw_name = fixed_name
                except Exception:
                    pass

                _, ext = raw_name.rsplit(".", 1) if "." in raw_name else (raw_name, "")
                if f".{ext.lower()}" in _ALLOWED_EXTENSIONS:
                    filename = raw_name

        # Проверка magic bytes: если файл назван .doc, но внутри ZIP (PK\x03\x04), это docx!
        if filename.lower().endswith(".doc") and file_bytes.startswith(b"PK\x03\x04"):
            filename = filename[:-4] + ".docx"

        logger.info("Скачан файл: %s (%d байт)", filename, len(file_bytes))
        return filename, file_bytes

    except Exception as e:
        logger.error("Ошибка скачивания %s: %s", url, e)
        return None


class EISFetchResult:
    """Результат работы скрапера: файлы, номер закупки и извлеченные метаданные из ЕИС."""
    def __init__(self, files: List[Tuple[str, bytes]], reg_number: str, metadata: Optional[dict] = None):
        self.files = files
        self.reg_number = reg_number
        self.metadata = metadata or {"reg_number": reg_number}

    def __iter__(self):
        return iter((self.files, self.reg_number, self.metadata))

    def __getitem__(self, idx):
        return (self.files, self.reg_number, self.metadata)[idx]

    def __len__(self):
        return 3


class EISScraper:
    """Скрапер документов и метаданных с портала ЕИС zakupki.gov.ru."""

    @staticmethod
    def extract_metadata_from_html(html: str, reg_number: str) -> dict:
        """Извлекает ключевые сведения о закупке (НМЦК, заказчик, предмет, сроки, ИКЗ, ЭТП) из HTML."""
        soup = BeautifulSoup(html, "html.parser")
        data: dict = {}
        for sec in soup.select('.cardMainInfo__section, .blockInfo__section'):
            title = sec.select_one('.sectionMainInfo__header, .section__title')
            body = sec.select_one('.sectionMainInfo__body, .section__info')
            if title and body:
                k = title.get_text(strip=True)
                v = body.get_text(strip=True)
                data[k] = v

        # НМЦК
        price_str = data.get("Начальная (максимальная) цена контракта")
        clean_price: Optional[float] = None
        if price_str:
            try:
                clean_price = float(re.sub(r"[^\d,]", "", price_str).replace(",", "."))
            except Exception:
                clean_price = None

        # Предмет закупки
        purchase_subject = data.get("Наименование объекта закупки")
        if not purchase_subject:
            subj_el = soup.select_one(".cardMainInfo__content, .cardMainInfo__data, h1")
            if subj_el:
                purchase_subject = subj_el.get_text(strip=True)

        # Заказчик
        customer_name = data.get("Организация, осуществляющая размещение") or data.get("Размещение осуществляет")

        # ИКЗ, ИНН, КПП
        ikz = data.get("Идентификационный код закупки (ИКЗ)")
        customer_inn = None
        customer_kpp = None
        inn_match = re.search(r"ИНН[^\d]{1,15}(\d{10})\b", html)
        if inn_match:
            customer_inn = inn_match.group(1)
        elif ikz and len(ikz) >= 21:
            customer_inn = ikz[2:12]

        kpp_match = re.search(r"КПП[^\d]{1,15}(\d{9})\b", html)
        if kpp_match:
            customer_kpp = kpp_match.group(1)
        elif ikz and len(ikz) >= 21:
            customer_kpp = ikz[12:21]

        # Место и сроки
        delivery_place = data.get("Место поставки товара, выполнения работы или оказания услуги") or data.get("Почтовый адрес")
        delivery_term = data.get("Срок исполнения контракта")
        if data.get("Количество этапов"):
            delivery_term = f"{delivery_term} ({data.get('Количество этапов')} этапов)" if delivery_term else f"{data.get('Количество этапов')} этапов"

        etp_name = data.get("Наименование электронной площадки в информационно-телекоммуникационной сети «Интернет»")
        contract_guarantee = data.get("Размер обеспечения исполнения контракта")
        app_guarantee = data.get("Размер обеспечения заявки")
        deadline = data.get("Дата и время окончания срока подачи заявок")

        return {
            "reg_number": reg_number,
            "purchase_subject": purchase_subject,
            "nmck": clean_price,
            "currency": "RUB",
            "customer_name": customer_name,
            "customer_inn": customer_inn,
            "customer_kpp": customer_kpp,
            "delivery_place": delivery_place,
            "delivery_term": delivery_term,
            "etp_name": etp_name,
            "ikz": ikz,
            "law_type": "44-ФЗ",
            "contract_guarantee": contract_guarantee,
            "application_guarantee": app_guarantee,
            "submission_deadline": deadline,
        }

    @staticmethod
    def fetch_documents(
        url: str,
        max_files: int = 10,
        timeout: int = 15,
    ) -> EISFetchResult:
        """
        Скачивает документы закупки и извлекает метаданные с zakupki.gov.ru с поддержкой сессий и cookie.
        Возвращает EISFetchResult (files, reg_number, metadata).
        """
        if "zakupki.gov.ru" not in url:
            raise ValueError(f"Ссылка должна быть на zakupki.gov.ru. Получено: {url}")

        reg_number = extract_reg_number(url)
        if not reg_number:
            raise ValueError(
                "Не удалось извлечь номер закупки из ссылки. "
                "Убедитесь, что URL содержит ?regNumber=... или номер в пути."
            )

        logger.info("Обрабатываем закупку №%s", reg_number)
        session = requests.Session()

        # 1. Формируем умный список кандидатов URL документов
        docs_urls_to_try: List[str] = []

        # Если в URL уже есть страница /view/common-info или /view/... меняем на /view/documents.html
        if "/view/" in url:
            direct_doc_url = re.sub(r"/view/[^?]+\.html", "/view/documents.html", url)
            docs_urls_to_try.append(direct_doc_url)

        # Определяем тип процедуры из URL (zk20, ea20, ok20, ea, zk)
        for proc in ["zk20", "ea20", "ok20", "ea", "outBid", "print223"]:
            if f"/{proc}/" in url:
                candidate = f"https://zakupki.gov.ru/epz/order/notice/{proc}/view/documents.html?regNumber={reg_number}"
                if candidate not in docs_urls_to_try:
                    docs_urls_to_try.append(candidate)

        # Добавляем остальные шаблоны
        for template in _DOCS_TEMPLATES:
            candidate = template.format(reg=reg_number)
            if candidate not in docs_urls_to_try:
                docs_urls_to_try.append(candidate)

        # 2. Ищем страницу документов
        file_links: List[Tuple[str, str]] = []
        successful_page_url = ""

        for docs_url in docs_urls_to_try:
            logger.info("Пробуем URL документов: %s", docs_url)
            html = _fetch_html(session, docs_url, timeout=timeout)
            if html is None:
                continue

            links = _extract_file_links(html, docs_url)
            if links:
                file_links = links
                successful_page_url = docs_url
                break

        if not file_links:
            raise RuntimeError(
                f"Документы для закупки №{reg_number} не найдены на портале ЕИС. "
                f"Попробуйте прикрепить файлы спецификации и проекта контракта вручную."
            )

        # 3. Скачиваем файлы в рамках сессии
        downloaded: List[Tuple[str, bytes]] = []
        for link_text, file_url in file_links[:max_files]:
            result = _download_file(session, file_url, link_text, successful_page_url, timeout=timeout)
            if result:
                downloaded.append(result)

        if not downloaded:
            raise RuntimeError(
                f"Не удалось скачать файлы для закупки №{reg_number} с сервера ЕИС. "
                f"Попробуйте загрузить файлы вручную."
            )

        # 4. Извлекаем официальные метаданные страницы сведений
        metadata: dict = {"reg_number": reg_number}
        common_info_url = re.sub(r"/view/[^?]+\.html", "/view/common-info.html", url)
        if "/view/" not in common_info_url:
            common_info_url = f"https://zakupki.gov.ru/epz/order/notice/ea20/view/common-info.html?regNumber={reg_number}"

        try:
            logger.info("Извлекаем метаданные закупки: %s", common_info_url)
            common_html = _fetch_html(session, common_info_url, timeout=timeout)
            if common_html:
                metadata = EISScraper.extract_metadata_from_html(common_html, reg_number)
        except Exception as e:
            logger.warning("Не удалось извлечь метаданные из %s: %s", common_info_url, e)

        logger.info("Успешно скачано %d файлов для закупки №%s (НМЦК: %s)", len(downloaded), reg_number, metadata.get("nmck"))
        return EISFetchResult(downloaded, reg_number, metadata)
