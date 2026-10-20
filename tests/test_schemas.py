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


def test_full_analysis_report_schema_valid():
    """Проверка корректной валидации Pydantic модели FullAnalysisReport."""
    sample_report = FullAnalysisReport(
        verdict=TrafficLightVerdict.RED,
        risk_score=85,
        verdict_summary="Обнаружены критические несоответствия: кабальные пени 0.5% в день и нереальный срок поставки 3 дня.",
        summary=TenderSummary(
            purchase_subject="Поставка ультразвуковой диагностической системы",
            law_type="44-ФЗ",
            nmck_rubles=12500000.0,
            delivery_deadline="3 календарных дня с момента заключения контракта",
            advance_percent=0.0,
            contract_guarantee_percent=10.0,
        ),
        risks=[
            RiskItem(
                category=RiskCategory.LEGAL,
                severity=RiskSeverity.HIGH,
                title="Кабальный размер неустойки (пени)",
                description="В проекте контракта установлена пеня 0.5% за каждый день просрочки, что в 15 раз превышает норму ПП РФ № 1042.",
                quote="Пункт 7.3: В случае просрочки поставщик уплачивает пени в размере 0.5% от цены контракта за каждый день.",
                law_reference="ч. 7 ст. 34 44-ФЗ, Постановление Правительства РФ № 1042",
                recommendation="Подать официальный запрос на разъяснение положений с требованием привести условие о неустойке в соответствие с ПП № 1042.",
            )
        ],
        med_compliance=MedComplianceAudit(
            ru_required=True,
            ru_notes="Требуется копия действующего регистрационного удостоверения Росздравнадзора.",
            national_regime_applies=True,
            national_regime_details="Применяется ПП РФ № 878 (ограничение допуска радиоэлектронной продукции).",
            ktru_used=True,
            ktru_code="26.60.12.119-00000010",
        ),
        equipment=[
            EquipmentItem(
                name="Аппарат УЗИ экспертного класса",
                quantity="1 шт.",
                key_specs=["Датчик конвексный 1-6 МГц", "Секторный фазированный датчик"],
                potential_bias_warning="Совокупность частотных диапазонов датчиков соответствует характеристикам Mindray Resona 7",
            )
        ],
        clarification_requests=[
            ClarificationRequest(
                subject="Несоответствие условий контракта о неустойке ПП РФ № 1042",
                justification="Согласно ч. 7 ст. 34 Федерального закона № 44-ФЗ и ПП РФ № 1042...",
                draft_text="Просим разъяснить правомерность установления неустойки 0.5% в день...",
            )
        ],
    )

    assert sample_report.verdict == TrafficLightVerdict.RED
    assert sample_report.risk_score == 85
    assert len(sample_report.risks) == 1
    assert sample_report.risks[0].severity == RiskSeverity.HIGH
