from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, ForeignKey, Text
from db.db import db
from datetime import datetime
from sqlalchemy import event

# Base per tutti da cui ereditare tutti i modelli ORM
class Base(DeclarativeBase):
    pass

class UserORM(Base):
    __tablename__ = "users"

    uid: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    surname: Mapped[str] = mapped_column(String(100), nullable=False)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    birthdate: Mapped[str] = mapped_column(String(20), nullable=False)
    gender: Mapped[str] = mapped_column(String(200), nullable=False)
    is_coordinator: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    #Domande ricevute (da viaggiatori → verso coordinatore)
    quests_from: Mapped[list["QuestORM"]] = relationship(
        back_populates="coord",
        foreign_keys="QuestORM.coord_id"
    )

    #Tutte le domande fatte dallo User ai Coord (domande del viaggiatore)
    quests_to: Mapped[list["QuestORM"]] = relationship(
        back_populates="user",
        foreign_keys="QuestORM.user_id"
    )

    #Prenotazioni dell'utente
    bookings: Mapped[list["BookingORM"]] = relationship(
        back_populates="user",
        foreign_keys="BookingORM.user_id"
    )

    #Viaggi coordinati da questo user
    coordinated_trips: Mapped[list["TripORM"]] = relationship(
        back_populates="coordinator",
        foreign_keys="TripORM.coord_id"
    )

class TripORM(Base):
    __tablename__ = "trips"

    tid: Mapped[int] = mapped_column(Integer, primary_key=True)
    destination: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    subtitle: Mapped[str] = mapped_column(String(100), default="")
    tour: Mapped[str]= mapped_column(Text, default="")
    start: Mapped[str] = mapped_column(String(10), nullable=False)  # formato dd/mm/yyyy
    end: Mapped[str] = mapped_column(String(10), nullable=False)  # formato dd/mm/yyyy  
    max_seats: Mapped[int] = mapped_column(Integer, default=10)
    free_seats: Mapped[int] = mapped_column(Integer, default=0)
    transport_price: Mapped[int] = mapped_column(Integer, default=0)
    stay_price: Mapped[int] = mapped_column(Integer, default=0)
    act_price: Mapped[int] = mapped_column(Integer, default=0)
    card_img_path: Mapped[str] = mapped_column(String(250), default="")
    bg_img_path: Mapped[str] = mapped_column(String(250), default="")
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    #ForeignKey verso il coordinatore
    coord_id: Mapped[int | None] = mapped_column( ForeignKey("users.uid"), nullable=True)

    price: Mapped[int] = mapped_column(Integer, default=0)
    nights: Mapped[int] = mapped_column(Integer, default=0)

    #Riempito da coordinated_trips in UserORM
    coordinator: Mapped["UserORM"] = relationship(
        back_populates="coordinated_trips",
        foreign_keys=[coord_id]
    )

    #Tutte le prenotazioni a questo viaggio
    bookings: Mapped[list["BookingORM"]] = relationship(
        back_populates="trip",
        foreign_keys="BookingORM.trip_id"
    )

    quests: Mapped[list["QuestORM"]] = relationship(
        back_populates="trip",
        foreign_keys="QuestORM.trip_id"
    )

    #Ottengo la lista user partecipanti al viaggio
    @property
    def participants(self):
        return [booking.user for booking in self.bookings]


#Calcola price e nights prima dell'inserimento nuovo viaggio
@event.listens_for(TripORM, "before_insert")
def calculate_trip_fields(mapper, connection, target: TripORM):
    target.price = (
        target.transport_price +
        target.stay_price +
        target.act_price
    )

    start_date = datetime.strptime(target.start, "%d/%m/%Y")
    end_date = datetime.strptime(target.end, "%d/%m/%Y")
    target.nights = (end_date - start_date).days

#Ricalcola price e nights quando si aggiorna la bozza
@event.listens_for(TripORM, "before_update")
def calculate_trip_fields_update(mapper, connection, target: TripORM):
    target.price = (
        target.transport_price +
        target.stay_price +
        target.act_price
    )

    start_date = datetime.strptime(target.start, "%d/%m/%Y")
    end_date = datetime.strptime(target.end, "%d/%m/%Y")
    target.nights = (end_date - start_date).days

class QuestORM(Base):
    __tablename__ = "quests"

    qid: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=True)
    destination: Mapped[str] = mapped_column(String(100), nullable=False)

    #Viaggiotore che ha fatto la domanda
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.uid"), nullable=False)

    user: Mapped["UserORM"] = relationship(
        back_populates="quests_to",
        foreign_keys=[user_id]
    )

    #Coordinatore a cui è rivolta
    coord_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.uid"), nullable=False)

    coord: Mapped["UserORM"] = relationship(
        back_populates="quests_from",
        foreign_keys=[coord_id]
    )

    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey("trips.tid"), nullable=False)

    trip: Mapped["TripORM"] = relationship(
        back_populates="quests",
        foreign_keys=[trip_id]
    )

class BookingORM(Base):
    __tablename__ = "bookings"

    bid: Mapped[int] = mapped_column(Integer, primary_key=True)
    card_img_path: Mapped[str] = mapped_column(String(250), nullable=False, default="")

    #Riferimento allo user che ha prenotato:
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.uid"), nullable=False)

    user: Mapped["UserORM"] = relationship(
        back_populates="bookings",
        foreign_keys=[user_id]
    )
    
    #Riferimento al viaggio protagonista della prenotazione:
    trip_id: Mapped[int] = mapped_column(Integer, ForeignKey("trips.tid"), nullable=False)

    trip: Mapped["TripORM"] = relationship(
        back_populates="bookings",
        foreign_keys=[trip_id]
    )
    
