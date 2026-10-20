from enum import Enum
from typing import Dict, List
from app.services.extractor import ExtractedDocument


class DocumentType(str, Enum):
    """Тип документа в составе извещения."""
    TECH_SPEC = "TECH_SPEC"              # Техническое задание / Описание объекта закупки
    CONTRACT_DRAFT = "CONTRACT_DRAFT"    # Проект контракта / Договора
    INFO_CARD = "INFO_CARD"              # Информационная карта / Инструкция к заявке
    NMCK_JUSTIFICATION = "NMCK"          # Обоснование НМЦК
    OTHER = "OTHER"                      # Прочие приложения


class ClassifiedDocument:
    """Обертка над документом с присвоенным типом и приоритетом анализа."""
    def __init__(self, doc: ExtractedDocument, doc_type: DocumentType, score: float):
        self.doc = doc
        self.doc_type = doc_type
        self.score = score

    @property
    def filename(self) -> str:
        return self.doc.filename

    @property
    def text(self) -> str:
        return self.doc.text_content


class DocumentClassifier:
    """Эвристический классификатор тендерных документов по имени и содержимому."""

    # Маркеры в имени файла
    FILENAME_MARKERS: Dict[DocumentType, List[str]] = {
        DocumentType.TECH_SPEC: ["тз", "тех", "специфик", "описание", "характер", "оборудован", "приложение_1", "приложение 1"],
        DocumentType.CONTRACT_DRAFT: ["контракт", "договор", "проект_контракта", "проект контракта", "документация", "приложение_2"],
        DocumentType.INFO_CARD: ["инфо", "карта", "инструкц", "требован", "заявк", "извещен"],
        DocumentType.NMCK_JUSTIFICATION: ["нмцк", "обоснован", "расчет", "смета"],
    }

    # Маркеры в первых 2000 символов текста
    CONTENT_MARKERS: Dict[DocumentType, List[str]] = {
        DocumentType.TECH_SPEC: [
            "описание объекта закупки",
            "техническое задание",
            "спецификация товара",
            "технические характеристики",
            "каталог товаров, работ, услуг",
            "ктру",
            "требования к функциональным",
            "комплект поставки",
        ],
        DocumentType.CONTRACT_DRAFT: [
            "проект государственного контракта",
            "государственный контракт №",
            "проект договора",
            "ответственность сторон",
            "размер штрафа",
            "настоящий контракт заключен",
            "порядок оплаты",
            "банковская гарантия",
        ],
        DocumentType.INFO_CARD: [
            "информационная карта",
            "инструкция по заполнению",
            "требования к составу заявки",
            "размер обеспечения заявки",
            "критерии оценки заявок",
        ],
        DocumentType.NMCK_JUSTIFICATION: [
            "обоснование начальной (максимальной) цены",
            "метод сопоставимых рыночных цен",
            "коммерческое предложение",
            "расчет нмцк",
        ],
    }

    @classmethod
    def classify(cls, doc: ExtractedDocument) -> ClassifiedDocument:
        """Определяет категорию документа по имени и содержимому."""
        fname_lower = doc.filename.lower()
        content_sample = doc.text_content[:3000].lower()

        scores: Dict[DocumentType, float] = {
            DocumentType.TECH_SPEC: 0.0,
            DocumentType.CONTRACT_DRAFT: 0.0,
            DocumentType.INFO_CARD: 0.0,
            DocumentType.NMCK_JUSTIFICATION: 0.0,
        }

        # 1. Анализ имени файла (вес 2.0)
        for doc_type, markers in cls.FILENAME_MARKERS.items():
            for m in markers:
                if m in fname_lower:
                    scores[doc_type] += 2.0
                    break

        # 2. Анализ текста (вес 1.5 за каждое вхождение)
        for doc_type, markers in cls.CONTENT_MARKERS.items():
            for m in markers:
                if m in content_sample:
                    scores[doc_type] += 1.5

        # Выбираем категорию с наивысшим баллом
        best_type, best_score = max(scores.items(), key=lambda item: item[1])

        if best_score < 1.0:
            best_type = DocumentType.OTHER

        return ClassifiedDocument(doc=doc, doc_type=best_type, score=best_score)

    @classmethod
    def classify_all(cls, docs: List[ExtractedDocument]) -> List[ClassifiedDocument]:
        """Классифицирует список документов."""
        return [cls.classify(d) for d in docs]
