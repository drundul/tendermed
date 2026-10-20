from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class TrafficLightVerdict(str, Enum):
    """Светофор итогового вердикта участия."""
    GREEN = "GREEN"      # 🟢 Участвовать (риски минимальны)
    YELLOW = "YELLOW"    # 🟡 С оговорками (нужны разъяснения или осторожность)
    RED = "RED"          # 🔴 Стоп-фактор (высокий риск РНП, штрафов, заточка)


class RiskCategory(str, Enum):
    """Категория риска в закупке."""
    LEGAL = "LEGAL"              # Штрафы, пени, расторжение, ПП 1042
    TECHNICAL = "TECHNICAL"      # Характеристики, ГОСТы, КТРУ, заточки
    MEDICAL = "MEDICAL"          # РУ Росздравнадзора, ПП 878, нацрежим
    FINANCIAL = "FINANCIAL"      # Обеспечение, оплата, отсутствие аванса
    TIMING = "TIMING"            # Нереалистичные сроки поставки/ввода


class RiskSeverity(str, Enum):
    """Степень критичности риска."""
    HIGH = "HIGH"        # 🔴 Критический стоп-фактор
    MEDIUM = "MEDIUM"    # 🟡 Требует внимания / запроса разъяснений
    LOW = "LOW"          # 🟢 Незначительный / стандартный риск


class RiskItem(BaseModel):
    """Отдельный выявленный риск документации."""
    category: RiskCategory = Field(description="Категория риска")
    severity: RiskSeverity = Field(description="Критичность риска")
    title: str = Field(description="Краткое название риска")
    description: str = Field(description="Подробное объяснение сути риска и последствий")
    quote: Optional[str] = Field(default=None, description="Точная цитата пункта из ТЗ/контракта")
    law_reference: Optional[str] = Field(default=None, description="Ссылка на закон (44-ФЗ, ПП 1042, ПП 878 и др.)")
    recommendation: str = Field(description="Рекомендация поставщику: как минимизировать или устранить")


class MedComplianceAudit(BaseModel):
    """Проверка специфических медицинских и нормативных требований."""
    ru_required: bool = Field(default=True, description="Требуется ли регистрационное удостоверение (РУ) Росздравнадзора")
    ru_notes: str = Field(description="Анализ формулировок касательно РУ и комплектации")
    national_regime_applies: bool = Field(default=False, description="Применяется ли ст. 14 44-ФЗ / ПП РФ № 878")
    national_regime_details: str = Field(description="Анализ ограничений допуска, статус радиоэлектроники, реестр Минпромторга")
    ktru_used: bool = Field(default=False, description="Использована ли позиция КТРУ")
    ktru_code: Optional[str] = Field(default=None, description="Код позиции КТРУ, если обнаружен")
    installation_and_training: bool = Field(default=False, description="Требуются ли монтаж, пусконаладка и инструктаж медперсонала")
    warranty_period_months: Optional[int] = Field(default=None, description="Гарантийный срок (в месяцах)")


class TenderSummary(BaseModel):
    """Базовые параметры закупки, извлеченные из документации."""
    purchase_subject: str = Field(description="Наименование объекта закупки")
    law_type: str = Field(default="44-ФЗ", description="Федеральный закон (44-ФЗ или 223-ФЗ)")
    nmck_rubles: Optional[float] = Field(default=None, description="Начальная (максимальная) цена контракта в рублях")
    delivery_deadline: Optional[str] = Field(default=None, description="Срок и график поставки оборудования")
    delivery_place: Optional[str] = Field(default=None, description="Место поставки (город, ЛПУ)")
    advance_percent: Optional[float] = Field(default=None, description="Размер аванса в процентах (0 если нет)")
    contract_guarantee_percent: Optional[float] = Field(default=None, description="Обеспечение исполнения контракта (%)")
    application_guarantee_percent: Optional[float] = Field(default=None, description="Обеспечение заявки (%)")
    payment_terms_days: Optional[int] = Field(default=7, description="Срок оплаты заказчиком (в рабочих/календарных днях)")


class EquipmentItem(BaseModel):
    """Позиция медицинского оборудования из спецификации ТЗ."""
    name: str = Field(description="Наименование оборудования")
    quantity: Optional[str] = Field(default="1 шт.", description="Количество")
    key_specs: List[str] = Field(default_factory=list, description="Ключевые технические характеристики")
    potential_bias_warning: Optional[str] = Field(
        default=None, 
        description="Признак заточки под конкретного производителя/модель (если обнаружен)"
    )


class ClarificationRequest(BaseModel):
    """Черновик официального запроса на разъяснение положений извещения в ЕИС."""
    subject: str = Field(description="Краткая суть спорного пункта ТЗ или контракта")
    justification: str = Field(description="Нормативно-правовое обоснование (ст. 33 44-ФЗ, 135-ФЗ, ПП 1042)")
    draft_text: str = Field(description="Готовый текст запроса к заказчику для подачи через электронную площадку")


class FullAnalysisReport(BaseModel):
    """Полный структурированный отчет ИИ-экспертизы тендера."""
    verdict: TrafficLightVerdict = Field(description="Итоговый светофор (GREEN / YELLOW / RED)")
    risk_score: int = Field(ge=0, le=100, description="Индекс риска от 0 (безопасно) до 100 (критично)")
    verdict_summary: str = Field(description="Краткое резюме для руководителя: почему такой вердикт и что делать")
    summary: TenderSummary = Field(description="Параметры контракта")
    risks: List[RiskItem] = Field(default_factory=list, description="Список выявленных рисков")
    med_compliance: MedComplianceAudit = Field(description="Медицинский и регуляторный комплаенс")
    equipment: List[EquipmentItem] = Field(default_factory=list, description="Спецификация оборудования")
    clarification_requests: List[ClarificationRequest] = Field(
        default_factory=list, 
        description="Готовые проекты запросов на разъяснение положений документации"
    )
    analysis_timestamp: Optional[str] = Field(default=None, description="Время проведения анализа")
    model_used: Optional[str] = Field(default=None, description="Использованная модель ИИ")
