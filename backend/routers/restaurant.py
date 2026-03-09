"""Маршрути ресторану: меню та резервація столиків."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from schemas.restaurant import TableReservationCreate, TableReservationResponse
from services.restaurant_service import (
    create_table_reservation,
    get_menu,
)

router = APIRouter()


@router.get("/menu")
def get_menu_endpoint(category: Optional[str] = None, db: Session = Depends(get_db)):
    """Меню ресторану (опціональний фільтр за категорією)."""
    return get_menu(db, category)


@router.post(
    "/reserve-table",
    response_model=TableReservationResponse,
    status_code=status.HTTP_201_CREATED,
)
def reserve_table(data: TableReservationCreate, db: Session = Depends(get_db)):
    """Резервація столика в ресторані."""
    reservation = create_table_reservation(data, db)
    return reservation

