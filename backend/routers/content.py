"""Маршрути для керування контент-блоками."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import require_admin
from models.content_block import ContentBlock
from schemas.content import ContentBlockCreate, ContentBlockRead, ContentBlockUpdate

router = APIRouter()


@router.get("/api/content", tags=["Контент"])
def public_content(db: Session = Depends(get_db)):
    """Публічний ендпойнт — повертає всі блоки як {key: value}."""
    blocks = db.query(ContentBlock).all()
    return {"success": True, "data": {b.key: b.value for b in blocks}, "message": ""}


@router.get("/admin/content", tags=["Контент"])
def list_content(
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    blocks = db.query(ContentBlock).order_by(ContentBlock.section, ContentBlock.key).all()
    grouped: dict = {}
    for b in blocks:
        grouped.setdefault(b.section, []).append(ContentBlockRead.model_validate(b))
    return {"success": True, "data": grouped, "message": ""}


@router.put("/admin/content/{key}", tags=["Контент"])
def update_content(
    key: str,
    data: ContentBlockUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    block = db.query(ContentBlock).filter(ContentBlock.key == key).first()
    if not block:
        raise HTTPException(status_code=404, detail="Блок не знайдено")
    block.value = data.value
    db.commit()
    db.refresh(block)
    return {"success": True, "data": ContentBlockRead.model_validate(block), "message": "Збережено"}


@router.post("/admin/content", status_code=201, tags=["Контент"])
def create_content(
    data: ContentBlockCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    existing = db.query(ContentBlock).filter(ContentBlock.key == data.key).first()
    if existing:
        raise HTTPException(status_code=400, detail="Блок з таким ключем вже існує")
    block = ContentBlock(**data.model_dump())
    db.add(block)
    db.commit()
    db.refresh(block)
    return {"success": True, "data": ContentBlockRead.model_validate(block), "message": "Блок створено"}
