import pytest
from app.services.classifier import ClassifiedDocument, DocumentType
from app.services.extractor import ExtractedDocument
from app.services.context_optimizer import ContextOptimizer
from app.services.analyzer import TenderAnalyzerPipeline


def test_contract_draft_optimization_removes_boilerplate_preserves_penalties():
    contract_text = """
1. ПРЕДМЕТ КОНТРАКТА
1.1. Поставщик обязуется поставить медицинское оборудование в соответствии со спецификацией.

2. СРОКИ И УСЛОВИЯ ПОСТАВКИ
2.1. Поставка Товара осуществляется в течение 5 (пяти) календарных дней с даты заключения контракта.

3. ОТВЕТСТВЕННОСТЬ СТОРОН
3.1. За каждый день просрочки исполнения поставщик уплачивает пеню в размере 0,5 процента от цены Контракта.
3.2. Штрафы начисляются в порядке Постановления Правительства РФ № 1042.

8. ОБСТОЯТЕЛЬСТВА НЕПРЕОДОЛИМОЙ СИЛЫ (ФОРС-МАЖОР)
8.1. Стороны освобождаются от ответственности за частичное или полное неисполнение обязательств по Контракту, если оно явилось следствием обстоятельств непреодолимой силы: пожара, наводнения, землетрясения, военных действий, эпидемий, подтвержденных Торгово-промышленной палатой РФ.
8.2. Сторона, для которой создалась невозможность исполнения обязательств, обязана в течение 3 дней уведомить другую Сторону.

9. АНТИКОРРУПЦИОННАЯ ОГОВОРКА
9.1. При исполнении своих обязательств Стороны, их аффилированные лица и работники не выплачивают и не предлагают выплатить какие-либо денежные средства или ценности лицам для оказания влияния.

14. АДРЕСА И БАНКОВСКИЕ РЕКВИЗИТЫ СТОРОН
Заказчик: ГБУЗ СОКБ, ИНН 6315001234, КПП 631501001, БИК 043601001, р/с 40702810900000000001, к/с 30101810200000000607 в Отделении Самара.
Поставщик: ООО МедСнаб, ИНН 7701234567, КПП 770101001, р/с 40702810500000000002.
    """

    optimized, preserved_sections = ContextOptimizer.optimize_contract_draft(contract_text)

    # 1. Проверяем, что критические разделы сохранены
    assert "5 (пяти) календарных дней" in optimized
    assert "0,5 процента" in optimized
    assert "1042" in optimized
    assert "ПРЕДМЕТ КОНТРАКТА" in optimized

    # 2. Проверяем, что юридическая вода и банковские счета удалены
    assert "пожара, наводнения, землетрясения" not in optimized
    assert "Торгово-промышленной палатой" not in optimized
    assert "не выплачивают и не предлагают выплатить" not in optimized
    assert "40702810900000000001" not in optimized

    # 3. Проверяем, что сохраненные секции отражены в списке
    assert any("ОТВЕТСТВЕННОСТЬ" in s.upper() for s in preserved_sections)
    assert any("СРОКИ" in s.upper() for s in preserved_sections)


def test_tech_spec_tables_and_parameters_strictly_preserved():
    tech_spec_text = """
1. ОБЩИЕ ТРЕБОВАНИЯ К ТОВАРУ
Настоящее описание определяет перечень и функциональные характеристики оборудования.
Поставщик обязан соблюдать правила охраны труда и пожарной безопасности при погрузочных работах.

2. ТРЕБОВАНИЯ К ОБОРУДОВАНИЮ И КОМПЛЕКТАЦИИ
Товар должен быть новым, 2026 года выпуска, не бывшим в употреблении.
Наличие действующего регистрационного удостоверения (РУ) Росздравнадзора обязательно.
Код позиции КТРУ: 26.60.12.119-00000001.

--- Таблица 1 ---
Наименование параметра | Требуемое значение Заказчика | Единица измерения
Диапазон частот конвексного датчика | от 1.2 до 6.0 | МГц
Диагональ основного медицинского монитора | не менее 21.5 | дюйм
Количество активных портов для датчиков | не менее 4 | шт.
Наличие технологии зонного акустического преобразования | Да, эквивалент не допускается | Да/Нет
Потребляемая мощность | не более 150 | Вт
Гарантийный срок производителя | 24 | мес.
    """

    optimized, preserved_sections = ContextOptimizer.optimize_tech_spec(tech_spec_text)

    # 1. Таблица и все её параметры должны быть сохранены на 100%
    assert "--- Таблица 1 ---" in optimized
    assert "Диапазон частот конвексного датчика" in optimized
    assert "от 1.2 до 6.0" in optimized
    assert "МГц" in optimized
    assert "21.5" in optimized
    assert "дюйм" in optimized
    assert "эквивалент не допускается" in optimized
    assert "24" in optimized

    # 2. Критические нормативные требования сохранены
    assert "регистрационного удостоверения" in optimized
    assert "26.60.12.119" in optimized
    assert "2026 года выпуска" in optimized

    # 3. Общая вода про охрану труда опущена
    assert "правила охраны труда" not in optimized


