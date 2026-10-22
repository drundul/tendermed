import datetime
import logging
from typing import Optional
from openai import OpenAI

from app.config import settings
from app.models.schemas import (
    FullAnalysisReport,
    TrafficLightVerdict,
    RiskCategory,
    RiskSeverity,
    RiskItem,
    MedComplianceAudit,
    TenderSummary,
    EquipmentItem,
    ClarificationRequest,
)
from app.services.prompts import SYSTEM_PROMPT_MED_AUDIT, USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)


class LLMService:
    """Сервис взаимодействия с OpenAI API с поддержкой Structured Outputs и Mock-режима."""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        raw_key = api_key if api_key is not None else settings.openai_api_key
        self.api_key = raw_key.strip() if (raw_key and raw_key != "your_openai_api_key_here") else None
        
        raw_url = base_url if base_url is not None else settings.openai_base_url
        self.base_url = raw_url.strip() if (raw_url and raw_url.strip()) else None

        if self.api_key:
            client_kwargs = {"api_key": self.api_key}
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            self.client = OpenAI(**client_kwargs)
        else:
            self.client = None

    def analyze_tender(
        self,
        context_text: str,
        model_name: Optional[str] = None,
        force_mock: bool = False,
        user_api_key: Optional[str] = None,
    ) -> FullAnalysisReport:
        """Проводит анализ документации через OpenAI или возвращает демонстрационный отчет."""
        effective_model = model_name or settings.openai_model_smart

        # 1. Если принудительно запрошен демо-режим:
        if force_mock:
            logger.info("Возврат эталонного демонстрационного отчета (force_mock=True).")
            return self._generate_mock_report()

        # 2. Выбираем клиент (пользовательский ключ или системный)
        active_client = self.client
        if user_api_key and user_api_key.strip():
            client_kwargs = {"api_key": user_api_key.strip()}
            if self.base_url:
                client_kwargs["base_url"] = self.base_url
            active_client = OpenAI(**client_kwargs)

        if not active_client:
            raise ValueError(
                "API-ключ OpenAI не найден или пуст! Пожалуйста, укажите действующий ключ в боковой панели "
                "слева или включите 'Демо-режим'."
            )

        # 3. Реальный запрос к OpenAI API:
        try:
            logger.info(f"Запуск живого анализа через OpenAI модель '{effective_model}'...")
            prompt = USER_PROMPT_TEMPLATE.format(context_documents=context_text[:120000])

            # Вызов Structured Outputs через бета-парсер Pydantic
            response = active_client.beta.chat.completions.parse(
                model=effective_model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_MED_AUDIT},
                    {"role": "user", "content": prompt},
                ],
                response_format=FullAnalysisReport,
                temperature=0.1,
            )

            report = response.choices[0].message.parsed
            if report:
                report.analysis_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                report.model_used = f"OpenAI {effective_model}"
                report.is_mock = False
                try:
                    from app.services.fas_generator import FASComplaintGenerator
                    report.fas_complaint = FASComplaintGenerator.generate(report)
                except Exception:
                    pass
                return report
            else:
                raise RuntimeError("Модель OpenAI не вернула структурированный ответ.")

        except Exception as e:
            logger.error(f"Ошибка при вызове OpenAI API ({effective_model}): {str(e)}")
            # Пробрасываем реальную ошибку, чтобы пользователь увидел конкретную причину
            raise RuntimeError(f"Ошибка OpenAI API при вызове модели '{effective_model}': {str(e)}") from e

    @staticmethod
    def _generate_mock_report() -> FullAnalysisReport:
        """Создает детальный эталонный образец анализа закупки ультразвукового аппарата."""
        return FullAnalysisReport(
            verdict=TrafficLightVerdict.RED,
            risk_score=82,
            is_mock=True,
            verdict_summary=(
                "КРИТИЧЕСКИЙ РИСК: Закупка содержит признаки преднамеренной заточки под конкретного поставщика оборудования Mindray Resona 7. "
                "Установлен невыполнимый срок поставки (5 календарных дней для высокотехнологичной медтехники) и кабальный размер пени "
                "0.5% за каждый день просрочки, что грубо нарушает Постановление Правительства РФ № 1042."
            ),
            summary=TenderSummary(
                purchase_subject="Поставка ультразвуковой системы экспертного класса для ГБУЗ «Городская клиническая больница № 1»",
                law_type="44-ФЗ",
                nmck_rubles=14850000.0,
                delivery_deadline="5 календарных дней с даты заключения контракта",
                delivery_place="г. Москва, ул. Ленина, д. 14, приемное отделение",
                advance_percent=0.0,
                contract_guarantee_percent=10.0,
                application_guarantee_percent=1.0,
                payment_terms_days=7,
            ),
            risks=[
                RiskItem(
                    category=RiskCategory.TIMING,
                    severity=RiskSeverity.HIGH,
                    title="Нереалистичный срок поставки высокотехнологичной медтехники",
                    description=(
                        "Срок поставки составляет всего 5 календарных дней с момента подписания контракта. "
                        "Для диагностического УЗИ-комплекса с пусконаладкой и инструктажем медицинского персонала "
                        "это непреодолимый барьер для любого поставщика, у которого товар не лежит на локальном складе в данном регионе."
                    ),
                    quote="Раздел 3 проекта контракта: 'Поставка Товара, разгрузка, монтаж и ввод в эксплуатацию осуществляются в течение 5 (пяти) календарных дней'.",
                    law_reference="ч. 2 ст. 33 44-ФЗ, ст. 17 Федерального закона № 135-ФЗ «О защите конкуренции»",
                    recommendation="Подать запрос на разъяснение положений с требованием увеличить срок поставки до разумных 30 календарных дней.",
                ),
                RiskItem(
                    category=RiskCategory.LEGAL,
                    severity=RiskSeverity.HIGH,
                    title="Кабальные пени за просрочку (0.5% в день)",
                    description=(
                        "Заказчик установил размер неустойки (пени) в размере 0.5% от цены контракта за каждый день просрочки. "
                        "При цене 14.85 млн руб. штраф составит 74 250 руб. за каждый день, что в 15 раз превышает законный размер "
                        "по ПП РФ № 1042 (1/300 ключевой ставки ЦБ РФ ≈ 0.05%–0.07% в день)."
                    ),
                    quote="Пункт 8.4 Проекта контракта: 'В случае нарушения срока поставки Поставщик уплачивает Заказчику пеню в размере 0,5 процента от цены Контракта за каждый день просрочки'.",
                    law_reference="ч. 7 ст. 34 44-ФЗ, Постановление Правительства РФ № 1042 от 30.08.2017",
                    recommendation="Направить официальный запрос заказчику с требованием привести условие об ответственности в соответствие с ПП № 1042.",
                ),
                RiskItem(
                    category=RiskCategory.TECHNICAL,
                    severity=RiskSeverity.MEDIUM,
                    title="Признаки ограничения конкуренции (заточка под линейку Mindray Resona)",
                    description=(
                        "Совокупность узких диапазонов частот монокристаллического конвексного датчика (1.2 - 6.0 МГц) "
                        "и запатентованной технологии зонального сканирования исключает поставку эквивалентных аппаратов GE Logiq и Canon Aplio."
                    ),
                    quote="Техническое задание, таблица 2, п. 14: 'Наличие технологии акустического зонного преобразования с частотным диапазоном датчика строго от 1.2 до 6.0 МГц'.",
                    law_reference="п. 1 ч. 1 ст. 33 44-ФЗ (Правила описания объекта закупки)",
                    recommendation="Запросить разъяснение с предложением расширить диапазон частот датчика до 'от 1.0 до 6.5 МГц' для допуска эквивалентов.",
                ),
                RiskItem(
                    category=RiskCategory.MEDICAL,
                    severity=RiskSeverity.MEDIUM,
                    title="Применение национального режима (ПП РФ № 878)",
                    description=(
                        "Код КТРУ 26.60.12.119 подпадает под действие Постановления Правительства РФ № 878 (ограничение допуска радиоэлектроники). "
                        "Действует правило 'третий лишний'. Если в торгах будут поданы хотя бы 2 заявки с отечественным оборудованием из реестра Минпромторга — заявка с иностранным оборудованием будет отклонена."
                    ),
                    quote="Раздел 'Информационная карта': 'Установлены ограничения допуска в соответствии с Постановлением Правительства РФ от 10.07.2019 № 878'.",
                    law_reference="Постановление Правительства РФ № 878, ст. 14 44-ФЗ",
                    recommendation="Проверить наличие в реестре радиоэлектронной продукции Минпромторга аналогичных моделей. При участии с импортным товаром учитывать риск отклонения второй части заявки.",
                ),
            ],
            med_compliance=MedComplianceAudit(
                ru_required=True,
                ru_notes="Требуется действующее регистрационное удостоверение Росздравнадзора. Комплектация оборудования в РУ должна строго совпадать со спецификацией ТЗ.",
                national_regime_applies=True,
                national_regime_details="Применяется ПП РФ № 878 (ограничение допуска иностранной радиоэлектронной продукции). Обязательно подтверждение страны происхождения.",
                ktru_used=True,
                ktru_code="26.60.12.119-00000004: Система ультразвуковой визуализации универсальная",
                installation_and_training=True,
                warranty_period_months=24,
            ),
            equipment=[
                EquipmentItem(
                    name="Ультразвуковая диагностическая система экспертного класса",
                    quantity="1 комплект",
                    key_specs=[
                        "ЖК-монитор высокого разрешения не менее 21.5 дюймов",
                        "Сенсорная командная панель управления диагональю не менее 12 дюймов",
                        "Монокристальный конвексный датчик (диапазон частот 1.2–6.0 МГц)",
                        "Линейный высокоплотный датчик (диапазон частот 3.0–14.0 МГц)",
                        "Секторный фазированный датчик для кардиологических исследований",
                    ],
                    potential_bias_warning="Сочетание параметров датчиков и закрытых протоколов указывает на модель Mindray Resona 7",
                )
            ],
            clarification_requests=[
                ClarificationRequest(
                    subject="О приведении размера неустойки (пени) в соответствие с Постановлением Правительства РФ № 1042",
                    justification="В силу ч. 7 ст. 34 44-ФЗ и ПП РФ № 1042 размер пени не может устанавливаться в произвольном размере 0.5% в день.",
                    draft_text=(
                        "Уважаемый Заказчик!\n\n"
                        "В пункте 8.4 проекта контракта установлено: 'В случае нарушения срока поставки Поставщик уплачивает Заказчику пеню в размере 0,5 процента от цены Контракта за каждый день просрочки'.\n\n"
                        "Обращаем Ваше внимание, что согласно ч. 7 ст. 34 Федерального закона № 44-ФЗ и Постановлению Правительства РФ от 30.08.2017 № 1042 "
                        "пеня начисляется за каждый день просрочки исполнения обязательства в размере одной трехсотой действующей на дату уплаты пени ключевой ставки Банка России от цены контракта.\n\n"
                        "Установление пени в размере 0.5% в день является прямым нарушением норм действующего законодательства о контрактной системе.\n\n"
                        "На основании изложенного, руководствуясь ч. 4 ст. 65 Федерального закона № 44-ФЗ, просим внести изменения в проект государственного контракта и привести условие о размере пени в соответствие с ПП РФ № 1042."
                    ),
                ),
                ClarificationRequest(
                    subject="О разумности срока поставки и недопущении ограничения конкуренции (ст. 33 44-ФЗ)",
                    justification="Срок 5 календарных дней нарушает требования о разумности сроков и ограничивает круг участников торгов (ст. 17 135-ФЗ).",
                    draft_text=(
                        "Уважаемый Заказчик!\n\n"
                        "Согласно Техническому заданию и проекту контракта срок поставки, монтажа и ввода в эксплуатацию сложной ультразвуковой диагностической системы составляет 5 календарных дней.\n\n"
                        "Учитывая специфику высокотехнологичного медицинского оборудования, необходимость бережной транспортировки спецтранспортом с соблюдением температурного режима, "
                        "проведение квалифицированного монтажа и инструктажа медицинского персонала, срок в 5 календарных дней является заведомо неисполнимым для неограниченного круга добросовестных поставщиков "
                        "и ограничивает конкуренцию в нарушение требований ст. 8, ст. 33 Федерального закона № 44-ФЗ и ст. 17 Федерального закона № 135-ФЗ 'О защите конкуренции'.\n\n"
                        "Просим рассмотреть возможность продления срока поставки до разумного периода — не менее 25-30 календарных дней."
                    ),
                ),
            ],
            analysis_timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            model_used="Эталонный образец (Демо-режим)",
        )
        try:
            from app.services.fas_generator import FASComplaintGenerator
            mock_rep.fas_complaint = FASComplaintGenerator.generate(mock_rep)
        except Exception:
            pass
        return mock_rep
