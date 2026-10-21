import io
import os
import zipfile
from typing import List, Tuple
from pydantic import BaseModel, Field

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    from docx import Document as DocxDocument
except ImportError:
    DocxDocument = None


class ExtractedDocument(BaseModel):
    """Структура извлеченного документа."""
    filename: str = Field(description="Имя файла с расширением")
    file_type: str = Field(description="Тип файла: docx, pdf, txt, etc.")
    text_content: str = Field(description="Текстовое содержимое документа")
    page_count: int = Field(default=1, description="Количество страниц (для PDF)")
    char_count: int = Field(default=0, description="Количество символов")
    is_scanned: bool = Field(default=False, description="Признак сканированного PDF с малым кол-вом текста")


class ExtractionResult(BaseModel):
    """Результат распаковки и чтения пакета тендерной документации."""
    documents: List[ExtractedDocument] = Field(default_factory=list)
    total_documents: int = Field(default=0)
    total_chars: int = Field(default=0)
    warnings: List[str] = Field(default_factory=list)


class DocumentExtractor:
    """Сервис распаковки архивов и извлечения текста из DOCX, PDF и TXT."""

    SUPPORTED_EXTENSIONS = {".docx", ".pdf", ".txt", ".md"}

    @classmethod
    def extract_from_multiple_files(cls, files: List[Tuple[str, bytes]]) -> ExtractionResult:
        """Извлекает текст из списка файлов (архивы или отдельные документы)."""
        all_docs: List[ExtractedDocument] = []
        all_warnings: List[str] = []

        for fname, fbytes in files:
            res = cls.extract_from_bytes(fname, fbytes)
            all_docs.extend(res.documents)
            all_warnings.extend(res.warnings)

        return ExtractionResult(
            documents=all_docs,
            total_documents=len(all_docs),
            total_chars=sum(d.char_count for d in all_docs),
            warnings=all_warnings
        )

    @classmethod
    def extract_from_bytes(cls, filename: str, file_bytes: bytes) -> ExtractionResult:
        """Извлекает текст из переданных байтов файла (архив или одиночный файл)."""
        lower_name = filename.lower()

        if lower_name.endswith(".zip"):
            return cls._extract_zip(file_bytes)
        elif lower_name.endswith(".docx"):
            doc = cls._extract_docx(filename, file_bytes)
            return ExtractionResult(
                documents=[doc],
                total_documents=1,
                total_chars=doc.char_count,
                warnings=["Документ пуст"] if doc.char_count == 0 else []
            )
        elif lower_name.endswith(".doc"):
            doc = cls._extract_doc(filename, file_bytes)
            return ExtractionResult(
                documents=[doc],
                total_documents=1,
                total_chars=doc.char_count,
                warnings=["Документ пуст"] if doc.char_count == 0 else []
            )
        elif lower_name.endswith(".pdf"):
            doc = cls._extract_pdf(filename, file_bytes)
            return ExtractionResult(
                documents=[doc],
                total_documents=1,
                total_chars=doc.char_count,
                warnings=["Обнаружен скан без распознанного текстового слоя"] if doc.is_scanned else []
            )
        elif lower_name.endswith((".txt", ".md")):
            doc = cls._extract_txt(filename, file_bytes)
            return ExtractionResult(
                documents=[doc],
                total_documents=1,
                total_chars=doc.char_count
            )
        else:
            return ExtractionResult(
                documents=[],
                total_documents=0,
                total_chars=0,
                warnings=[f"Формат файла '{filename}' не поддерживается. Загрузите .zip, .docx или .pdf."]
            )

    @classmethod
    def _extract_zip(cls, zip_bytes: bytes) -> ExtractionResult:
        """Безопасная распаковка ZIP-архива в памяти с извлечением текста."""
        docs: List[ExtractedDocument] = []
        warnings: List[str] = []

        try:
            with zipfile.ZipFile(io.BytesIO(zip_bytes)) as zf:
                for member in zf.infolist():
                    # Пропуск директорий и скрытых системных файлов macOS/Windows
                    if member.is_dir() or member.filename.startswith("__MACOSX/") or member.filename.startswith("."):
                        continue

                    # Проверка расширения
                    _, ext = os.path.splitext(member.filename.lower())
                    if ext not in cls.SUPPORTED_EXTENSIONS:
                        continue

                    file_data = zf.read(member.filename)
                    base_name = os.path.basename(member.filename)

                    if ext == ".docx":
                        doc = cls._extract_docx(base_name, file_data)
                        docs.append(doc)
                    elif ext == ".pdf":
                        doc = cls._extract_pdf(base_name, file_data)
                        docs.append(doc)
                        if doc.is_scanned:
                            warnings.append(f"Файл '{base_name}' содержит мало текста (возможно, графический скан).")
                    elif ext in (".txt", ".md"):
                        doc = cls._extract_txt(base_name, file_data)
                        docs.append(doc)

        except zipfile.BadZipFile:
            warnings.append("Загруженный файл поврежден или не является корректным ZIP-архивом.")
        except Exception as e:
            warnings.append(f"Ошибка при обработке архива: {str(e)}")

        total_chars = sum(d.char_count for d in docs)
        return ExtractionResult(
            documents=docs,
            total_documents=len(docs),
            total_chars=total_chars,
            warnings=warnings
        )

    @classmethod
    def _extract_docx(cls, filename: str, file_bytes: bytes) -> ExtractedDocument:
        """Извлечение текста и таблиц из DOCX документа."""
        if DocxDocument is None:
            return ExtractedDocument(
                filename=filename,
                file_type="docx",
                text_content="[Ошибка: python-docx не установлен]",
                char_count=0
            )

        text_parts: List[str] = []
        try:
            doc = DocxDocument(io.BytesIO(file_bytes))
            # 1. Параграфы
            for p in doc.paragraphs:
                p_text = p.text.strip()
                if p_text:
                    text_parts.append(p_text)

            # 2. Таблицы (важно для ТЗ и спецификаций)
            for table_idx, table in enumerate(doc.tables, 1):
                table_lines = [f"\n--- Таблица {table_idx} ---"]
                for row in table.rows:
                    row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                    # Удаляем дублирующиеся объединенные ячейки
                    cleaned_row = []
                    for idx, cell_val in enumerate(row_cells):
                        if idx == 0 or cell_val != row_cells[idx - 1]:
                            cleaned_row.append(cell_val)
                    if any(cleaned_row):
                        table_lines.append(" | ".join(cleaned_row))
                text_parts.append("\n".join(table_lines))

            full_text = "\n\n".join(text_parts)
        except Exception as e:
            full_text = f"[Ошибка чтения DOCX файла: {str(e)}]"

        return ExtractedDocument(
            filename=filename,
            file_type="docx",
            text_content=full_text,
            page_count=max(1, len(full_text) // 2500),
            char_count=len(full_text)
        )

    @classmethod
    def _extract_pdf(cls, filename: str, file_bytes: bytes) -> ExtractedDocument:
        """Извлечение текста из PDF документа через PyMuPDF (fitz)."""
        if fitz is None:
            return ExtractedDocument(
                filename=filename,
                file_type="pdf",
                text_content="[Ошибка: PyMuPDF не установлен]",
                char_count=0
            )

        text_parts: List[str] = []
        page_count = 0
        try:
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                page_count = len(doc)
                for page_idx in range(page_count):
                    page = doc[page_idx]
                    page_text = page.get_text("text").strip()
                    if page_text:
                        text_parts.append(f"--- Страница {page_idx + 1} ---\n{page_text}")

            full_text = "\n\n".join(text_parts)
        except Exception as e:
            full_text = f"[Ошибка чтения PDF файла: {str(e)}]"

        char_count = len(full_text)
        # Если в многостраничном PDF в среднем меньше 80 символов на страницу — вероятно, скан
        is_scanned = (page_count > 0 and (char_count / page_count) < 80)

        return ExtractedDocument(
            filename=filename,
            file_type="pdf",
            text_content=full_text,
            page_count=max(1, page_count),
            char_count=char_count,
            is_scanned=is_scanned
        )

    @classmethod
    def _extract_txt(cls, filename: str, file_bytes: bytes) -> ExtractedDocument:
        """Извлечение текста из TXT/MD с автоопределением кодировки (UTF-8, CP1251)."""
        text = ""
        for encoding in ("utf-8", "windows-1251", "cp1251", "latin-1"):
            try:
                text = file_bytes.decode(encoding)
                break
            except UnicodeDecodeError:
                continue

        return ExtractedDocument(
            filename=filename,
            file_type="txt",
            text_content=text,
            page_count=max(1, len(text) // 2500),
            char_count=len(text)
        )

    @classmethod
    def _extract_doc(cls, filename: str, file_bytes: bytes) -> ExtractedDocument:
        """Извлечение текста из файлов формата .doc (Word 97-2003 OLE2 или маскированный docx)."""
        # Если это на самом деле docx (ZIP архив)
        if file_bytes.startswith(b"PK\x03\x04"):
            return cls._extract_docx(filename, file_bytes)

        import re
        text_chunks: List[str] = []

        # Поиск UTF-16LE строк (русские буквы 0x0400..0x04FF и ASCII)
        utf16_matches = re.findall(rb'(?:[\x20-\x7e\r\n\t]\x00|[\x00-\xff]\x04)+', file_bytes)
        for chunk in utf16_matches:
            try:
                decoded = chunk.decode("utf-16le").strip()
                if len(decoded) > 3:
                    text_chunks.append(decoded)
            except Exception:
                pass

        if not text_chunks:
            cp1251_matches = re.findall(rb'[\x20-\x7e\xc0-\xff\r\n\t]{4,}', file_bytes)
            for chunk in cp1251_matches:
                try:
                    decoded = chunk.decode("windows-1251").strip()
                    if len(decoded) > 3:
                        text_chunks.append(decoded)
                except Exception:
                    pass

        full_text = "\n".join(text_chunks)
        return ExtractedDocument(
            filename=filename,
            file_type="doc",
            text_content=full_text,
            page_count=max(1, len(full_text) // 2000),
            char_count=len(full_text),
        )

