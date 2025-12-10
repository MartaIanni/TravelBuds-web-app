from backend.orm.models import TripORM, BookingORM
from db.db import db
from backend.schemas.trip import TripCreate, TripUpdate #Per usare Pydantic per la validazione

class TripsDAO:

    #Recupera il singolo viaggio con trip_id
    @staticmethod
    def get_trip_by_id(trip_id: int):
        #Recupera la trip dal DB tramite tid
        return db.session.query(TripORM).filter(TripORM.tid == trip_id).first()

    @staticmethod
    def get_trip_participants(trip_id: int):
        trip = db.session.query(TripORM).filter(TripORM.tid == trip_id).first()
        if not trip:
            return []
        # restituisce lista di UserORM
        return [booking.user for booking in trip.bookings]

    #Recupera tutti i viaggi pubblicati
    @staticmethod
    def get_public_trips():
        return db.session.query(TripORM).filter(TripORM.is_published == True).all()

    #Recupera tutti i viaggi bozza
    @staticmethod
    def get_draft_trips():
        return db.session.query(TripORM).filter(TripORM.is_published == False).all()

    #Recupera tutti i viaggi pubblicati da username (coord)
    @staticmethod
    def get_username_public_trips(username):
        return db.session.query(TripORM).filter(
            TripORM.coordinator.has(username=username),
            TripORM.is_published == True
            ).all()

    #Recupera tutti gli username che hanno prenotato un certo viaggio
    @staticmethod
    def get_u_list(tripcode: int):
        bookings = db.session.query(BookingORM).filter(BookingORM.trip_id == tripcode).all()
        return [b.user.username for b in bookings]  # recupera tutti gli User (info complete non solo gli username)

    #Creazione nuovo viaggio e salvataggio nel db
    @staticmethod
    def add_trip(trip_data: dict):
        try:
            #Validazione Pydantic:
            check_new_trip = TripCreate(**trip_data)
            #Conversione in dict
            new_trip = check_new_trip.model_dump()
            #Creazione ORM e salvataggio
            trip_orm = TripORM(**new_trip)
            db.session.add(trip_orm)
            db.session.commit()
            return True
        except Exception as e:
            print("Errore nella memorizzazione del viaggio:", e)
            db.session.rollback()
            return False

    #Cancella un viaggio dal db
    @staticmethod
    def delete_trip(trip_id: int):
        #Seleziona il viaggio tramite tid
        trip = db.session.query(TripORM).filter(TripORM.tid == trip_id).first()
        if not trip:
            return False
        try:
            db.session.delete(trip)
            db.session.commit()
            return True
        except Exception as e:
            print("Errore nella cancellazione del viaggio:", e)
            db.session.rollback()
            return False

    #Aggiorna un viaggio nel db
    @staticmethod
    def update_trip(trip_id: int, trip_data: dict):
        trip = db.session.query(TripORM).filter(TripORM.tid == trip_id).first()
        if not trip:
            return False
        try:
            #Valida i dati con Pydantic
            validated_updates = TripUpdate(**trip_data)
            #Converti in dict e aggiorna solo i campi che l’utente ha effettivamente inviato
            trip_updates = validated_updates.model_dump(exclude_unset=True)
            
            #Applica gli update all'oggetto ORM
            for key, value in trip_updates.items():
                setattr(trip, key, value) #aggiorna l'oggetto trip ORM con i nuovi value associati a key
            db.session.commit()
            return True
        except Exception as e:
            print("Errore nell'aggiornamento del viaggio:", e)
            db.session.rollback()
            return False

    #Cambia is_public in True di un viaggio nel db
    @staticmethod
    def public_trip(trip_id: int):
        #Seleziona il viaggio tramite tid
        trip = db.session.query(TripORM).filter(TripORM.tid == trip_id).first()
        if not trip:
            return False
        try:
            trip.is_published = True #aggiorna l’attributo sull'oggetto ORM trip
            db.session.commit()
            return True
        except Exception as e:
            print("Errore nella pubblicazione del viaggio:", e)
            db.session.rollback()
            return False
        finally:
            db.session.close()
        
    @staticmethod
    def update_seats(trip_id: int, new_value: int):
        trip = db.session.query(TripORM).filter(TripORM.tid == trip_id).first()
        if not trip:
            return False
        try:
            trip.free_seats = new_value
            db.session.commit()
            return True
        except Exception as e:
            print("Errore nell'aggiornamento dei numeri dei posti viaggio:", e)
            db.session.rollback()
            return False
        finally:
            db.session.close()
