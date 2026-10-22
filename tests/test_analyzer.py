import os
from app.services.analyzer import TenderAnalyzerPipeline
from app.models.schemas import TrafficLightVerdict, RiskSeverity
from app.utils.export import ReportExporter


def test_analyzer_pipeline_end_to_end_mock():
    """Сквозной тест работы пайплайна с эталонным образцом закупки УЗИ."""
    sample_file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "sample_data",
        "sample_med_tender.md"
    )
    assert os.path.exists(sample_file_path), "Файл с тестовыми данными должен существовать"

    with open(sample_file_path, "rb") as f:
        file_bytes = f.read()

    pipeline = TenderAnalyzerPipeline()
    result = pipeline.process_file_bytes(
        filename="sample_med_tender.md",
        file_bytes=file_bytes,
        force_mock=True
    )

    # 1. Проверяем метрики выполнения
    assert result.execution_time_seconds >= 0.0
    assert result.total_documents == 1
    assert result.total_characters > 1000

    # 2. Проверяем отчет
    report = result.report
    assert report.verdict == TrafficLightVerdict.RED
    assert report.risk_score >= 80
    assert "Mindray" in report.verdict_summary or "ловушк" in report.verdict_summary.lower() or "пени" in report.verdict_summary.lower()

    # 3. Проверяем наличие ключевых рисков
    severities = [r.severity for r in report.risks]
    assert RiskSeverity.HIGH in severities

    # 4. Проверяем медицинский комплаенс
    assert report.med_compliance.ru_required is True
    assert report.med_compliance.national_regime_applies is True

    # 5. Проверяем генератор запросов
    assert any("1042" in (cr.justification + cr.draft_text) for cr in report.clarification_requests)

    # 6. Проверяем генерацию Markdown-отчета
    md_output = ReportExporter.to_markdown(report)
    assert "# ЭКСПЕРТНОЕ ЗАКЛЮЧЕНИЕ" in md_output
    assert "СТОП-ФАКТОРЫ" in md_output
