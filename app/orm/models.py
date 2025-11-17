from datetime import date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Boolean, ForeignKey, Text


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
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    is_coordinator: Mapped[bool] = mapped_column(Boolean, default=False)

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
    seats: Mapped[int] = mapped_column(Integer, default=0)
    transport_price: Mapped[int] = mapped_column(Integer, default=0)
    stay_price: Mapped[int] = mapped_column(Integer, default=0)
    act_price: Mapped[int] = mapped_column(Integer, default=0)
    card_img_path: Mapped[str] = mapped_column(String(250), default="")
    bg_img_path: Mapped[str] = mapped_column(String(250), default="")
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    #ForeignKey verso il coordinatore
    coord_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.uid"), nullable=True
    )
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


class QuestORM(Base):
    __tablename__ = "quests"

    qid: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    destination: Mapped[str] = mapped_column(String(100), nullable=False)

    #Viaggiotore che ha fatto la domanda
    user_id: Mapped[int] = mapped_column(ForeignKey("users.uid"), nullable=False)

    user: Mapped["UserORM"] = relationship(
        back_populates="quests_to",
        foreign_keys=[user_id]
    )

    #Coordinatore a cui è rivolta
    coord_id: Mapped[int] = mapped_column(ForeignKey("users.uid"), nullable=False)

    coord: Mapped["UserORM"] = relationship(
        back_populates="quests_from",
        foreign_keys=[coord_id]
    )

class BookingORM(Base):
    __tablename__ = "bookings"

    bid: Mapped[int] = mapped_column(primary_key=True)
    card_img_path: Mapped[str] = mapped_column(String(2500), nullable=False, default="")

    #Riferimento allo user che ha prenotato:
    user_id: Mapped[int] = mapped_column(ForeignKey("users.uid"), nullable=False)

    user: Mapped["UserORM"] = relationship(
        back_populates="bookings",
        foreign_keys=[user_id]
    )
    
    #Riferimento al viaggio protagonista della prenotazione:
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.tid"), nullable=False)

    trip: Mapped["TripORM"] = relationship(
        back_populates="bookings",
        foreign_keys=[trip_id]
    )
    
