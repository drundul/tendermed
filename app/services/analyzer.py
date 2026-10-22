import time
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field

from app.models.schemas import FullAnalysisReport, ContextOptimizationStats
from app.services.extractor import DocumentExtractor, ExtractedDocument
from app.services.classifier import DocumentClassifier, DocumentType, ClassifiedDocument
from app.services.anonymizer import DataAnonymizer, AnonymizationStats
from app.services.context_optimizer import ContextOptimizer
from app.services.llm_service import LLMService


class PipelineExecutionResult(BaseModel):
    """Результат выполнения пайплайна анализа."""
    report: FullAnalysisReport
    execution_time_seconds: float
    total_documents: int
    total_characters: int
    classified_documents: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    anonymization_stats: AnonymizationStats = Field(default_factory=AnonymizationStats)
    optimization_stats: Optional[ContextOptimizationStats] = None


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
        tender_metadata: Optional[dict] = None,
        user_api_key: Optional[str] = None,
    ) -> PipelineExecutionResult:
        """Сквозная обработка одного загруженного файла (архив ZIP, PDF, DOCX)."""
        return self.process_files(
            [(filename, file_bytes)],
            model_name=model_name,
            force_mock=force_mock,
            tender_metadata=tender_metadata,
            user_api_key=user_api_key,
        )

    def process_files(
        self,
        files: List[Tuple[str, bytes]],
        model_name: Optional[str] = None,
        force_mock: bool = False,
        tender_metadata: Optional[dict] = None,
        user_api_key: Optional[str] = None,
    ) -> PipelineExecutionResult:
        """Сквозная обработка списка файлов (несколько документов или архивов)."""
        start_time = time.time()

        # 1. Извлечение файлов и текстов
        ext_result = DocumentExtractor.extract_from_multiple_files(files)
        if not ext_result.documents:
            # Если документов нет или ошибка формата
            from app.services.heuristic_analyzer import HeuristicAnalyzer
            mock_report = HeuristicAnalyzer.analyze([], "", metadata=tender_metadata)
            return PipelineExecutionResult(
                report=mock_report,
                execution_time_seconds=round(time.time() - start_time, 2),
                total_documents=0,
                total_characters=0,
                warnings=ext_result.warnings
            )

        # 1.1 Микро-анонимизация персональных данных (152-ФЗ) перед классификацией и LLM
        total_anonymization_stats = AnonymizationStats()
        for doc in ext_result.documents:
            cleaned_text, doc_stats = DataAnonymizer.anonymize_text(doc.text_content)
            doc.text_content = cleaned_text
            total_anonymization_stats.phones_count += doc_stats.phones_count
            total_anonymization_stats.emails_count += doc_stats.emails_count
            total_anonymization_stats.passports_count += doc_stats.passports_count
            total_anonymization_stats.snils_count += doc_stats.snils_count
            total_anonymization_stats.personal_inn_count += doc_stats.personal_inn_count
            total_anonymization_stats.bank_cards_count += doc_stats.bank_cards_count

        # 2. Классификация документов
        classified = DocumentClassifier.classify_all(ext_result.documents)

        # 3. Формирование приоритезированного контекста для LLM
        # 3. Интеллектуальная оптимизация и сжатие контекста перед отправкой в LLM (Token Optimization)
        priority_order = {
            DocumentType.TECH_SPEC: 1,
            DocumentType.CONTRACT_DRAFT: 2,
            DocumentType.INFO_CARD: 3,
            DocumentType.NMCK_JUSTIFICATION: 4,
            DocumentType.OTHER: 5,
        }
        sorted_classified = sorted(classified, key=lambda c: priority_order.get(c.doc_type, 99))
        doc_summaries = []

        for c_doc in sorted_classified:
            type_label = {
                DocumentType.TECH_SPEC: "ТЕХНИЧЕСКОЕ ЗАДАНИЕ / СПЕЦИФИКАЦИЯ",
                DocumentType.CONTRACT_DRAFT: "ПРОЕКТ ГОСУДАРСТВЕННОГО КОНТРАКТА",
                DocumentType.INFO_CARD: "ИНФОРМАЦИОННАЯ КАРТА / ТРЕБОВАНИЯ",
                DocumentType.NMCK_JUSTIFICATION: "ОБОСНОВАНИЕ НМЦК",
                DocumentType.OTHER: "ПРИЛОЖЕНИЕ",
            }.get(c_doc.doc_type, "ДОКУМЕНТ")
            doc_summaries.append(f"{c_doc.filename} -> [{type_label}]")

        # Применяем интеллектуальное удаление шума и выделение критических разделов
        optimized_context, opt_stats = ContextOptimizer.optimize_classified_documents(sorted_classified)

        # 4. Запуск анализа: LLM (если есть ключ) или встроенный эвристический анализатор
        has_key = bool(self.llm_service.api_key or (user_api_key and user_api_key.strip()))
        if force_mock or not has_key:
            from app.services.heuristic_analyzer import HeuristicAnalyzer
            report = HeuristicAnalyzer.analyze(
                sorted_classified, 
                optimized_context, 
                metadata=tender_metadata,
                optimization_stats=opt_stats,
            )
        else:
            try:
                report = self.llm_service.analyze_tender(
                    context_text=optimized_context,
                    model_name=model_name,
                    force_mock=False,
                    user_api_key=user_api_key,
                    optimization_stats=opt_stats,
                )
                if tender_metadata:
                    if tender_metadata.get("nmck") and (not report.summary.nmck_rubles or report.summary.nmck_rubles == 0):
                        report.summary.nmck_rubles = tender_metadata["nmck"]
                    if tender_metadata.get("customer_name") and (not report.summary.customer_name or "не указан" in report.summary.customer_name.lower()):
                        report.summary.customer_name = tender_metadata["customer_name"]
                    if tender_metadata.get("purchase_subject") and (not report.summary.purchase_subject or "не указан" in report.summary.purchase_subject.lower()):
                        report.summary.purchase_subject = tender_metadata["purchase_subject"]
                    if tender_metadata.get("customer_inn") and not report.summary.customer_inn:
                        report.summary.customer_inn = tender_metadata["customer_inn"]
                    if tender_metadata.get("customer_kpp") and not report.summary.customer_kpp:
                        report.summary.customer_kpp = tender_metadata["customer_kpp"]
                    if tender_metadata.get("delivery_place") and not report.summary.delivery_place:
                        report.summary.delivery_place = tender_metadata["delivery_place"]
                    if tender_metadata.get("delivery_term") and not report.summary.delivery_deadline:
                        report.summary.delivery_deadline = tender_metadata["delivery_term"]
                    if tender_metadata.get("etp_name") and not report.summary.etp_name:
                        report.summary.etp_name = tender_metadata["etp_name"]
                    if tender_metadata.get("reg_number") and not report.summary.notice_number:
                        report.summary.notice_number = tender_metadata["reg_number"]
                    if tender_metadata.get("ikz") and not report.summary.ikz:
                        report.summary.ikz = tender_metadata["ikz"]
            except Exception as e:
                from app.services.heuristic_analyzer import HeuristicAnalyzer
                report = HeuristicAnalyzer.analyze(
                    sorted_classified, 
                    optimized_context, 
                    metadata=tender_metadata,
                    optimization_stats=opt_stats,
                )
                report.verdict_summary = f"[ИИ API временно недоступен ({str(e)}). Аудит выполнен экспертным модулем 44-ФЗ]\n" + report.verdict_summary

        elapsed = round(time.time() - start_time, 2)
        return PipelineExecutionResult(
            report=report,
            execution_time_seconds=elapsed,
            total_documents=ext_result.total_documents,
            total_characters=ext_result.total_chars,
            classified_documents=doc_summaries,
            warnings=ext_result.warnings,
            anonymization_stats=total_anonymization_stats,
            optimization_stats=opt_stats,
        )
