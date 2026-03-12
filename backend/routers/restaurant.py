"""Маршрути ресторану: меню та резервація столиків."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.auth import require_admin
from models.user import User
from schemas.restaurant import MenuItemCreate, MenuItemResponse, TableReservationCreate, TableReservationResponse
from services.restaurant_service import (
    create_menu_item,
    create_table_reservation,
    get_menu,
)
from services import email_service

router = APIRouter()


@router.get("/menu")
def get_menu_endpoint(category: Optional[str] = None, db: Session = Depends(get_db)):
    """Меню ресторану (опціональний фільтр за категорією)."""
    return get_menu(db, category)


@router.post(
    "/menu",
    response_model=MenuItemResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_menu_item_endpoint(
    data: MenuItemCreate,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin),
):
    """Додати позицію меню (тільки для адміністраторів)."""
    return create_menu_item(data, db)


@router.post(
    "/reserve-table",
    response_model=TableReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def reserve_table(data: TableReservationCreate, db: Session = Depends(get_db)):
    """Резервація столика в ресторані."""
    reservation = create_table_reservation(data, db)

    await email_service.send_table_reservation_confirmation(reservation)
    await email_service.send_table_reservation_notification_admin(reservation)

    return reservation

