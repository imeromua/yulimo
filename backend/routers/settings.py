"""Маршрути для налаштувань сайту."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import require_admin
from models.settings import SiteSetting
from schemas.settings import SiteSettingBulkUpdate, SiteSettingRead, SiteSettingUpdate

router = APIRouter()


@router.get("/settings", tags=["Налаштування"])
def public_settings(db: Session = Depends(get_db)):
    """Публічний ендпойнт — повертає всі налаштування як {key: value}."""
    settings = db.query(SiteSetting).all()
    return {"success": True, "data": {s.key: s.value for s in settings}, "message": ""}


@router.get("/admin/settings", tags=["Налаштування"])
def list_settings(
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    settings = db.query(SiteSetting).order_by(SiteSetting.group, SiteSetting.id).all()
    grouped: dict = {}
    for s in settings:
        grouped.setdefault(s.group, []).append(SiteSettingRead.model_validate(s))
    return {"success": True, "data": grouped, "message": ""}


@router.put("/admin/settings/{key}", tags=["Налаштування"])
def update_setting(
    key: str,
    data: SiteSettingUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    setting = db.query(SiteSetting).filter(SiteSetting.key == key).first()
    if not setting:
        raise HTTPException(status_code=404, detail="Налаштування не знайдено")
    setting.value = data.value
    db.commit()
    db.refresh(setting)
    return {"success": True, "data": SiteSettingRead.model_validate(setting), "message": "Збережено"}


@router.post("/admin/settings/bulk", tags=["Налаштування"])
def bulk_update_settings(
    data: SiteSettingBulkUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    updated = []
    for key, value in data.settings.items():
        setting = db.query(SiteSetting).filter(SiteSetting.key == key).first()
        if setting:
            setting.value = str(value)
            updated.append(key)
    db.commit()
    return {"success": True, "data": {"updated": updated}, "message": f"Оновлено {len(updated)} налаштувань"}
