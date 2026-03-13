"""Маршрути для управління клієнтами (CRM)."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import require_admin
from models.booking import Booking
from models.client import Client
from schemas.client import ClientCreate, ClientRead, ClientUpdate

router = APIRouter()


def _client_to_read(client: Client, db: Session) -> ClientRead:
    bookings = db.query(Booking).filter(Booking.client_id == client.id).all()
    bookings_count = len(bookings)
    last_visit = None
    if bookings:
        check_outs = [b.check_out for b in bookings if b.check_out]
        if check_outs:
            last_visit = max(check_outs)
    return ClientRead(
        id=client.id,
        name=client.name,
        phone=client.phone,
        email=client.email,
        birthday=client.birthday,
        notes=client.notes,
        source=client.source,
        is_active=client.is_active,
        bookings_count=bookings_count,
        last_visit=last_visit,
        created_at=client.created_at,
        updated_at=client.updated_at,
    )


@router.get("/admin/clients", tags=["Клієнти"])
def list_clients(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    query = db.query(Client)
    if search:
        pattern = f"%{search}%"
        query = query.filter(
            Client.name.ilike(pattern)
            | Client.phone.ilike(pattern)
            | Client.email.ilike(pattern)
        )
    total = query.count()
    clients = query.order_by(Client.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return {
        "success": True,
        "data": {
            "items": [_client_to_read(c, db) for c in clients],
            "total": total,
            "page": page,
            "per_page": per_page,
        },
        "message": "",
    }


@router.post("/admin/clients", status_code=status.HTTP_201_CREATED, tags=["Клієнти"])
def create_client(
    data: ClientCreate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    existing = db.query(Client).filter(Client.phone == data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Клієнт з таким номером телефону вже існує")
    client = Client(**data.model_dump())
    db.add(client)
    db.commit()
    db.refresh(client)
    return {"success": True, "data": _client_to_read(client, db), "message": "Клієнта створено"}


@router.get("/admin/clients/{client_id}", tags=["Клієнти"])
def get_client(
    client_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клієнта не знайдено")
    bookings = db.query(Booking).filter(Booking.client_id == client_id).order_by(Booking.created_at.desc()).all()
    client_data = _client_to_read(client, db)
    booking_list = [
        {
            "id": b.id,
            "room_id": b.room_id,
            "check_in": str(b.check_in),
            "check_out": str(b.check_out),
            "nights": b.nights,
            "total_price": b.total_price,
            "status": b.status.value if hasattr(b.status, "value") else b.status,
            "created_at": str(b.created_at),
        }
        for b in bookings
    ]
    return {"success": True, "data": {"client": client_data, "bookings": booking_list}, "message": ""}


@router.put("/admin/clients/{client_id}", tags=["Клієнти"])
def update_client(
    client_id: int,
    data: ClientUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клієнта не знайдено")
    update_data = data.model_dump(exclude_unset=True)
    if "phone" in update_data:
        existing = db.query(Client).filter(Client.phone == update_data["phone"], Client.id != client_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Клієнт з таким номером телефону вже існує")
    for field, value in update_data.items():
        setattr(client, field, value)
    db.commit()
    db.refresh(client)
    return {"success": True, "data": _client_to_read(client, db), "message": "Клієнта оновлено"}


@router.delete("/admin/clients/{client_id}", tags=["Клієнти"])
def delete_client(
    client_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Клієнта не знайдено")
    client.is_active = False
    db.commit()
    return {"success": True, "data": None, "message": "Клієнта деактивовано"}


@router.post("/admin/clients/from-booking/{booking_id}", status_code=status.HTTP_201_CREATED, tags=["Клієнти"])
def create_client_from_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Бронювання не знайдено")
    existing = db.query(Client).filter(Client.phone == booking.guest_phone).first()
    if existing:
        if booking.client_id != existing.id:
            booking.client_id = existing.id
            db.commit()
        return {"success": True, "data": _client_to_read(existing, db), "message": "Клієнт вже існує, бронювання прив'язано"}
    client = Client(
        name=booking.guest_name,
        phone=booking.guest_phone,
        email=booking.guest_email,
        source="website",
    )
    db.add(client)
    db.flush()
    booking.client_id = client.id
    db.commit()
    db.refresh(client)
    return {"success": True, "data": _client_to_read(client, db), "message": "Клієнта створено з бронювання"}
