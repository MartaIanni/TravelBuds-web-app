from db.db import db
from app.schemas.booking import BookingCreate
from app.orm.models import BookingORM, UserORM

class BookingsDAO:

    @staticmethod
    def check_is_booked(user_id: int, trip_id: int):
        booking = db.session.query(BookingORM).filter(BookingORM.trip_id == trip_id, BookingORM.user_id == user_id).first()
        if booking:
            return True
        return False
    
    @staticmethod
    def get_booked_trips(username: str):
        user = db.session.query(UserORM).filter(UserORM.username == username).first()
        if not user:
            return []
        return user.bookings
    
    @staticmethod
    def add_booking(booking_data: dict):
        try:
            check_new_booking = BookingCreate(**booking_data)
            new_booking = check_new_booking.model_dump()
            booking_orm = BookingORM(**new_booking)
            db.session.add(booking_orm)
            db.session.commit()
            return True
        except Exception as e:
            print("Errore nel caricamento della nuova prenotazione:", e)
            db.session.rollback()
            return False