def test_safety_windowing_catches_traps_in_hidden_sections():
    """Если заказчик спрятал кабальные пени внутри раздела 'Форс-мажор', ловушка обязана сохраниться."""
    text = """
8. ОБСТОЯТЕЛЬСТВА НЕПРЕОДОЛИМОЙ СИЛЫ (ФОРС-МАЖОР)
8.1. Стороны освобождаются от ответственности при пожарах и наводнениях.
8.2. В случае задержки поставки Поставщик уплачивает пеню 1.5% за каждый день просрочки по ПП РФ № 1042.
    """

    optimized, preserved_sections = ContextOptimizer.optimize_contract_draft(text)

    assert "пеню 1.5% за каждый день просрочки" in optimized
    assert "1042" in optimized
    assert "пожарах и наводнениях" not in optimized


def test_context_optimizer_end_to_end_stats():
    doc1 = ExtractedDocument(
        filename="ТЗ.docx",
        file_type="docx",
        text_content="""
--- Таблица 1 ---
Параметр | Значение
Частота | 5 МГц
Мощность | 100 Вт
Наличие РУ Росздравнадзора: Да.
        """,
        char_count=100,
    )
    boilerplate_filler = "Стандартные условия действия обстоятельств непреодолимой силы в соответствии с ГК РФ. " * 25
    bank_filler = "Адреса и банковские реквизиты сторон, номера счетов и казначейских счетов казначейства. " * 20
    doc2 = ExtractedDocument(
        filename="Проект_контракта.docx",
        file_type="docx",
        text_content=f"""
1. ПРЕДМЕТ
Поставка медицинского товара.

2. СРОК ПОСТАВКИ
Срок поставки 10 календарных дней.

3. ОТВЕТСТВЕННОСТЬ
Пеня 0.1% в день.

8. ФОРС-МАЖОР
{boilerplate_filler}

9. БАНКОВСКИЕ РЕКВИЗИТЫ
Р/с 40702810000000000000, БИК 044525225, КПП 770101001. {bank_filler}
        """,
        char_count=2000,
    )

    c_docs = [
        ClassifiedDocument(doc=doc1, doc_type=DocumentType.TECH_SPEC, score=3.0),
        ClassifiedDocument(doc=doc2, doc_type=DocumentType.CONTRACT_DRAFT, score=3.0),
    ]

    optimized_text, stats = ContextOptimizer.optimize_classified_documents(c_docs)

    assert stats.original_characters > stats.optimized_characters
    assert stats.compression_ratio_percent > 0
    assert stats.saved_tokens_approx > 0
    assert len(stats.preserved_sections) >= 1

    assert "5 МГц" in optimized_text
    assert "10 календарных дней" in optimized_text
    assert "Пеня 0.1%" in optimized_text
    assert "40702810000000000000" not in optimized_text
    assert "землетрясения, наводнения" not in optimized_text


def test_pipeline_execution_result_includes_optimization_stats():
    pipeline = TenderAnalyzerPipeline()
    # Тестовый файл в памяти
    content = """
    ТЕХНИЧЕСКОЕ ЗАДАНИЕ
    --- Таблица 1 ---
    Параметр | Требование
    Датчик | 3.5 МГц
    Срок поставки: 5 календарных дней.
    """.encode("utf-8")
    res = pipeline.process_file_bytes(
        filename="tz.txt",
        file_bytes=content,
        force_mock=True,
    )

    assert res.report is not None
    assert res.optimization_stats is not None
    assert res.report.optimization_stats is not None
