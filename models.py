from datetime import datetime
#Pydantic:
from pydantic import BaseModel, Field, SecretStr, field_validator, computed_field, model_validator
#Annotated: vincoli sui fields
#Literal: limitare i valori di un field
from typing import Literal, Annotated

#Check se password inserita e' corretta
from werkzeug.security import check_password_hash

# from flask_login import UserMixin # type: ignore

# class User(UserMixin):
#     def __init__(self, name, surname, birthdate, gender, username, password, admin):
#         self.name = name
#         self.surname = surname
#         self.birthdate = birthdate
#         self.gender = gender
#         self.username = username
#         self.password = password
#         self.admin = admin
#     def get_id(self):
#         return self.username
    
#Pydantic:
class User(BaseModel):
    uid: Annotated[int, Field(gt=0),]
    name: Annotated[str, Field(pattern=r"^[a-zA-Z\s]+$")]
    surname: Annotated[str, Field(pattern=r"^[a-zA-Z\s]+$")]
    username: str
    password: SecretStr
    birthdate: str
    gender: str
    is_coordinator: bool

class UserRegistration(BaseModel):
    username: str
    password: str
    db_password: str

    @model_validator(mode="after")
    def password_match(self) -> "UserRegistration":
        if not check_password_hash(self.db_password, self.password):
            raise ValueError("Password errata!")
        return self

class Trip(BaseModel):
    tripcode: Annotated[int, Field(gt=0),]
    destination: str
    start: Annotated[str, Field(pattern=r"^\d{2}/\d{2}/\d{4}$")]  # es accetta: 11/11/2025
    end: Annotated[str, Field(pattern=r"^\d{2}/\d{2}/\d{4}$")]
    seats: Annotated[int, Field(ge=0),]
    description: str = ""
    transport_price: Annotated[int, Field(ge=0),]
    stay_price: Annotated[int, Field(ge=0),]
    act_price: Annotated[int, Field(ge=0),]
    subtitle: str = ""
    tour: str = ""
    is_published: bool = False
    card_img_path: str = ""
    bg_img_path: str = ""
    coordinator: User
    max_seats: int = 10
    #NEWTRIP:

    #Start sia successiva alla data odierna
    @field_validator("start")
    @classmethod
    def validate_date_start(cls, v: str):
        start = datetime.strptime(v, "%d/%m/%Y")
        if start.date() < datetime.today().date():
            raise ValueError("La data di inizio deve essere successiva a oggi.")
        return v
    
    #End sia successivo alla data di start
    @field_validator("end")
    @classmethod
    def validate_date_end(cls, v: str, info):
        #in info.data abbiamo i campi gia' validati in ordine precedenti a end (incluso start)
        start_str = info.data.get("start")
        if start_str:
            start = datetime.strptime(start_str, "%d/%m/%Y")
            end = datetime.strptime(v, "%d/%m/%Y")
            if end <= start:
                raise ValueError("La data di fine deve essere successiva a quella di inizio.")
        return v
    
    @computed_field
    def nights(self) -> int:
        if not self.start or not self.end:
            return 0
        start_date = datetime.strptime(self.start, "%d/%m/%Y")
        end_date = datetime.strptime(self.end, "%d/%m/%Y")
        return (end_date - start_date).days
    
    #Calcolo il prezzo totale del viaggio:
    @computed_field
    def tot_price(self) -> int:
        return (self.transport_price + self.act_price + self.stay_price)

#X  Calcolo dei posti liberi
    @computed_field
    def free_seats(self) -> int:
        return (self.max_seats - self.seats)
    
class Quest(BaseModel):
    qid: Annotated[int, Field(gt=0),]
    content: str
    user: User
    answer: str | None
    destination: str
    coord: User


class Booking(BaseModel):
    bid: Annotated[int, Field(gt=0),]
    user: User
    trip: Trip
    card_img_path: str




