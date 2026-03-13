"""FSM-стани для Telegram-бота."""

from aiogram.fsm.state import State, StatesGroup


class BookingStates(StatesGroup):
    select_room = State()
    enter_checkin = State()
    enter_checkout = State()
    enter_name = State()
    enter_phone = State()
    enter_email = State()
    enter_guests = State()
    confirm = State()


class TableStates(StatesGroup):
    enter_date = State()
    enter_time = State()
    enter_guests = State()
    enter_name = State()
    enter_phone = State()
    confirm = State()


class AvailabilityStates(StatesGroup):
    enter_checkin = State()
    enter_checkout = State()
