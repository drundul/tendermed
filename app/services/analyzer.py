import time
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field

from app.models.schemas import FullAnalysisReport
from app.services.extractor import DocumentExtractor, ExtractedDocument
from app.services.classifier import DocumentClassifier, DocumentType, ClassifiedDocument
from app.services.llm_service import LLMService


class PipelineExecutionResult(BaseModel):
    """Результат выполнения пайплайна анализа."""
    report: FullAnalysisReport
    execution_time_seconds: float
    total_documents: int
    total_characters: int
    classified_documents: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class TenderAnalyzerPipeline:
    """Главный оркестратор сквозного анализа тендерной документации."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.llm_service = LLMService(api_key=api_key, base_url=base_url)

    def process_file_bytes(
        self,
        filename: str,
        file_bytes: bytes,
        model_name: Optional[str] = None,
        force_mock: bool = False,
    ) -> PipelineExecutionResult:
        """Сквозная обработка одного загруженного файла (архив ZIP, PDF, DOCX)."""
        return self.process_files([(filename, file_bytes)], model_name=model_name, force_mock=force_mock)

    def process_files(
        self,
        files: List[Tuple[str, bytes]],
        model_name: Optional[str] = None,
        force_mock: bool = False,
    ) -> PipelineExecutionResult:
        """Сквозная обработка списка файлов (несколько документов или архивов)."""
        start_time = time.time()

        # 1. Извлечение файлов и текстов
        ext_result = DocumentExtractor.extract_from_multiple_files(files)
        if not ext_result.documents:
            # Если документов нет или ошибка формата
            mock_report = self.llm_service.analyze_tender(
                context_text="",
                model_name=model_name,
                force_mock=True
            )
            return PipelineExecutionResult(
                report=mock_report,
                execution_time_seconds=round(time.time() - start_time, 2),
                total_documents=0,
                total_characters=0,
                warnings=ext_result.warnings
            )

        # 2. Классификация документов
        classified = DocumentClassifier.classify_all(ext_result.documents)

        # 3. Формирование приоритезированного контекста для LLM
        # Сначала отдаем ТЗ и Проект контракта (самые критичные для выявления рисков)
        context_parts = []
        doc_summaries = []

        # Сортируем: сначала ТЗ и Контракт, затем Инфокарта, потом остальное
        priority_order = {
            DocumentType.TECH_SPEC: 1,
            DocumentType.CONTRACT_DRAFT: 2,
            DocumentType.INFO_CARD: 3,
            DocumentType.NMCK_JUSTIFICATION: 4,
            DocumentType.OTHER: 5,
        }
        sorted_classified = sorted(classified, key=lambda c: priority_order.get(c.doc_type, 99))

        for c_doc in sorted_classified:
            type_label = {
                DocumentType.TECH_SPEC: "ТЕХНИЧЕСКОЕ ЗАДАНИЕ / СПЕЦИФИКАЦИЯ",
                DocumentType.CONTRACT_DRAFT: "ПРОЕКТ ГОСУДАРСТВЕННОГО КОНТРАКТА",
                DocumentType.INFO_CARD: "ИНФОРМАЦИОННАЯ КАРТА / ТРЕБОВАНИЯ",
                DocumentType.NMCK_JUSTIFICATION: "ОБОСНОВАНИЕ НМЦК",
                DocumentType.OTHER: "ПРИЛОЖЕНИЕ",
            }.get(c_doc.doc_type, "ДОКУМЕНТ")

            doc_summaries.append(f"{c_doc.filename} -> [{type_label}]")
            context_parts.append(
                f"=====================================================\n"
                f"ФАЙЛ: {c_doc.filename} (ТИП: {type_label})\n"
                f"=====================================================\n"
                f"{c_doc.text}\n\n"
            )

        full_context = "".join(context_parts)

        # 4. Запуск LLM анализа
        report = self.llm_service.analyze_tender(
            context_text=full_context,
            model_name=model_name,
            force_mock=force_mock
        )

        elapsed = round(time.time() - start_time, 2)
        return PipelineExecutionResult(
            report=report,
            execution_time_seconds=elapsed,
            total_documents=ext_result.total_documents,
            total_characters=ext_result.total_chars,
            classified_documents=doc_summaries,
            warnings=ext_result.warnings
        )
