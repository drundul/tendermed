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
    """Базовые параметры закупки и реквизиты сторон, извлеченные из документации."""
    purchase_subject: str = Field(description="Наименование объекта закупки")
    law_type: str = Field(default="44-ФЗ", description="Федеральный закон (44-ФЗ или 223-ФЗ)")
    notice_number: Optional[str] = Field(default=None, description="Номер извещения закупки (например, 0859200001126012552)")
    ikz: Optional[str] = Field(default=None, description="Идентификационный код закупки (ИКЗ)")
    etp_name: Optional[str] = Field(default=None, description="Электронная торговая площадка (РТС-тендер, Сбербанк-АСТ, ЕЭТП и др.)")
    customer_name: Optional[str] = Field(default=None, description="Полное наименование заказчика (ЛПУ/учреждения)")
    customer_inn: Optional[str] = Field(default=None, description="ИНН Заказчика")
    customer_kpp: Optional[str] = Field(default=None, description="КПП Заказчика")
    customer_address: Optional[str] = Field(default=None, description="Юридический и/или фактический адрес доставки/заказчика")
    customer_signer: Optional[str] = Field(default=None, description="Уполномоченное лицо заказчика (должность, ФИО, основание полномочий из преамбулы)")
    nmck_rubles: Optional[float] = Field(default=None, description="Начальная (максимальная) цена контракта в рублях")
    delivery_deadline: Optional[str] = Field(default=None, description="Срок и график поставки оборудования")
    delivery_place: Optional[str] = Field(default=None, description="Место поставки (город, ЛПУ)")
    advance_percent: Optional[float] = Field(default=None, description="Размер аванса в процентах (0 если нет)")
    contract_guarantee_percent: Optional[float] = Field(default=None, description="Обеспечение исполнения контракта (%)")
    application_guarantee_percent: Optional[float] = Field(default=None, description="Обеспечение заявки (%)")
    payment_terms_days: Optional[int] = Field(default=7, description="Срок оплаты заказчиком (в рабочих/календарных днях)")


class EquipmentItem(BaseModel):
    """Позиция медицинского оборудования из спецификации ТЗ с глубоким аудитом заточек."""
    name: str = Field(description="Наименование оборудования/медизделия")
    quantity: Optional[str] = Field(default="1 шт.", description="Количество")
    ktru_code: Optional[str] = Field(default=None, description="Код позиции КТРУ (если указан)")
    key_specs: List[str] = Field(default_factory=list, description="Ключевые технические характеристики из ТЗ")
    potential_bias_warning: Optional[str] = Field(
        default=None, 
        description="Краткий индикатор заточки (например: Заточка под Medtronic / Abbott)"
    )
    detected_brand_bias: Optional[str] = Field(
        default=None,
        description="Подробный экспертный разбор скрытой заточки: какие именно параметры (вес до грамма, габариты в мм, алгоритмы) указывают на конкретного производителя и исключают аналоги"
    )
    suggested_neutral_specs: Optional[str] = Field(
        default=None,
        description="Рекомендации поставщику: какие характеристики оспорить в запросе для допуска аналогов"
    )


class ClarificationRequest(BaseModel):
    """Официальный юридический запрос на разъяснение положений извещения в ЕИС."""
    subject: str = Field(description="Краткая суть спорного пункта ТЗ или контракта")
    recipient_header: str = Field(
        default="",
        description="Официальная шапка запроса с реквизитами Заказчика (Кому, Куда, В лице кого, Извещение №, ЭТП)"
    )
    justification: str = Field(description="Нормативно-правовое обоснование (ст. 33, ст. 34, ст. 65 44-ФЗ, 135-ФЗ, ПП 1042)")
    draft_text: str = Field(description="Полный официальный текст письма-запроса, готовый к подаче на ЭТП")


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
    is_mock: bool = Field(default=False, description="Признак демонстрационного эталона")


# ===================== API DTO SCHEMAS =====================

class UserRegisterRequest(BaseModel):
    email: str
    password: str
    company_name: Optional[str] = None


class UserLoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    available_credits: int
    email: str


class UserResponse(BaseModel):
    id: int
    email: str
    company_name: Optional[str] = None
    available_credits: int
    is_active: bool

    class Config:
        from_attributes = True


class TenderEISMetadata(BaseModel):
    """Официальные метаданные извещения, извлеченные со страницы ЕИС."""
    reg_number: str
    purchase_subject: Optional[str] = None
    nmck: Optional[float] = None
    currency: str = "RUB"
    customer_name: Optional[str] = None
    customer_inn: Optional[str] = None
    customer_kpp: Optional[str] = None
    delivery_place: Optional[str] = None
    delivery_term: Optional[str] = None
    etp_name: Optional[str] = None
    ikz: Optional[str] = None
    law_type: str = "44-ФЗ"
    application_guarantee: Optional[str] = None
    contract_guarantee: Optional[str] = None
    submission_deadline: Optional[str] = None


class AnalyzeUrlRequest(BaseModel):
    url: str
    model_name: Optional[str] = "gpt-5.4-mini"
    demo_mode: Optional[bool] = False
    api_key: Optional[str] = None


class AuditSummaryResponse(BaseModel):
    id: int
    notice_number: Optional[str] = None
    purchase_subject: str
    customer_name: Optional[str] = None
    law_type: str
    verdict: str
    risk_score: int
    created_at: str

    class Config:
        from_attributes = True

