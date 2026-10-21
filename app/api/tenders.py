import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.config import settings
from app.core.database import get_db
from app.db.models import User, TenderAudit
from app.api.auth import get_current_user
from app.models.schemas import AnalyzeUrlRequest, FullAnalysisReport
from app.services.eis_scraper import EISScraper
from app.services.analyzer import TenderAnalyzerPipeline

router = APIRouter(prefix="/api/tenders", tags=["tenders"])


@router.post("/analyze-url")
def analyze_by_url(
    payload: AnalyzeUrlRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Анализ закупки по прямой ссылке с zakupki.gov.ru:
    Автоматически скачивает документы, анонимизирует по 152-ФЗ,
    проводит ИИ-аудит и списывает 1 проверку с баланса.
    """
    if current_user.available_credits <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Лимит проверок исчерпан. Пожалуйста, подключите тариф для продолжения аудитов.",
        )

    url = payload.url.strip()
    if not url:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Укажите ссылку на закупку ЕИС")

    # 1. Скачиваем документы через EISScraper
    try:
        eis_files, reg_number = EISScraper.fetch_documents(url)
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except RuntimeError as re_err:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(re_err))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка скачивания с ЕИС: {str(e)}")

    if not eis_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Прикрепленные файлы для закупки №{reg_number} не обнаружены на портале ЕИС.",
        )

    # 2. Запуск сквозного пайплайна анализа
    pipeline = TenderAnalyzerPipeline()
    use_mock = bool(payload.demo_mode) or (not settings.has_api_key)
    try:
        result = pipeline.process_files(
            files=eis_files,
            model_name=payload.model_name or "gpt-5.4-mini",
            force_mock=use_mock,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка работы аналитического модуля: {str(e)}",
        )

    # 3. Списание 1 проверки
    current_user.available_credits -= 1

    # 4. Сохранение в базу данных
    audit = TenderAudit(
        user_id=current_user.id,
        source_url=url,
        notice_number=result.report.summary.notice_number or reg_number,
        purchase_subject=result.report.summary.purchase_subject,
        customer_name=result.report.summary.customer_name,
        law_type=result.report.summary.law_type,
        verdict=result.report.verdict.value,
        risk_score=result.report.risk_score,
        execution_time_seconds=str(result.execution_time_seconds),
        report_json=result.report.model_dump_json(),
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    db.refresh(current_user)

    return {
        "audit_id": audit.id,
        "report": result.report,
        "execution_time_seconds": result.execution_time_seconds,
        "total_documents": result.total_documents,
        "anonymization_stats": result.anonymization_stats,
        "remaining_credits": current_user.available_credits,
    }


@router.post("/analyze-files")
async def analyze_by_files(
    files: List[UploadFile] = File(...),
    model_name: Optional[str] = "gpt-5.4-mini",
    demo_mode: Optional[bool] = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Анализ закупки по загруженным файлам (Word / PDF / ZIP):
    Анонимизирует по 152-ФЗ, проводит ИИ-аудит и списывает 1 проверку.
    """
    if current_user.available_credits <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Лимит проверок исчерпан. Пожалуйста, подключите тариф для продолжения аудитов.",
        )

    if not files:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Не загружено ни одного файла")

    files_payload = []
    for f in files:
        content = await f.read()
        files_payload.append((f.filename, content))

    pipeline = TenderAnalyzerPipeline()
    use_mock = bool(demo_mode) or (not settings.has_api_key)
    try:
        result = pipeline.process_files(
            files=files_payload,
            model_name=model_name or "gpt-5.4-mini",
            force_mock=use_mock,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка обработки файлов: {str(e)}",
        )

    current_user.available_credits -= 1

    audit = TenderAudit(
        user_id=current_user.id,
        source_url=None,
        notice_number=result.report.summary.notice_number,
        purchase_subject=result.report.summary.purchase_subject,
        customer_name=result.report.summary.customer_name,
        law_type=result.report.summary.law_type,
        verdict=result.report.verdict.value,
        risk_score=result.report.risk_score,
        execution_time_seconds=str(result.execution_time_seconds),
        report_json=result.report.model_dump_json(),
    )
    db.add(audit)
    db.commit()
    db.refresh(audit)
    db.refresh(current_user)

    return {
        "audit_id": audit.id,
        "report": result.report,
        "execution_time_seconds": result.execution_time_seconds,
        "total_documents": result.total_documents,
        "anonymization_stats": result.anonymization_stats,
        "remaining_credits": current_user.available_credits,
    }


@router.get("/history")
def get_audit_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Возвращает историю проверенных закупок текущего пользователя."""
    audits = (
        db.query(TenderAudit)
        .filter(TenderAudit.user_id == current_user.id)
        .order_by(TenderAudit.created_at.desc())
        .limit(50)
        .all()
    )
    
    results = []
    for a in audits:
        results.append({
            "id": a.id,
            "notice_number": a.notice_number,
            "purchase_subject": a.purchase_subject,
            "customer_name": a.customer_name,
            "law_type": a.law_type,
            "verdict": a.verdict,
            "risk_score": a.risk_score,
            "created_at": a.created_at.isoformat() if a.created_at else "",
        })
    return results


@router.get("/{audit_id}")
def get_audit_detail(
    audit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Возвращает полный сохраненный отчет по ID проверки."""
    audit = (
        db.query(TenderAudit)
        .filter(TenderAudit.id == audit_id, TenderAudit.user_id == current_user.id)
        .first()
    )
    if not audit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проверка не найдена")

    return {
        "id": audit.id,
        "notice_number": audit.notice_number,
        "source_url": audit.source_url,
        "created_at": audit.created_at.isoformat() if audit.created_at else "",
        "report": json.loads(audit.report_json),
    }
