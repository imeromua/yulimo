"""Сервіс ресторану: меню та резервація столиків."""

from typing import Optional

from sqlalchemy.orm import Session

from models.restaurant import MenuItem, TableReservation
from schemas.restaurant import MenuItemCreate, MenuItemUpdate, TableReservationCreate


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


def update_menu_item(item_id: int, data: MenuItemUpdate, db: Session) -> Optional[MenuItem]:
    """Оновлює існуючу позицію меню. Повертає None якщо не знайдено."""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    db.commit()
    db.refresh(item)
    return item


def delete_menu_item(item_id: int, db: Session) -> bool:
    """Видаляє позицію меню. Повертає True якщо успішно, False якщо не знайдено."""
    item = db.query(MenuItem).filter(MenuItem.id == item_id).first()
    if not item:
        return False
    db.delete(item)
    db.commit()
    return True
