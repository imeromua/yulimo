"""Маршрути для медіа-менеджера."""

import os
import re
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import require_admin
from models.media import Media
from schemas.media import MediaRead, MediaUpdate

router = APIRouter()

IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "images")
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


def _sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\-_\.]", "_", name)
    return name[:200]


def _ensure_images_dir():
    os.makedirs(IMAGES_DIR, exist_ok=True)


@router.get("/admin/media", tags=["Медіа"])
def list_media(
    section: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    query = db.query(Media)
    if section:
        query = query.filter(Media.section == section)
    items = query.order_by(Media.sort_order.asc(), Media.uploaded_at.desc()).all()
    return {"success": True, "data": [MediaRead.model_validate(m) for m in items], "message": ""}


@router.post("/admin/media/upload", status_code=status.HTTP_201_CREATED, tags=["Медіа"])
async def upload_media(
    file: UploadFile = File(...),
    section: str = Form("other"),
    title_uk: Optional[str] = Form(None),
    sort_order: int = Form(0),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    ext = (file.filename or "").rsplit(".", 1)[-1].lower() if file.filename and "." in file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Дозволені формати: {', '.join(ALLOWED_EXTENSIONS)}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Файл занадто великий (макс. 10 МБ)")

    original_name = file.filename or "upload"
    base_name = _sanitize_filename(original_name.rsplit(".", 1)[0])
    sanitized = f"{base_name}.{ext}"

    # Ensure unique filename
    _ensure_images_dir()
    candidate = sanitized
    counter = 1
    while db.query(Media).filter(Media.filename == candidate).first():
        candidate = f"{base_name}_{counter}.{ext}"
        counter += 1

    file_path = os.path.join(IMAGES_DIR, candidate)
    with open(file_path, "wb") as f:
        f.write(content)

    media = Media(
        filename=candidate,
        original_name=original_name,
        section=section,
        title_uk=title_uk,
        sort_order=sort_order,
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return {"success": True, "data": MediaRead.model_validate(media), "message": "Файл завантажено"}


@router.put("/admin/media/{media_id}", tags=["Медіа"])
def update_media(
    media_id: int,
    data: MediaUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Медіа не знайдено")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(media, field, value)
    db.commit()
    db.refresh(media)
    return {"success": True, "data": MediaRead.model_validate(media), "message": "Оновлено"}


@router.delete("/admin/media/{media_id}", tags=["Медіа"])
def delete_media(
    media_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Медіа не знайдено")
    file_path = os.path.join(IMAGES_DIR, media.filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    db.delete(media)
    db.commit()
    return {"success": True, "data": None, "message": "Видалено"}


@router.post("/admin/media/{media_id}/reorder", tags=["Медіа"])
def reorder_media(
    media_id: int,
    sort_order: int = Query(...),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    media = db.query(Media).filter(Media.id == media_id).first()
    if not media:
        raise HTTPException(status_code=404, detail="Медіа не знайдено")
    media.sort_order = sort_order
    db.commit()
    return {"success": True, "data": None, "message": "Порядок змінено"}


@router.get("/api/gallery", tags=["Галерея"])
def public_gallery(db: Session = Depends(get_db)):
    items = (
        db.query(Media)
        .filter(Media.section == "gallery", Media.is_active == True)
        .order_by(Media.sort_order.asc(), Media.uploaded_at.desc())
        .all()
    )
    return {
        "success": True,
        "data": [
            {
                "id": m.id,
                "filename": m.filename,
                "title_uk": m.title_uk,
                "url": f"/images/{m.filename}",
            }
            for m in items
        ],
        "message": "",
    }
