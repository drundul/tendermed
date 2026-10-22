import json
from urllib.parse import quote
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.db.models import User, TenderAudit
from app.api.auth import get_current_user
from app.models.schemas import FullAnalysisReport
from app.utils.export import ReportExporter

router = APIRouter(prefix="/api/exports", tags=["exports"])

DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def _get_audit_and_report(audit_id: int, user_id: int, db: Session) -> FullAnalysisReport:
    """Извлекает и десериализует отчет из базы данных."""
    audit = db.query(TenderAudit).filter(
        TenderAudit.id == audit_id,
        TenderAudit.user_id == user_id
    ).first()
    if not audit:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Проверка не найдена")
    
    data = json.loads(audit.report_json)
    return FullAnalysisReport.model_validate(data)


@router.get("/tenders/{audit_id}/report.docx")
def export_docx_report(
    audit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Скачивание полного экспертного аудита закупки в формате Word (.docx)."""
    report = _get_audit_and_report(audit_id, current_user.id, db)
    docx_bytes = ReportExporter.to_docx_report(report)

    filename = f"Tender_Audit_{report.summary.notice_number or 'Report'}.docx"
    encoded_filename = quote(filename)

    return Response(
        content=docx_bytes,
        media_type=DOCX_MIME,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
    )


@router.get("/tenders/{audit_id}/clarifications.docx")
def export_docx_all_clarifications(
    audit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Скачивание ВСЕХ официальных запросов на разъяснение единым файлом Word (.docx)."""
    report = _get_audit_and_report(audit_id, current_user.id, db)
    if not report.clarification_requests:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="В отчете нет запросов на разъяснение")

    docx_bytes = ReportExporter.to_docx_all_clarifications(
        report.clarification_requests, report.summary
    )

    filename = f"Vse_Zaprosy_{report.summary.notice_number or '44FZ'}.docx"
    encoded_filename = quote(filename)

    return Response(
        content=docx_bytes,
        media_type=DOCX_MIME,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
    )


@router.get("/tenders/{audit_id}/clarification/{index}.docx")
def export_docx_single_clarification(
    audit_id: int,
    index: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Скачивание конкретного официального запроса на разъяснение в формате Word (.docx)."""
    report = _get_audit_and_report(audit_id, current_user.id, db)
    if not report.clarification_requests or index < 1 or index > len(report.clarification_requests):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Запрос с таким номером не найден")

    cr = report.clarification_requests[index - 1]
    docx_bytes = ReportExporter.to_docx_clarification_request(cr, report.summary, index)

    filename = f"Zapros_Raziasneniy_{index}_{report.summary.notice_number or '44FZ'}.docx"
    encoded_filename = quote(filename)

    return Response(
        content=docx_bytes,
        media_type=DOCX_MIME,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
    )


@router.get("/tenders/{audit_id}/report.md")
def export_markdown_report(
    audit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Скачивание отчета в формате Markdown (.md)."""
    report = _get_audit_and_report(audit_id, current_user.id, db)
    md_text = ReportExporter.to_markdown(report)

    filename = f"Tender_Audit_{report.summary.notice_number or 'Report'}.md"
    encoded_filename = quote(filename)

    return Response(
        content=md_text.encode("utf-8"),
        media_type="text/markdown; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
    )


@router.get("/tenders/{audit_id}/fas-complaint.docx")
def export_docx_fas_complaint(
    audit_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Скачивание официальной жалобы в ФАС России (ст. 105 44-ФЗ) в формате Word (.docx)."""
    report = _get_audit_and_report(audit_id, current_user.id, db)

    complaint = report.fas_complaint
    if not complaint:
        from app.services.fas_generator import FASComplaintGenerator
        complaint = FASComplaintGenerator.generate(
            report,
            applicant_name=current_user.company_name or "Участник закупки",
            applicant_contacts=current_user.email,
        )

    docx_bytes = ReportExporter.export_fas_complaint_docx(complaint)

    filename = f"Zhaloba_FAS_{report.summary.notice_number or '44FZ'}.docx"
    encoded_filename = quote(filename)

    return Response(
        content=docx_bytes,
        media_type=DOCX_MIME,
        headers={"Content-Disposition": f"attachment; filename*=UTF-8''{encoded_filename}"},
    )

