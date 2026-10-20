from app.models.schemas import FullAnalysisReport, TrafficLightVerdict, RiskSeverity


class ReportExporter:
    """Генерация форматированного отчета для скачивания или отправки руководству."""

    @classmethod
    def to_markdown(cls, report: FullAnalysisReport) -> str:
        """Преобразует аналитический отчет в профессиональный Markdown-документ."""
        verdict_icon = {
            TrafficLightVerdict.GREEN: "🟢 УЧАСТВОВАТЬ (РИСКИ МИНИМАЛЬНЫ)",
            TrafficLightVerdict.YELLOW: "🟡 С ОГОВОРКАМИ (ТРЕБУЕТСЯ ЗАПРОС РАЗЪЯСНЕНИЙ)",
            TrafficLightVerdict.RED: "🔴 СТОП-ФАКТОРЫ (ВЫСОКИЙ РИСК ПОТЕРИ ДЕНЕГ / РНП)",
        }.get(report.verdict, "ВЕРДИКТ НЕ ОПРЕДЕЛЕН")

        lines = [
            "# ЭКСПЕРТНОЕ ЗАКЛЮЧЕНИЕ ПО ТЕНДЕРНОЙ ДОКУМЕНТАЦИИ",
            f"**Объект закупки:** {report.summary.purchase_subject}",
            f"**Законодательство:** {report.summary.law_type}",
            f"**Извещение №:** {report.summary.notice_number or 'Не указан'} | **ЭТП:** {report.summary.etp_name or 'Не указана'}",
            f"**Заказчик:** {report.summary.customer_name or 'Не указан'}",
            f"**В лице:** {report.summary.customer_signer or 'Руководителя учреждения'}",
            f"**Адрес заказчика / поставки:** {report.summary.customer_address or report.summary.delivery_place or 'Не указан'}",
            f"**ИКЗ:** {report.summary.ikz or 'Не указан'}",
            f"**Дата анализа:** {report.analysis_timestamp or 'Н/Д'}",
            f"**Аналитический движок:** {report.model_used or 'TenderAI Med'}",
            "",
            "---",
            f"## ИТОГОВЫЙ ВЕРДИКТ: {verdict_icon}",
            f"**Индекс риска:** {report.risk_score} / 100",
            f"> **Резюме для руководства:** {report.verdict_summary}",
            "",
            "---",
            "## 1. КЛЮЧЕВЫЕ ПАРАМЕТРЫ КОНТРАКТА",
            f"- **НМЦК:** {f'{report.summary.nmck_rubles:,.2f} ₽'.replace(',', ' ') if report.summary.nmck_rubles else 'Не указана'}",
            f"- **Срок поставки:** {report.summary.delivery_deadline or 'Не указан'}",
            f"- **Аванс:** {f'{report.summary.advance_percent}%' if report.summary.advance_percent is not None else 'Без аванса'}",
            f"- **Обеспечение исполнения контракта:** {f'{report.summary.contract_guarantee_percent}%' if report.summary.contract_guarantee_percent is not None else 'Не установлено'}",
            f"- **Обеспечение заявки:** {f'{report.summary.application_guarantee_percent}%' if report.summary.application_guarantee_percent is not None else 'Не установлено'}",
            f"- **Срок оплаты:** {report.summary.payment_terms_days or 7} рабочих дней",
            "",
            "---",
            "## 2. МАТРИЦА ВЫЯВЛЕННЫХ РИСКОВ",
        ]

        if not report.risks:
            lines.append("Критических рисков и нарушений законодательства не выявлено.")
        else:
            for idx, risk in enumerate(report.risks, 1):
                sev_icon = {
                    RiskSeverity.HIGH: "🔴 ВЫСОКИЙ",
                    RiskSeverity.MEDIUM: "🟡 УМЕРЕННЫЙ",
                    RiskSeverity.LOW: "🟢 НИЗКИЙ",
                }.get(risk.severity, "ИНФО")

                lines.extend([
                    f"### {idx}. [{sev_icon}] {risk.title} ({risk.category.value})",
                    f"- **Суть риска:** {risk.description}",
                ])
                if risk.quote:
                    lines.append(f"- **Цитата из документа:** *«{risk.quote}»*")
                if risk.law_reference:
                    lines.append(f"- **Нарушение норм:** {risk.law_reference}")
                lines.append(f"- **Рекомендация:** **{risk.recommendation}**\n")

        lines.extend([
            "---",
            "## 3. МЕДИЦИНСКИЙ И РЕГУЛЯТОРНЫЙ КОМПЛАЕНС",
            f"- **Регистрационное удостоверение (РУ):** {'Требуется' if report.med_compliance.ru_required else 'Не требуется'}",
            f"  *Детали:* {report.med_compliance.ru_notes}",
            f"- **Национальный режим (ПП РФ № 878 / ст. 14):** {'Применяется' if report.med_compliance.national_regime_applies else 'Не применяется'}",
            f"  *Детали:* {report.med_compliance.national_regime_details}",
            f"- **Каталог товаров, работ, услуг (КТРУ):** {'Использован' if report.med_compliance.ktru_used else 'Не использован'}" + (f" (Код: {report.med_compliance.ktru_code})" if report.med_compliance.ktru_code else ""),
            f"- **Монтаж, пусконаладка и обучение персонала:** {'Требуется' if report.med_compliance.installation_and_training else 'Не требуется'}",
            f"- **Гарантийный срок:** {f'{report.med_compliance.warranty_period_months} мес.' if report.med_compliance.warranty_period_months else 'Не указан'}",
            "",
            "---",
            "## 4. СПЕЦИФИКАЦИЯ ОБОРУДОВАНИЯ И АНАЛИЗ ЗАТОЧЕК",
        ])

        if report.equipment:
            for eq in report.equipment:
                ktru_str = f" [КТРУ: {eq.ktru_code}]" if eq.ktru_code else ""
                lines.append(f"### {eq.name} (Кол-во: {eq.quantity or '1 шт.'}){ktru_str}")
                if eq.potential_bias_warning:
                    lines.append(f"> ⚠️ **ИНДИКАТОР ЗАТОЧКИ:** {eq.potential_bias_warning}")
                if eq.detected_brand_bias:
                    lines.append(f"> 🔬 **ДЕТАЛЬНЫЙ РАЗБОР ЗАТОЧКИ:** {eq.detected_brand_bias}")
                if eq.suggested_neutral_specs:
                    lines.append(f"> 💡 **КАК ОСПАРИВАТЬ (РЕКОМЕНДАЦИЯ):** {eq.suggested_neutral_specs}")
                lines.append("**Ключевые технические требования ТЗ:**")
                for s in eq.key_specs:
                    lines.append(f"- {s}")
                lines.append("")
        else:
            lines.append("Спецификация оборудования не выделена.")

        if report.clarification_requests:
            lines.extend([
                "---",
                "## 5. ОФИЦИАЛЬНЫЕ ЗАПРОСЫ РАЗЪЯСНЕНИЙ ЗАКАЗЧИКУ В ЕИС",
            ])
            for idx, cr in enumerate(report.clarification_requests, 1):
                lines.extend([
                    f"### Запрос № {idx}: {cr.subject}",
                    f"**Правовое обоснование:** {cr.justification}",
                    "```text",
                    cr.draft_text,
                    "```",
                    "",
                ])

        lines.extend([
            "---",
            "*Сформировано в системе TenderAI Med. Документ носит рекомендательный характер.*"
        ])

        return "\n".join(lines)
