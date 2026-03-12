"""Сервіс ресторану: меню та резервація столиків."""

from typing import Optional

from sqlalchemy.orm import Session

from models.restaurant import MenuItem, TableReservation
from schemas.restaurant import MenuItemCreate, TableReservationCreate


def get_menu(db: Session, category: Optional[str] = None) -> list[MenuItem]:
    """Повертає активні позиції меню, опціонально фільтруючи за категорією."""
    q = db.query(MenuItem).filter(MenuItem.is_active == True)
    if category:
        q = q.filter(MenuItem.category == category)
    return q.all()


def create_table_reservation(
    data: TableReservationCreate, db: Session
) -> TableReservation:
    """Зберігає нову резервацію столика."""
    reservation = TableReservation(**data.model_dump())
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def get_all_table_reservations(db: Session) -> list[TableReservation]:
    """Повертає всі резервації столиків."""
    return (
        db.query(TableReservation)
        .order_by(TableReservation.created_at.desc())
        .all()
    )


def create_menu_item(data: MenuItemCreate, db: Session) -> MenuItem:
    """Створює нову позицію меню."""
    item = MenuItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
