import io
import zipfile
from app.services.extractor import DocumentExtractor
from app.services.classifier import DocumentClassifier, DocumentType


def test_extract_txt_file():
    sample_text = "Техническое задание на поставку медицинского оборудования.\nКТРУ 26.60.12.119."
    file_bytes = sample_text.encode("utf-8")
    
    res = DocumentExtractor.extract_from_bytes("ТЗ_УЗИ.txt", file_bytes)
    assert res.total_documents == 1
    assert res.total_chars > 0
    assert "КТРУ" in res.documents[0].text_content


def test_extract_zip_archive():
    # Создаем тестовый архив в памяти
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("Техническое_задание.txt", "Описание объекта закупки: Поставка УЗИ аппарата.")
        zf.writestr("Проект_контракта.txt", "Проект государственного контракта. Ответственность сторон: размер штрафа 0.5% в день.")
    
    zip_bytes = zip_buffer.getvalue()
    res = DocumentExtractor.extract_from_bytes("tender_docs.zip", zip_bytes)
    
    assert res.total_documents == 2
    assert len(res.documents) == 2

    # Проверяем классификатор
    classified = DocumentClassifier.classify_all(res.documents)
    types = {c.doc_type for c in classified}
    assert DocumentType.TECH_SPEC in types
    assert DocumentType.CONTRACT_DRAFT in types
