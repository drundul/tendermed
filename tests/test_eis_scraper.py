import pytest
from unittest.mock import patch, MagicMock
from app.services.eis_scraper import (
    extract_reg_number,
    _extract_file_links,
    _guess_filename,
    EISScraper,
)


def test_extract_reg_number_common_info():
    url = "https://zakupki.gov.ru/epz/order/notice/ea20/view/common-info.html?regNumber=0142200001326018834"
    assert extract_reg_number(url) == "0142200001326018834"


def test_extract_reg_number_documents_tab():
    url = "https://zakupki.gov.ru/epz/order/notice/ea20/view/documents.html?regNumber=0142200001326018834"
    assert extract_reg_number(url) == "0142200001326018834"


def test_extract_reg_number_print_form():
    url = "https://zakupki.gov.ru/epz/order/notice/printForm/viewByVersionNumber.html?regNumber=0859200001126012552&versionNumber=1&qualifier=regNumberAndVersion"
    assert extract_reg_number(url) == "0859200001126012552"


def test_extract_reg_number_invalid():
    assert extract_reg_number("https://google.com/search?q=tender") is None


def test_guess_filename():
    url = "https://zakupki.gov.ru/44fz/filestore/public/1.0/download/priz/file.html?uid=01A11ACFC64C7F86A213C0C5313C6C5D"
    content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    link_text = "Обоснование НМЦК"
    name = _guess_filename(url, content_type, link_text)
    assert name.endswith(".docx")
    assert "Обоснование_НМЦК" in name


def test_extract_file_links_from_html():
    sample_html = """
    <html>
        <body>
            <div class="blockFiles">
                <a href="https://zakupki.gov.ru/44fz/filestore/public/1.0/download/priz/file.html?uid=AAA111">Проект контракта</a>
                <a href="/44fz/filestore/public/1.0/download/priz/file.html?uid=BBB222">Техническое задание</a>
                <a href="https://zakupki.gov.ru/epz/main/public/siteMap.html">Карта сайта</a>
            </div>
        </body>
    </html>
    """
    links = _extract_file_links(sample_html, "https://zakupki.gov.ru/epz/order/notice/ea20/view/documents.html?regNumber=0142200001326018834")
    assert len(links) == 2
    assert links[0][0] == "Проект контракта"
    assert "uid=AAA111" in links[0][1]
    assert links[1][0] == "Техническое задание"
    assert links[1][1].startswith("https://zakupki.gov.ru/")
    assert "uid=BBB222" in links[1][1]


@patch("app.services.eis_scraper.requests.Session")
def test_eis_scraper_fetch_documents_mock(mock_session_cls):
    sample_html = """
    <html>
        <body>
            <a href="https://zakupki.gov.ru/44fz/filestore/public/1.0/download/priz/file.html?uid=12345">Проект контракта</a>
        </body>
    </html>
    """

    # Ответ на запрос страницы
    resp_page = MagicMock()
    resp_page.headers = {"content-type": "text/html; charset=utf-8"}
    resp_page.text = sample_html
    resp_page.content = sample_html.encode("utf-8")
    resp_page.raise_for_status = MagicMock()

    # Ответ на скачивание файла
    resp_file = MagicMock()
    resp_file.headers = {
        "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "Content-Disposition": 'attachment; filename="Contract_Project.docx"'
    }
    resp_file.content = b"PK\x03\x04mock docx content"
    resp_file.raise_for_status = MagicMock()

    mock_session = MagicMock()
    # Поочередно отдаем страницу, затем файл
    mock_session.get.side_effect = [resp_page, resp_file]
    mock_session_cls.return_value = mock_session

    files, reg = EISScraper.fetch_documents("https://zakupki.gov.ru/epz/order/notice/ea20/view/common-info.html?regNumber=0142200001326018834")
    
    assert reg == "0142200001326018834"
    assert len(files) == 1
    filename, content = files[0]
    assert filename == "Contract_Project.docx"
    assert content == b"PK\x03\x04mock docx content"


@patch("app.services.eis_scraper.requests.Session")
def test_download_file_mojibake_decoded(mock_session_cls):
    from app.services.eis_scraper import _download_file
    
    resp_file = MagicMock()
    # "Проект контракта.docx" in UTF-8 decoded as latin-1
    mojibake = "Проект контракта.docx".encode("utf-8").decode("latin-1")
    resp_file.headers = {
        "content-type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "Content-Disposition": f'attachment; filename="{mojibake}"'
    }
    resp_file.content = b"sample_bytes"
    resp_file.raise_for_status = MagicMock()

    mock_session = MagicMock()
    mock_session.get.return_value = resp_file
    mock_session_cls.return_value = mock_session

    result = _download_file("https://zakupki.gov.ru/fake_url", "Проект")
    assert result is not None
    filename, _ = result
    assert filename == "Проект контракта.docx"

