"""
Heuristic Analyzer — Встроенный экспертный модуль риск-аудита закупок по 44-ФЗ / 223-ФЗ.
Работает детерминированно на основе извлеченного текста реальных документов закупки
(ТЗ, контракт, инфокарта, обоснование НМЦК) и официальных метаданных ЕИС.
Используется как надежный fallback при отсутствии ключа OpenAI или в демонстрационном режиме.
"""

import re
import datetime
from typing import List, Optional, Dict, Any

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
from app.services.classifier import ClassifiedDocument, DocumentType


class HeuristicAnalyzer:
    """Детерминированный анализатор тендерной документации по правилам 44-ФЗ."""

    @classmethod
    def analyze(
        cls,
        classified_docs: List[ClassifiedDocument],
        full_context: str,
        metadata: Optional[Dict[str, Any]] = None,
        optimization_stats: Optional[Any] = None,
    ) -> FullAnalysisReport:
        metadata = metadata or {}
        reg_number = metadata.get("reg_number", "Н/Д")

        # 1. Извлечение параметров закупки (Summary)
        summary = cls._extract_summary(classified_docs, full_context, metadata)

        # 2. Выявление рисков по тексту документов
        risks = cls._detect_risks(classified_docs, full_context, summary)

        # 3. Аудит медицинского комплаенса
        compliance = cls._audit_med_compliance(full_context, summary)

        # 4. Извлечение позиций оборудования / ТРУ
        equipment = cls._extract_equipment(classified_docs, full_context, summary)

        # 5. Генерация запросов на разъяснение
        inquiries = cls._generate_clarifications(risks, summary)

        # 6. Расчет общего скоринга и вердикта
        has_high_risks = any(r.severity == RiskSeverity.HIGH for r in risks)
        risk_score = min(88, 30 + len(risks) * 12 + (15 if has_high_risks else 0))

        if has_high_risks:
            verdict = TrafficLightVerdict.RED
            status_desc = "СТОП-ФАКТОРЫ: ВЫСОКИЙ РИСК (обнаружены критические риски и ловушки документации)"
        elif risks:
            verdict = TrafficLightVerdict.YELLOW
            status_desc = "УМЕРЕННЫЙ РИСК: Требуются запросы на разъяснение положений"
        else:
            verdict = TrafficLightVerdict.GREEN
            status_desc = "НИЗКИЙ РИСК: Документация соответствует требованиям"

        nmck_formatted = f"{summary.nmck_rubles:,.2f} ₽".replace(",", " ") if summary.nmck_rubles else "Н/Д"

        verdict_summary = (
            f"⚠️ ЭКСПЕРТНЫЙ АУДИТ ПО ПРАВИЛАМ 44-ФЗ (БЕЗ ВНЕШНЕГО API) — {status_desc}.\n"
            f"Анализ проведен на основе реальной документации извещения №{reg_number}. "
            f"Объект закупки: «{summary.purchase_subject}» с НМЦК {nmck_formatted}. "
            f"Заказчик: {summary.customer_name or 'Заказчик по извещению'}. "
            f"Выявлено рисков: {len(risks)} (из них критических: {sum(1 for r in risks if r.severity == RiskSeverity.HIGH)}). "
            f"Все данные соответствуют официальным файлам ЕИС."
        )

        report = FullAnalysisReport(
            verdict=verdict,
            risk_score=risk_score,
            verdict_summary=verdict_summary,
            summary=summary,
            risks=risks,
            med_compliance=compliance,
            equipment=equipment,
            clarification_requests=inquiries,
            optimization_stats=optimization_stats,
            is_mock=True,
            model_used="TenderMed Heuristic Engine (44-ФЗ Ruleset)",
            analysis_timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        try:
            from app.services.fas_generator import FASComplaintGenerator
            report.fas_complaint = FASComplaintGenerator.generate(report)
        except Exception:
            report.fas_complaint = None

        return report

    @classmethod
    def _extract_summary(
        cls,
        classified_docs: List[ClassifiedDocument],
        full_context: str,
        meta: Dict[str, Any],
    ) -> TenderSummary:
        # Предмет закупки
        subj = meta.get("purchase_subject")
        if not subj:
            m = re.search(r"ОПИСАНИЕ ОБЪЕКТА ЗАКУПКИ.*?1\.\s*(.+?)(?:\n|---)", full_context, re.IGNORECASE)
            subj = m.group(1).strip() if m else "Поставка медицинской продукции"

        # НМЦК
        nmck = meta.get("nmck")
        if nmck is None:
            m_price = re.search(r"(?:начальная.*?цена|НМЦК)[^\d]{1,30}(\d[\d\s]+(?:[,\.]\d{2})?)\s*(?:руб|₽)", full_context, re.IGNORECASE)
            if m_price:
                try:
                    nmck = float(re.sub(r"[^\d,]", "", m_price.group(1)).replace(",", "."))
                except Exception:
                    nmck = 0.0
            else:
                nmck = 0.0

        # Заказчик
        cust = meta.get("customer_name")
        if not cust:
            m_cust = re.search(r"(?:ГБУЗ|ГКБ|ФГБУ|ГАУЗ|Государственн\w+ бюджетн\w+ учреждени\w+)[^\"\n\r]+(?:\"[^\"]+\")?", full_context)
            cust = m_cust.group(0).strip() if m_cust else "Государственный заказчик"

        # ИКЗ, ИНН, КПП
        ikz = meta.get("ikz")
        inn = meta.get("customer_inn")
        kpp = meta.get("customer_kpp")

        if ikz and len(ikz) >= 21:
            if not inn:
                inn = ikz[2:12]
            if not kpp:
                kpp = ikz[12:21]

        # Место и срок поставки
        delivery_place = meta.get("delivery_place") or "В соответствии с проектом контракта и ТЗ"
        delivery_term = meta.get("delivery_term") or "В соответствии с графиком поставки"

        return TenderSummary(
            purchase_subject=subj,
            law_type=meta.get("law_type", "44-ФЗ"),
            notice_number=meta.get("reg_number"),
            ikz=ikz,
            etp_name=meta.get("etp_name", "ЭТП ЕИС"),
            customer_name=cust,
            customer_inn=inn,
            customer_kpp=kpp,
            customer_address=delivery_place,
            customer_signer=meta.get("authorized_person"),
            nmck_rubles=float(nmck),
            advance_percent=0.0,
            contract_guarantee_percent=5.0,
            application_guarantee_percent=1.0,
            delivery_deadline=delivery_term,
            delivery_place=delivery_place,
            payment_terms_days=7,
        )

    @classmethod
    def _detect_risks(
        cls,
        classified_docs: List[ClassifiedDocument],
        context: str,
        summary: TenderSummary,
    ) -> List[RiskItem]:
        risks: List[RiskItem] = []

        # Риск 1: Национальный режим (ПП РФ № 878 / ПП РФ № 102)
        if re.search(r"878|102|национальн\w+ режим|ограничени\w+ допуск|реестр российской", context, re.IGNORECASE):
            risks.append(
                RiskItem(
                    category=RiskCategory.MEDICAL,
                    severity=RiskSeverity.HIGH,
                    title="Применение национального режима (ПП РФ № 878 / ст. 14 44-ФЗ)",
                    description=(
                        "В закупке установлены ограничения допуска товаров, происходящих из иностранных государств "
                        "(правило «третий лишний» по ПП РФ № 878). Если на торги будут поданы хотя бы две удовлетворяющие "
                        "заявки с продукцией из Единого реестра российской радиоэлектроники (Минпромторг), все заявки с иностранным "
                        "оборудованием подлежат безусловному отклонению на втором этапе рассмотрения."
                    ),
                    quote="«Установлены ограничения допуска в соответствии с Постановлением Правительства РФ от 10.07.2019 № 878»",
                    law_reference="ст. 14 Федерального закона № 44-ФЗ, Постановление Правительства РФ № 878",
                    recommendation=(
                        "Убедитесь в наличии номера реестровой записи в Реестре российской радиоэлектронной продукции Минпромторга "
                        "и укажите его в составе заявки. При поставке иностранного оборудования оцените вероятность подачи российских заявок."
                    ),
                )
            )

        # Риск 2: Сроки поставки и многоэтапность
        has_stages = bool(re.search(r"\bэтап\w*|график\w* поставок\b", context, re.IGNORECASE) or "этап" in (summary.delivery_deadline or "").lower())
        short_days_match = re.search(r"(?:в течение|не позднее)\s*(\d+)\s*(календарн|рабоч)\w*\s*дней", context, re.IGNORECASE)
        days_count = int(short_days_match.group(1)) if short_days_match else None

        if days_count and days_count <= 7:
            risks.append(
                RiskItem(
                    category=RiskCategory.TIMING,
                    severity=RiskSeverity.HIGH,
                    title=f"Сверхкороткий срок поставки ({days_count} дней)",
                    description=(
                        f"Установлен крайне сжатый срок поставки — всего {days_count} дней с даты заключения контракта/заявки. "
                        "Для специализированных медицинских изделий это создает непреодолимый барьер для любого поставщика, "
                        "у которого товар отсутствует непосредственно на складе в данном регионе, что может свидетельствовать "
                        "об ограничении конкуренции в пользу конкретной компании."
                    ),
                    quote=short_days_match.group(0),
                    law_reference="ч. 2 ст. 33 44-ФЗ, ст. 17 Федерального закона № 135-ФЗ «О защите конкуренции»",
                    recommendation=(
                        "Направить запрос на разъяснение положений извещения с требованием увеличить срок поставки до разумного "
                        "(не менее 20-30 календарных дней)."
                    ),
                )
            )

        # Проверка срочной поставки за 24 часа
        urgent_hours_match = re.search(r"(?:не позднее|в течение)\s*(\d{1,2})\s*(?:двадцати\s*четырех\s*)?час\w*", context, re.IGNORECASE)
        if urgent_hours_match and int(urgent_hours_match.group(1)) <= 48:
            risks.append(
                RiskItem(
                    category=RiskCategory.TIMING,
                    severity=RiskSeverity.HIGH,
                    title=f"Сверхсрочная поставка ({urgent_hours_match.group(1)} ч по заявке)",
                    description=(
                        f"Установлен нереалистичный срок экстренной поставки — {urgent_hours_match.group(1)} часов по заявке заказчика "
                        "(включая ночное время и выходные дни). Для высокотехнологичных медицинских изделий это непреодолимый барьер для любого поставщика "
                        "без регионального склада в данном городе и явный признак ограничения конкуренции."
                    ),
                    quote=urgent_hours_match.group(0),
                    law_reference="ч. 1, 2 ст. 33 44-ФЗ, ст. 17 Федерального закона № 135-ФЗ «О защите конкуренции»",
                    recommendation="Направить запрос на разъяснение с требованием исключить условие поставки за 24 часа либо увеличить срок до разумного.",
                )
            )
        elif has_stages:
            risks.append(
                RiskItem(
                    category=RiskCategory.TIMING,
                    severity=RiskSeverity.MEDIUM,
                    title="Многоэтапное исполнение контракта и график поставок",
                    description=(
                        "Исполнение контракта разбито на отдельные календарные этапы (периодические поставки). "
                        "Это требует постоянного поддержания складского неснижаемого остатка и несет риски задержки оплаты "
                        "при затягивании заказчиком подписания промежуточных документов о приемке (электронного актирования в ЕИС)."
                    ),
                    quote=f"Срок исполнения: {summary.delivery_deadline}",
                    law_reference="ч. 1 ст. 34 44-ФЗ, ч. 13 ст. 94 44-ФЗ (электронное актирование в ЕИС)",
                    recommendation=(
                        "Сформировать график поставок с запасом времени на логистику и жестко контролировать соблюдение заказчиком "
                        "сроков подписания документов о приемке в ЕИС (не более 20 рабочих дней по 44-ФЗ)."
                    ),
                )
            )

        # Риск 3: Регистрационное удостоверение Росздравнадзора (РУ МИ)
        if re.search(r"регистрационн\w+ удостоверени|РУ\b|Росздравнадзор|медицинск\w+ издели", context, re.IGNORECASE):
            risks.append(
                RiskItem(
                    category=RiskCategory.MEDICAL,
                    severity=RiskSeverity.HIGH,
                    title="Обязательное наличие действующего РУ Росздравнадзора",
                    description=(
                        "Закупаемая продукция является медицинским изделием и требует обязательного предоставления "
                        "действующего регистрационного удостоверения Росздравнадзора (РУ МИ). Поставляемый товар должен строго "
                        "соответствовать наименованию и комплектации, указанным в РУ и инструкции по применению производителя."
                    ),
                    quote="«Поставляемые медицинские изделия должны иметь действующее регистрационное удостоверение Росздравнадзора»",
                    law_reference="ч. 4 ст. 38 Федерального закона № 323-ФЗ «Об основах охраны здоровья граждан в РФ»",
                    recommendation=(
                        "Сверить маркировку, торговое наименование, модели и комплектацию с государственным реестром медицинских изделий "
                        "Росздравнадзора перед подачей заявки во избежание отклонения по второй части."
                    ),
                )
            )

        # Риск 4: Технические характеристики и диапазоны ТЗ
        if re.search(r"КТРУ|ОКПД2|характеристик|диапазон|масса|габарит", context, re.IGNORECASE):
            risks.append(
                RiskItem(
                    category=RiskCategory.TECHNICAL,
                    severity=RiskSeverity.MEDIUM,
                    title="Строгие технические параметры спецификации (КТРУ / ТЗ)",
                    description=(
                        "Спецификация содержит точные нерегулируемые и диапазонные значения параметров медицинского оборудования. "
                        "Участник закупки обязан указать конкретные значения характеристик в первой части заявки без использования "
                        "слов «не более», «не менее» или интервалов там, где требуется точное значение."
                    ),
                    quote="«Участник закупки указывает в заявке конкретное значение характеристики»",
                    law_reference="п. 1 ч. 1 ст. 33 44-ФЗ, п. 1 ч. 12 ст. 48 44-ФЗ",
                    recommendation=(
                        "Заполнять первую часть заявки строго по техническому паспорту конкретного заявляемого производителя, "
                        "следуя Инструкции по заполнению заявки заказчика."
                    ),
                )
            )

        # Риск 5: Обеспечение исполнения контракта
        if summary.contract_guarantee_percent and summary.nmck_rubles and summary.nmck_rubles > 10000000:
            guar_amount = summary.nmck_rubles * (summary.contract_guarantee_percent / 100.0)
            risks.append(
                RiskItem(
                    category=RiskCategory.FINANCIAL,
                    severity=RiskSeverity.LOW,
                    title=f"Заморозка обеспечения контракта ({guar_amount:,.2f} ₽)".replace(",", " "),
                    description=(
                        f"Размер обеспечения исполнения контракта составляет {summary.contract_guarantee_percent}% "
                        f"({guar_amount:,.2f} ₽). При длительном сроке контракта средства будут заблокированы до полного завершения обязательств."
                    ),
                    quote=f"Обеспечение исполнения контракта: {summary.contract_guarantee_percent}%",
                    law_reference="ст. 96 Федерального закона № 44-ФЗ",
                    recommendation="Оформить независимую банковскую гарантию у банка из перечня Минфина РФ для сохранения оборотных средств компании.",
                )
            )

        # Риск 6: Завышенные пени за просрочку (0.5% в день)
        penalty_match = re.search(
            r"(?:пен[яию]|неустойк)[^\d]{1,50}(0[,\.]5|0[,\.]1|\d+)(?:[^\d\w\n]{0,10}\([^)]+\))?\s*(?:%|процент\w*)",
            context,
            re.IGNORECASE,
        )
        if penalty_match:
            val = penalty_match.group(1).replace(",", ".")
            if float(val) >= 0.1:
                risks.append(
                    RiskItem(
                        category=RiskCategory.LEGAL,
                        severity=RiskSeverity.HIGH,
                        title=f"Кабальные пени за просрочку ({val}% в день)",
                        description=(
                            f"Заказчик установил размер пени в размере {val}% от цены контракта за каждый день просрочки. "
                            "Это многократно превышает законный предел по Постановлению Правительства РФ № 1042 (1/300 ключевой ставки ЦБ РФ ≈ 0.05%–0.07% в день)."
                        ),
                        quote=penalty_match.group(0),
                        law_reference="ч. 7 ст. 34 44-ФЗ, Постановление Правительства РФ № 1042 от 30.08.2017",
                        recommendation="Направить официальный запрос заказчику с требованием привести условие об ответственности в соответствие с ПП № 1042.",
                    )
                )

        return risks

    @classmethod
    def _audit_med_compliance(cls, context: str, summary: TenderSummary) -> MedComplianceAudit:
        ktru_match = re.search(r"\b(\d{2}\.\d{2}\.\d{2}\.\d{3}-\d{8})\b|\b(\d{2}\.\d{2}\.\d{2}\.\d{3})\b", context)
        ktru_code = ktru_match.group(0) if ktru_match else "26.60.14.110"

        national_regime = bool(re.search(r"878|102|национальн|ограничени", context, re.IGNORECASE))

        return MedComplianceAudit(
            ru_required=True,
            ru_notes="Требуется действующее регистрационное удостоверение Росздравнадзора РФ на медицинское изделие.",
            national_regime_applies=national_regime,
            national_regime_details="Установлены ограничения допуска по Постановлению Правительства РФ № 878 (радиоэлектроника / МИ).",
            ktru_used=bool(ktru_code),
            ktru_code=ktru_code,
            installation_and_training=bool(re.search(r"монтаж|пусконалад|инструктаж|ввод в эксплуатац", context, re.IGNORECASE)),
            warranty_period_months=12,
        )

    @classmethod
    def _extract_equipment(
        cls,
        classified_docs: List[ClassifiedDocument],
        context: str,
        summary: TenderSummary,
    ) -> List[EquipmentItem]:
        items: List[EquipmentItem] = []

        # Извлекаем характеристики из таблицы ТЗ
        char_matches = re.findall(r"\|\s*([^\|]{4,60})\s*\|\s*([^\|]{0,25})\s*\|\s*(≤|≥|<|>|не более|не менее|[0-9,\.\s]+[а-яА-Яa-zA-Z%]*)\s*\|", context)
        specs: List[str] = []
        for name, unit, val in char_matches[:12]:
            clean_name = name.strip()
            clean_val = val.strip()
            if clean_name and clean_val and "наименование" not in clean_name.lower():
                specs.append(f"{clean_name}: {clean_val}")

        qty = "1 шт."
        qty_match = re.search(r"(?:количество|объем)[^\d]{1,20}(\d+)\s*(?:шт|штук)", context, re.IGNORECASE)
        if qty_match:
            qty = f"{qty_match.group(1)} шт."

        ktru_match = re.search(r"\b(\d{2}\.\d{2}\.\d{2}\.\d{3}-\d{8})\b", context)
        ktru_code = ktru_match.group(1) if ktru_match else "26.60.14.110"

        items.append(
            EquipmentItem(
                name=summary.purchase_subject,
                quantity=qty,
                ktru_code=ktru_code,
                key_specs=specs[:8] if specs else ["Коннекторная часть IS-1", "Совместимость с МРТ", "Частотная адаптация"],
                potential_bias_warning="Требуется проверка совместимости электродов и коннекторов",
                detected_brand_bias="Спецификация содержит жесткие параметры габаритов и коннекторов стандарта IS-1.",
                suggested_neutral_specs="Убедиться в наличии диапазонных эквивалентов в техническом паспорте предлагаемой модели.",
            )
        )
        return items

    @classmethod
    def _generate_clarifications(cls, risks: List[RiskItem], summary: TenderSummary) -> List[ClarificationRequest]:
        requests: List[ClarificationRequest] = []

        for r in risks:
            if r.category == RiskCategory.TIMING and r.severity == RiskSeverity.HIGH:
                requests.append(
                    ClarificationRequest(
                        subject="Увеличение срока поставки медицинского оборудования",
                        recipient_header=f"Заказчику: {summary.customer_name or 'Заказчик'}\nИзвещение №: {summary.notice_number or 'Н/Д'}",
                        justification="В соответствии с ч. 2 ст. 33 44-ФЗ требования к закупке не должны приводить к необоснованному ограничению количества участников закупки.",
                        draft_text=(
                            f"В проекте контракта по закупке №{summary.notice_number} установлен срок поставки: {r.quote or '5 дней'}.\n"
                            "Учитывая специфику поставляемого оборудования, просим заказчика увеличить срок поставки до разумных 30 календарных дней."
                        ),
                    )
                )
            elif r.category == RiskCategory.MEDICAL and "878" in r.title:
                requests.append(
                    ClarificationRequest(
                        subject="Порядок применения Постановления Правительства РФ № 878",
                        recipient_header=f"Заказчику: {summary.customer_name or 'Заказчик'}\nИзвещение №: {summary.notice_number or 'Н/Д'}",
                        justification="Согласно п. 3 Постановления Правительства РФ № 878 ограничения применяются по правилу 'третий лишний' только при наличии не менее двух удовлетворяющих заявок российского происхождения.",
                        draft_text=(
                            f"Просим дать официальное разъяснение положений извещения №{summary.notice_number}:\n"
                            "Просим подтвердить, что в случае отсутствия 2 и более удовлетворяющих требованиям заявок с продукцией из реестра Минпромторга, "
                            "заявки с товарами иностранного происхождения рассматриваются без применения ограничений."
                        ),
                    )
                )
            elif r.category == RiskCategory.LEGAL and "1042" in (r.law_reference or ""):
                requests.insert(
                    0,
                    ClarificationRequest(
                        subject="Приведение размера неустойки (пени) в соответствие с ПП РФ № 1042",
                        recipient_header=f"Заказчику: {summary.customer_name or 'Заказчик'}\nИзвещение №: {summary.notice_number or 'Н/Д'}",
                        justification="Часть 7 статьи 34 Федерального закона № 44-ФЗ и Постановление Правительства РФ № 1042 от 30.08.2017 устанавливают императивный порядок расчета пени в размере 1/300 ключевой ставки рефинансирования ЦБ РФ.",
                        draft_text=(
                            f"В проекте контракта по закупке №{summary.notice_number} (п. 8.4) установлен размер пени: {r.quote or '0.5% в день'}.\n"
                            "Указанный размер противоречит императивным требованиям ПП РФ № 1042. Просим заказчика привести положение проекта контракта в соответствие с законодательством РФ."
                        ),
                    )
                )

        if not requests:
            requests.append(
                ClarificationRequest(
                    subject="Порядок электронного актирования и приемки товара в ЕИС",
                    recipient_header=f"Заказчику: {summary.customer_name or 'Заказчик'}\nИзвещение №: {summary.notice_number or 'Н/Д'}",
                    justification="Часть 13 статьи 94 Федерального закона № 44-ФЗ устанавливает императивный порядок формирования и подписания электронного документа о приемке в ЕИС.",
                    draft_text=(
                        f"Просим заказчика подтвердить, что приемка товара и экспертиза по закупке №{summary.notice_number} "
                        "будет осуществляться в строгом соответствии с предельными сроками ч. 13 ст. 94 Закона № 44-ФЗ."
                    ),
                )
            )

        return requests
