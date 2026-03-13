"""Маршрути Email Center."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import require_admin
from models.booking import Booking
from models.email_log import EmailLog
from models.email_template import EmailTemplate
from schemas.email import EmailLogRead, EmailSendManual, EmailStats, EmailTemplateRead, EmailTemplateUpdate
from services.smtp_email_service import send_manual_email, send_template_for_booking

router = APIRouter()


@router.get("/admin/emails/logs", tags=["Email"])
def get_email_logs(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    template_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    query = db.query(EmailLog)
    if status:
        query = query.filter(EmailLog.status == status)
    if template_type:
        query = query.filter(EmailLog.template_type == template_type)
    total = query.count()
    logs = query.order_by(EmailLog.sent_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return {
        "success": True,
        "data": {
            "items": [EmailLogRead.model_validate(l) for l in logs],
            "total": total,
            "page": page,
            "per_page": per_page,
        },
        "message": "",
    }


@router.get("/admin/emails/templates", tags=["Email"])
def get_templates(
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    templates = db.query(EmailTemplate).all()
    return {"success": True, "data": [EmailTemplateRead.model_validate(t) for t in templates], "message": ""}


@router.put("/admin/emails/templates/{template_id}", tags=["Email"])
def update_template(
    template_id: int,
    data: EmailTemplateUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    template = db.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Шаблон не знайдено")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(template, field, value)
    db.commit()
    db.refresh(template)
    return {"success": True, "data": EmailTemplateRead.model_validate(template), "message": "Шаблон оновлено"}


@router.post("/admin/emails/send", status_code=status.HTTP_201_CREATED, tags=["Email"])
async def send_email_manual(
    data: EmailSendManual,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    log = await send_manual_email(
        recipient_email=data.recipient_email,
        recipient_name=data.recipient_name,
        subject=data.subject,
        body=data.body,
        db=db,
    )
    return {"success": True, "data": EmailLogRead.model_validate(log), "message": "Лист надіслано"}


@router.post("/admin/emails/send-template/{booking_id}", status_code=status.HTTP_201_CREATED, tags=["Email"])
async def send_template_email(
    booking_id: int,
    template_type: str = Query(...),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронювання не знайдено")
    log = await send_template_for_booking(booking=booking, template_type=template_type, db=db)
    return {"success": True, "data": EmailLogRead.model_validate(log), "message": "Лист надіслано"}


@router.get("/admin/emails/stats", tags=["Email"])
def get_email_stats(
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    total = db.query(EmailLog).count()
    sent = db.query(EmailLog).filter(EmailLog.status == "sent").count()
    failed = db.query(EmailLog).filter(EmailLog.status == "failed").count()
    pending = db.query(EmailLog).filter(EmailLog.status == "pending").count()

    from sqlalchemy import func as sqlfunc
    type_rows = db.query(EmailLog.template_type, sqlfunc.count(EmailLog.id)).group_by(EmailLog.template_type).all()
    by_type = {row[0] or "manual": row[1] for row in type_rows}

    return {
        "success": True,
        "data": EmailStats(total=total, sent=sent, failed=failed, pending=pending, by_type=by_type),
        "message": "",
    }
