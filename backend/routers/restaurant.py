from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.restaurant import MenuItem, TableReservation

router = APIRouter()


@router.get("/menu")
def get_menu(category: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(MenuItem).filter(MenuItem.is_active == True)
    if category:
        query = query.filter(MenuItem.category == category)
    return query.all()


@router.post("/reserve-table")
def reserve_table(data: dict, db: Session = Depends(get_db)):
    reservation = TableReservation(**data)
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return {"success": True, "id": reservation.id}
