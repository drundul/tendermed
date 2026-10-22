import io
from typing import List, Optional
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

from app.models.schemas import (
    FullAnalysisReport,
    TrafficLightVerdict,
    RiskSeverity,
    ClarificationRequest,
    TenderSummary,
    FASComplaint,
)


def _set_cell_background(cell, fill_hex: str):
    """Устанавливает цвет заливки фона ячейки таблицы Word."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)


def _set_cell_margins(cell, top: int = 100, bottom: int = 100, left: int = 150, right: int = 150):
    """Устанавливает внутренние отступы ячейки."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


class ReportExporter:
    """Генерация профессиональных отчетов и юридических писем в форматах Markdown и DOCX."""

    # Цветовая палитра
    COLOR_PRIMARY = RGBColor(0x1F, 0x4E, 0x79)    # Темно-синий
    COLOR_DARK = RGBColor(0x26, 0x26, 0x26)       # Почти черный
    COLOR_MUTED = RGBColor(0x59, 0x59, 0x59)      # Серый
    COLOR_RED = RGBColor(0xCF, 0x13, 0x22)        # Красный
    COLOR_YELLOW = RGBColor(0xD4, 0x88, 0x06)     # Оранжево-желтый
    COLOR_GREEN = RGBColor(0x38, 0x9E, 0x0D)      # Зеленый

    # Hex для фонов таблиц
    HEX_PRIMARY = "1F4E79"
    HEX_LIGHT_BLUE = "F0F4F8"
    HEX_RED_LIGHT = "FFF1F0"
    HEX_RED_BORDER = "FFA39E"
    HEX_YELLOW_LIGHT = "FFFBE6"
    HEX_GREEN_LIGHT = "F6FFED"
    HEX_BORDER = "D9D9D9"

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

    @classmethod
    def to_docx_report(cls, report: FullAnalysisReport) -> bytes:
        """
        Формирует полный экспертный отчёт по закупке в формате Microsoft Word (.docx).
        Включает светофор, матрицу рисков, медицинский комплаенс, спецификацию и запросы.
        """
        doc = Document()

        # Настройка полей документа
        for section in doc.sections:
            section.top_margin = Inches(0.7)
            section.bottom_margin = Inches(0.7)
            section.left_margin = Inches(0.8)
            section.right_margin = Inches(0.8)

        # 1. Заголовок отчета
        title_p = doc.add_paragraph()
        title_run = title_p.add_run("ЭКСПЕРТНОЕ ЗАКЛЮЧЕНИЕ ТЕНДЕРНОГО АУДИТА")
        title_run.font.name = "Arial"
        title_run.font.size = Pt(16)
        title_run.font.bold = True
        title_run.font.color.rgb = cls.COLOR_PRIMARY
        title_p.paragraph_format.space_after = Pt(4)

        sub_p = doc.add_paragraph()
        sub_run = sub_p.add_run(f"Объект закупки: {report.summary.purchase_subject}")
        sub_run.font.name = "Arial"
        sub_run.font.size = Pt(11)
        sub_run.font.bold = True
        sub_run.font.color.rgb = cls.COLOR_DARK
        sub_p.paragraph_format.space_after = Pt(12)

        # 2. Баннер вердикта (Таблица-коллблок со светофором)
        verdict_table = doc.add_table(rows=1, cols=1)
        verdict_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        v_cell = verdict_table.cell(0, 0)
        _set_cell_margins(v_cell, top=140, bottom=140, left=180, right=180)

        if report.verdict == TrafficLightVerdict.RED:
            _set_cell_background(v_cell, cls.HEX_RED_LIGHT)
            v_title = "🔴 СТОП-ФАКТОРЫ: ВЫСОКИЙ РИСК ПОТЕРИ ДЕНЕГ ИЛИ ВКЛЮЧЕНИЯ В РНП"
            v_color = cls.COLOR_RED
        elif report.verdict == TrafficLightVerdict.YELLOW:
            _set_cell_background(v_cell, cls.HEX_YELLOW_LIGHT)
            v_title = "🟡 ВНИМАНИЕ: ТРЕБУЕТСЯ ЗАПРОС РАЗЪЯСНЕНИЙ ИЛИ ОСТОРОЖНОСТЬ"
            v_color = cls.COLOR_YELLOW
        else:
            _set_cell_background(v_cell, cls.HEX_GREEN_LIGHT)
            v_title = "🟢 РЕКОМЕНДОВАНО К УЧАСТИЮ (РИСКИ В ПРЕДЕЛАХ НОРМЫ)"
            v_color = cls.COLOR_GREEN

        vp1 = v_cell.paragraphs[0]
        vr1 = vp1.add_run(v_title)
        vr1.font.name = "Arial"
        vr1.font.size = Pt(12)
        vr1.font.bold = True
        vr1.font.color.rgb = v_color
        vp1.paragraph_format.space_after = Pt(4)

        vp2 = v_cell.add_paragraph()
        vr2 = vp2.add_run(f"Индекс риска: {report.risk_score} / 100\n")
        vr2.font.bold = True
        vr2.font.size = Pt(10.5)
        vr3 = vp2.add_run(f"Резюме для руководителя: {report.verdict_summary}")
        vr3.font.size = Pt(10)
        vr3.font.color.rgb = cls.COLOR_DARK
        vp2.paragraph_format.space_after = Pt(0)

        doc.add_paragraph().paragraph_format.space_after = Pt(8)

        # 3. Таблица реквизитов и ключевых параметров
        h1 = doc.add_paragraph()
        r_h1 = h1.add_run("1. Ключевые параметры закупки и реквизиты Заказчика")
        r_h1.font.name = "Arial"
        r_h1.font.size = Pt(12)
        r_h1.font.bold = True
        r_h1.font.color.rgb = cls.COLOR_PRIMARY
        h1.paragraph_format.space_after = Pt(6)

        param_table = doc.add_table(rows=7, cols=2)
        param_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        param_data = [
            ("Заказчик / Учреждение", f"{report.summary.customer_name or 'Не указан'}" + (f" (в лице: {report.summary.customer_signer})" if report.summary.customer_signer else "")),
            ("ИНН / КПП Заказчика", f"{report.summary.customer_inn or 'Не указан'} / {report.summary.customer_kpp or 'Н/Д'}"),
            ("Номер извещения в ЕИС / ЭТП", f"{report.summary.notice_number or 'По документации'} / {report.summary.etp_name or 'ЕЭТП / Сбербанк-АСТ'}"),
            ("НМЦК закупки", f"{report.summary.nmck_rubles:,.2f} ₽".replace(",", " ") if report.summary.nmck_rubles else "Не указана"),
            ("Срок поставки товара", report.summary.delivery_deadline or "По заявкам Заказчика"),
            ("Авансирование / Обеспечение контракта", f"{report.summary.advance_percent or 0}% аванс / {report.summary.contract_guarantee_percent or 0}% обеспечение"),
            ("Срок оплаты товара", f"{report.summary.payment_terms_days or 7} рабочих дней"),
        ]

        for i, (k, v) in enumerate(param_data):
            c1, c2 = param_table.cell(i, 0), param_table.cell(i, 1)
            _set_cell_margins(c1, top=60, bottom=60, left=100, right=100)
            _set_cell_margins(c2, top=60, bottom=60, left=100, right=100)
            _set_cell_background(c1, cls.HEX_LIGHT_BLUE)
            
            p1 = c1.paragraphs[0]
            r1 = p1.add_run(k)
            r1.font.name = "Arial"
            r1.font.size = Pt(9.5)
            r1.font.bold = True

            p2 = c2.paragraphs[0]
            r2 = p2.add_run(str(v))
            r2.font.name = "Arial"
            r2.font.size = Pt(9.5)

        doc.add_paragraph().paragraph_format.space_after = Pt(8)

        # 4. Матрица выявленных рисков
        h2 = doc.add_paragraph()
        r_h2 = h2.add_run(f"2. Выявленные риски и несоответствия ({len(report.risks)})")
        r_h2.font.name = "Arial"
        r_h2.font.size = Pt(12)
        r_h2.font.bold = True
        r_h2.font.color.rgb = cls.COLOR_PRIMARY
        h2.paragraph_format.space_after = Pt(6)

        if not report.risks:
            p_norisk = doc.add_paragraph("Критических правовых и финансовых рисков не обнаружено.")
            p_norisk.paragraph_format.space_after = Pt(6)
        else:
            for idx, risk in enumerate(report.risks, 1):
                rt = doc.add_table(rows=1, cols=1)
                rcell = rt.cell(0, 0)
                _set_cell_margins(rcell, top=100, bottom=100, left=140, right=140)

                sev_label = "🔴 ВЫСОКИЙ РИСК" if risk.severity == RiskSeverity.HIGH else "🟡 ВНИМАНИЕ"
                sev_bg = cls.HEX_RED_LIGHT if risk.severity == RiskSeverity.HIGH else cls.HEX_YELLOW_LIGHT
                _set_cell_background(rcell, sev_bg)

                rp = rcell.paragraphs[0]
                run_title = rp.add_run(f"{idx}. {risk.title} [{sev_label} • {risk.category.value}]\n")
                run_title.font.name = "Arial"
                run_title.font.size = Pt(10.5)
                run_title.font.bold = True
                
                run_desc = rp.add_run(f"{risk.description}\n")
                run_desc.font.size = Pt(9.5)

                if risk.quote:
                    run_q = rp.add_run(f"Цитата: «{risk.quote}»\n")
                    run_q.font.italic = True
                    run_q.font.size = Pt(9)
                    run_q.font.color.rgb = cls.COLOR_MUTED

                if risk.law_reference:
                    run_l = rp.add_run(f"Нарушение норм: {risk.law_reference}\n")
                    run_l.font.size = Pt(9)
                    run_l.font.bold = True

                run_rec = rp.add_run(f"Рекомендация: {risk.recommendation}")
                run_rec.font.size = Pt(9.5)
                run_rec.font.bold = True

                doc.add_paragraph().paragraph_format.space_after = Pt(4)

        # 5. Медицинский комплаенс
        h3 = doc.add_paragraph()
        r_h3 = h3.add_run("3. Медицинский и регуляторный комплаенс")
        r_h3.font.name = "Arial"
        r_h3.font.size = Pt(12)
        r_h3.font.bold = True
        r_h3.font.color.rgb = cls.COLOR_PRIMARY
        h3.paragraph_format.space_after = Pt(6)

        med_table = doc.add_table(rows=5, cols=2)
        med_data = [
            ("Регистрационное удостоверение (РУ)", f"{'Требуется' if report.med_compliance.ru_required else 'Не затребовано'} — {report.med_compliance.ru_notes}"),
            ("Национальный режим (ПП РФ № 878)", f"{'Применяется (ограничение допуска)' if report.med_compliance.national_regime_applies else 'Не применяется'} — {report.med_compliance.national_regime_details}"),
            ("Позиция КТРУ", f"{'Использована' if report.med_compliance.ktru_used else 'Свободная форма заказчика'} (Код: {report.med_compliance.ktru_code or 'Н/Д'})"),
            ("Монтаж, пусконаладка, инструктаж", "Включены в обязанности поставщика" if report.med_compliance.installation_and_training else "Не затребованы"),
            ("Гарантийный срок", f"{report.med_compliance.warranty_period_months or 'Не указан'} месяцев"),
        ]
        for i, (k, v) in enumerate(med_data):
            c1, c2 = med_table.cell(i, 0), med_table.cell(i, 1)
            _set_cell_margins(c1, top=60, bottom=60, left=100, right=100)
            _set_cell_margins(c2, top=60, bottom=60, left=100, right=100)
            _set_cell_background(c1, cls.HEX_LIGHT_BLUE)
            p1, p2 = c1.paragraphs[0], c2.paragraphs[0]
            r1 = p1.add_run(k)
            r1.font.bold = True
            r1.font.size = Pt(9.5)
            r2 = p2.add_run(v)
            r2.font.size = Pt(9.5)

        doc.add_paragraph().paragraph_format.space_after = Pt(8)

        # 6. Спецификация оборудования и заточки
        h4 = doc.add_paragraph()
        r_h4 = h4.add_run(f"4. Спецификация оборудования и анализ заточек ({len(report.equipment)})")
        r_h4.font.name = "Arial"
        r_h4.font.size = Pt(12)
        r_h4.font.bold = True
        r_h4.font.color.rgb = cls.COLOR_PRIMARY
        h4.paragraph_format.space_after = Pt(6)

        for eq in report.equipment:
            ep = doc.add_paragraph()
            ktru_part = f" [КТРУ: {eq.ktru_code}]" if eq.ktru_code else ""
            e_title = ep.add_run(f"• {eq.name} — {eq.quantity or '1 шт.'}{ktru_part}\n")
            e_title.font.bold = True
            e_title.font.size = Pt(10.5)

            if eq.detected_brand_bias:
                e_bias = ep.add_run(f"  🔬 Анализ заточки: {eq.detected_brand_bias}\n")
                e_bias.font.color.rgb = cls.COLOR_RED
                e_bias.font.size = Pt(9.5)

            if eq.suggested_neutral_specs:
                e_rec = ep.add_run(f"  💡 Как оспаривать: {eq.suggested_neutral_specs}\n")
                e_rec.font.color.rgb = cls.COLOR_PRIMARY
                e_rec.font.size = Pt(9.5)

            if eq.key_specs:
                e_sp = ep.add_run("  Ключевые требования: " + "; ".join(eq.key_specs[:4]) + "\n")
                e_sp.font.size = Pt(9)
                e_sp.font.color.rgb = cls.COLOR_MUTED

        # Подвал отчета
        doc.add_paragraph().paragraph_format.space_after = Pt(12)
        footer_p = doc.add_paragraph()
        f_run = footer_p.add_run("Отчёт сформирован программным комплексом TenderAI Med. Документ носит аналитический характер.")
        f_run.font.italic = True
        f_run.font.size = Pt(8.5)
        f_run.font.color.rgb = cls.COLOR_MUTED

        bio = io.BytesIO()
        doc.save(bio)
        return bio.getvalue()

    @classmethod
    def to_docx_clarification_request(
        cls,
        cr: ClarificationRequest,
        summary: TenderSummary,
        request_number: int = 1,
    ) -> bytes:
        """
        Формирует официальное юридическое письмо-запрос на разъяснение в формате Word (.docx).
        Оформлено по правилам делопроизводства и претензионной практики 44-ФЗ / 223-ФЗ.
        """
        doc = Document()

        for section in doc.sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(0.9)
            section.right_margin = Inches(0.9)

        # 1. Шапка письма (Справа)
        header_table = doc.add_table(rows=1, cols=2)
        header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        left_cell, right_cell = header_table.cell(0, 0), header_table.cell(0, 1)

        # Левая часть — Исходящий номер участника
        lp = left_cell.paragraphs[0]
        lr = lp.add_run(
            "Исх. № __________\n"
            "от «___» ____________ 202_ г."
        )
        lr.font.name = "Arial"
        lr.font.size = Pt(9.5)
        lr.font.color.rgb = cls.COLOR_MUTED

        # Правая часть — Кому адресовано
        rp = right_cell.paragraphs[0]
        rp.alignment = WD_ALIGN_PARAGRAPH.RIGHT

        recipient_text = cr.recipient_header.strip() if cr.recipient_header else (
            f"Заказчику: {summary.customer_name or 'Заказчику закупки'}\n"
            f"В лице: {summary.customer_signer or 'Руководителя'}\n"
            f"Адрес: {summary.customer_address or summary.delivery_place or 'По месту нахождения'}\n"
            f"ИНН: {summary.customer_inn or 'Н/Д'} / КПП: {summary.customer_kpp or 'Н/Д'}\n"
            f"ЭТП: {summary.etp_name or 'Оператору электронной площадки'}"
        )
        rr = rp.add_run(recipient_text)
        rr.font.name = "Arial"
        rr.font.size = Pt(9.5)
        rr.font.bold = True

        doc.add_paragraph().paragraph_format.space_after = Pt(18)

        # 2. Заголовок документа (По центру, полужирный)
        tp = doc.add_paragraph()
        tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        tr1 = tp.add_run("ЗАПРОС О ДАЧЕ РАЗЪЯСНЕНИЙ\n")
        tr1.font.name = "Arial"
        tr1.font.size = Pt(13)
        tr1.font.bold = True
        tr1.font.color.rgb = cls.COLOR_PRIMARY

        tr2 = tp.add_run(
            f"положений извещения и документации об осуществлении закупки № {summary.notice_number or '___________'}\n"
            f"(предмет закупки: «{summary.purchase_subject}»)"
        )
        tr2.font.name = "Arial"
        tr2.font.size = Pt(10.5)
        tr2.font.bold = True
        tp.paragraph_format.space_after = Pt(14)

        # 3. Тема и основание
        sub_p = doc.add_paragraph()
        sr1 = sub_p.add_run(f"Тема запроса: {cr.subject}\n")
        sr1.font.bold = True
        sr1.font.size = Pt(10.5)
        sr2 = sub_p.add_run(f"Правовое основание: {cr.justification}")
        sr2.font.bold = True
        sr2.font.size = Pt(9.5)
        sr2.font.color.rgb = cls.COLOR_PRIMARY
        sub_p.paragraph_format.space_after = Pt(14)

        # 4. Основной текст запроса (абзацы)
        body_lines = cr.draft_text.split("\n")
        for line in body_lines:
            stripped = line.strip()
            if not stripped:
                continue
            bp = doc.add_paragraph()
            bp.paragraph_format.first_line_indent = Inches(0.4)
            bp.paragraph_format.line_spacing = 1.15
            bp.paragraph_format.space_after = Pt(4)
            br = bp.add_run(stripped)
            br.font.name = "Arial"
            br.font.size = Pt(11)

        doc.add_paragraph().paragraph_format.space_after = Pt(24)

        # 5. Блок подписи
        sig_p = doc.add_paragraph()
        sig_p.paragraph_format.line_spacing = 1.3
        sig_r = sig_p.add_run(
            "С уважением,\n\n"
            "Уполномоченный представитель участника закупки: _________________ / _________________ /\n\n"
            "М.П."
        )
        sig_r.font.name = "Arial"
        sig_r.font.size = Pt(10.5)
        sig_r.font.bold = True

        bio = io.BytesIO()
        doc.save(bio)
        return bio.getvalue()

    @classmethod
    def to_docx_all_clarifications(
        cls,
        requests: List[ClarificationRequest],
        summary: TenderSummary,
    ) -> bytes:
        """
        Формирует единый Word-документ со всеми официальными запросами разъяснений,
        разделёнными разрывами страниц.
        """
        if not requests:
            doc = Document()
            doc.add_paragraph("Запросы на разъяснение отсутствуют.")
            bio = io.BytesIO()
            doc.save(bio)
            return bio.getvalue()

        # Если один запрос — просто вызываем генератор для одного
        if len(requests) == 1:
            return cls.to_docx_clarification_request(requests[0], summary, 1)

        doc = Document()
        for section in doc.sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(0.9)
            section.right_margin = Inches(0.9)

        for idx, cr in enumerate(requests, 1):
            if idx > 1:
                doc.add_page_break()

            # Шапка письма (Справа)
            header_table = doc.add_table(rows=1, cols=2)
            header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
            left_cell, right_cell = header_table.cell(0, 0), header_table.cell(0, 1)

            lp = left_cell.paragraphs[0]
            lr = lp.add_run(f"Исх. № {idx} / ЗР\nот «___» ____________ 202_ г.")
            lr.font.name = "Arial"
            lr.font.size = Pt(9.5)
            lr.font.color.rgb = cls.COLOR_MUTED

            rp = right_cell.paragraphs[0]
            rp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            recipient_text = cr.recipient_header.strip() if cr.recipient_header else (
                f"Заказчику: {summary.customer_name or 'Заказчику закупки'}\n"
                f"В лице: {summary.customer_signer or 'Руководителя'}\n"
                f"Адрес: {summary.customer_address or summary.delivery_place or 'По месту нахождения'}\n"
                f"ИНН: {summary.customer_inn or 'Н/Д'} / КПП: {summary.customer_kpp or 'Н/Д'}\n"
                f"ЭТП: {summary.etp_name or 'Оператору электронной площадки'}"
            )
            rr = rp.add_run(recipient_text)
            rr.font.name = "Arial"
            rr.font.size = Pt(9.5)
            rr.font.bold = True

            doc.add_paragraph().paragraph_format.space_after = Pt(14)

            tp = doc.add_paragraph()
            tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
            tr1 = tp.add_run(f"ЗАПРОС № {idx} О ДАЧЕ РАЗЪЯСНЕНИЙ\n")
            tr1.font.name = "Arial"
            tr1.font.size = Pt(13)
            tr1.font.bold = True
            tr1.font.color.rgb = cls.COLOR_PRIMARY

            tr2 = tp.add_run(
                f"положений извещения и документации об осуществлении закупки № {summary.notice_number or '___________'}\n"
                f"(предмет закупки: «{summary.purchase_subject}»)"
            )
            tr2.font.name = "Arial"
            tr2.font.size = Pt(10)
            tr2.font.bold = True
            tp.paragraph_format.space_after = Pt(12)

            sub_p = doc.add_paragraph()
            sr1 = sub_p.add_run(f"Тема запроса: {cr.subject}\n")
            sr1.font.bold = True
            sr1.font.size = Pt(10.5)
            sr2 = sub_p.add_run(f"Правовое основание: {cr.justification}")
            sr2.font.bold = True
            sr2.font.size = Pt(9.5)
            sr2.font.color.rgb = cls.COLOR_PRIMARY
            sub_p.paragraph_format.space_after = Pt(12)

            for line in cr.draft_text.split("\n"):
                stripped = line.strip()
                if not stripped:
                    continue
                bp = doc.add_paragraph()
                bp.paragraph_format.first_line_indent = Inches(0.4)
                bp.paragraph_format.line_spacing = 1.15
                bp.paragraph_format.space_after = Pt(4)
                br = bp.add_run(stripped)
                br.font.name = "Arial"
                br.font.size = Pt(11)

            doc.add_paragraph().paragraph_format.space_after = Pt(18)

            sig_p = doc.add_paragraph()
            sig_p.paragraph_format.line_spacing = 1.3
            sig_r = sig_p.add_run(
                "С уважением,\n\n"
                "Уполномоченный представитель участника закупки: _________________ / _________________ /\n\n"
                "М.П."
            )
            sig_r.font.name = "Arial"
            sig_r.font.size = Pt(10)
            sig_r.font.bold = True

        bio = io.BytesIO()
        doc.save(bio)
        return bio.getvalue()

    @classmethod
    def export_fas_complaint_docx(cls, complaint: FASComplaint) -> bytes:
        """Генерирует официальную жалобу в ФАС России в формате Microsoft Word (.docx)."""
        doc = Document()

        # Поля страницы: стандартные делопроизводственные (2 см)
        for section in doc.sections:
            section.top_margin = Inches(0.8)
            section.bottom_margin = Inches(0.8)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(0.6)

        # 1. Шапка адресата и сторон (таблица 2 колонки, реквизиты справа)
        header_table = doc.add_table(rows=1, cols=2)
        header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        left_cell = header_table.cell(0, 0)
        right_cell = header_table.cell(0, 1)
        left_cell.width = Inches(2.3)
        right_cell.width = Inches(4.7)

        def add_header_line(label: str, val: str, bold_label: bool = True):
            p = right_cell.add_paragraph()
            p.paragraph_format.line_spacing = 1.1
            p.paragraph_format.space_after = Pt(2)
            r1 = p.add_run(f"{label}: ")
            r1.font.name = "Times New Roman"
            r1.font.size = Pt(9.5)
            r1.font.bold = bold_label
            r2 = p.add_run(val)
            r2.font.name = "Times New Roman"
            r2.font.size = Pt(9.5)

        # В УФАС
        p_to = right_cell.paragraphs[0]
        p_to.paragraph_format.line_spacing = 1.15
        p_to.paragraph_format.space_after = Pt(3)
        r_to = p_to.add_run(f"В {complaint.fas_authority_name}\n")
        r_to.font.name = "Times New Roman"
        r_to.font.size = Pt(10)
        r_to.font.bold = True
        if complaint.fas_address:
            r_addr = p_to.add_run(f"Адрес: {complaint.fas_address}\n")
            r_addr.font.name = "Times New Roman"
            r_addr.font.size = Pt(9)
            r_addr.font.italic = True

        add_header_line("Заявитель", f"{complaint.applicant_name} (ИНН: {complaint.applicant_inn or 'указывается Заявителем'})\nКонтакты: {complaint.applicant_contacts or 'info@supplier.ru'}")
        add_header_line("Заказчик", f"{complaint.customer_name}\nИНН/КПП: {complaint.customer_inn} / {complaint.customer_kpp}\nАдрес: {complaint.customer_address or 'По данным ЕИС'}")
        add_header_line("Оператор ЭТП", complaint.etp_name or "ЭТП")
        add_header_line("Извещение №", f"{complaint.notice_number} в ЕИС (zakupki.gov.ru)")
        add_header_line("НМЦК", complaint.nmck_formatted)

        doc.add_paragraph().paragraph_format.space_after = Pt(8)

        # 2. Заголовок документа
        title_p = doc.add_paragraph()
        title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        title_p.paragraph_format.space_after = Pt(4)
        title_p.paragraph_format.space_before = Pt(8)
        r_title = title_p.add_run("ЖАЛОБА")
        r_title.font.name = "Times New Roman"
        r_title.font.size = Pt(14)
        r_title.font.bold = True

        sub_p = doc.add_paragraph()
        sub_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        sub_p.paragraph_format.space_after = Pt(14)
        r_sub = sub_p.add_run(
            f"на положения извещения и документации об осуществлении закупки № {complaint.notice_number}\n"
            f"(в порядке статей 105, 106 Федерального закона от 05.04.2013 № 44-ФЗ)"
        )
        r_sub.font.name = "Times New Roman"
        r_sub.font.size = Pt(11)
        r_sub.font.bold = True

        # 3. Вводная часть
        intro_p = doc.add_paragraph()
        intro_p.paragraph_format.line_spacing = 1.15
        intro_p.paragraph_format.first_line_indent = Inches(0.4)
        intro_p.paragraph_format.space_after = Pt(8)
        intro_r = intro_p.add_run(
            f"В единой информационной системе в сфере закупок (zakupki.gov.ru) Заказчиком — {complaint.customer_name} — "
            f"было размещено извещение № {complaint.notice_number} о проведении электронного аукциона на «{complaint.purchase_subject}» "
            f"с начальной (максимальной) ценой контракта {complaint.nmck_formatted} на электронной торговой площадке {complaint.etp_name}.\n"
            f"Заявитель ({complaint.applicant_name}) имеет намерение принять участие в указанной закупке. "
            f"Однако при анализе положений извещения, описания объекта закупки (ТЗ) и проекта контракта "
            f"были выявлены существенные нарушения требований Федерального закона № 44-ФЗ и Федерального закона № 135-ФЗ «О защите конкуренции», "
            f"ограничивающие круг участников закупки и делающие подачу заявки невозможной."
        )
        intro_r.font.name = "Times New Roman"
        intro_r.font.size = Pt(11)

        # 4. Эпизоды нарушений
        for ep in complaint.episodes:
            ep_header_p = doc.add_paragraph()
            ep_header_p.paragraph_format.space_before = Pt(10)
            ep_header_p.paragraph_format.space_after = Pt(3)
            ep_hr = ep_header_p.add_run(f"Эпизод {ep.number}. {ep.title}")
            ep_hr.font.name = "Times New Roman"
            ep_hr.font.size = Pt(11.5)
            ep_hr.font.bold = True

            # Норма права
            norm_p = doc.add_paragraph()
            norm_p.paragraph_format.space_after = Pt(4)
            norm_r = norm_p.add_run(f"Нарушенные нормы: {ep.violated_norms}")
            norm_r.font.name = "Times New Roman"
            norm_r.font.size = Pt(10)
            norm_r.font.bold = True
            norm_r.font.color.rgb = cls.COLOR_PRIMARY

            # Обстоятельства
            circ_p = doc.add_paragraph()
            circ_p.paragraph_format.line_spacing = 1.15
            circ_p.paragraph_format.first_line_indent = Inches(0.4)
            circ_p.paragraph_format.space_after = Pt(4)
            circ_r = circ_p.add_run(ep.circumstances)
            circ_r.font.name = "Times New Roman"
            circ_r.font.size = Pt(10.5)

            # Правовое обоснование
            arg_p = doc.add_paragraph()
            arg_p.paragraph_format.line_spacing = 1.15
            arg_p.paragraph_format.first_line_indent = Inches(0.4)
            arg_p.paragraph_format.space_after = Pt(8)
            arg_r = arg_p.add_run(ep.legal_argumentation)
            arg_r.font.name = "Times New Roman"
            arg_r.font.size = Pt(10.5)

        # 5. Просительная часть (ПРОШУ)
        proshu_title_p = doc.add_paragraph()
        proshu_title_p.paragraph_format.space_before = Pt(12)
        proshu_title_p.paragraph_format.space_after = Pt(6)
        proshu_title_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        pr_tr = proshu_title_p.add_run("На основании вышеизложенного, руководствуясь ст. 99, 105, 106 Федерального закона № 44-ФЗ, ст. 17 Федерального закона № 135-ФЗ,\n\nПРОШУ:")
        pr_tr.font.name = "Times New Roman"
        pr_tr.font.size = Pt(12)
        pr_tr.font.bold = True

        for i, item in enumerate(complaint.petitum, 1):
            item_p = doc.add_paragraph()
            item_p.paragraph_format.line_spacing = 1.15
            item_p.paragraph_format.first_line_indent = Inches(0.4)
            item_p.paragraph_format.space_after = Pt(3)
            ir = item_p.add_run(f"{i}. {item}")
            ir.font.name = "Times New Roman"
            ir.font.size = Pt(10.5)

        # 6. Приложения
        if complaint.attachments:
            att_title_p = doc.add_paragraph()
            att_title_p.paragraph_format.space_before = Pt(10)
            att_title_p.paragraph_format.space_after = Pt(3)
            atr = att_title_p.add_run("Приложения:")
            atr.font.name = "Times New Roman"
            atr.font.size = Pt(10.5)
            atr.font.bold = True

            for att in complaint.attachments:
                att_p = doc.add_paragraph()
                att_p.paragraph_format.first_line_indent = Inches(0.4)
                att_p.paragraph_format.space_after = Pt(2)
                ar = att_p.add_run(att)
                ar.font.name = "Times New Roman"
                ar.font.size = Pt(10)

        # 7. Подпись и дата
        doc.add_paragraph().paragraph_format.space_after = Pt(16)
        sig_p = doc.add_paragraph()
        sig_p.paragraph_format.line_spacing = 1.3
        sig_r = sig_p.add_run(
            f"«____» _______________ 2026 г.\n\n"
            f"Руководитель / Уполномоченный представитель {complaint.applicant_name}:\n\n"
            f"_______________________ / _______________________ /\n\n"
            f"М.П. (при наличии)"
        )
        sig_r.font.name = "Times New Roman"
        sig_r.font.size = Pt(10.5)

        bio = io.BytesIO()
        doc.save(bio)
        return bio.getvalue()
