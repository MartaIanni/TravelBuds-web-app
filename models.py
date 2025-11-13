from datetime import datetime
#Pydantic:
from pydantic import BaseModel, Field, SecretStr, field_validator, computed_field
#Annotated: vincoli sui fields
#Literal: limitare i valori di un field
from typing import Literal, Annotated



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
    gender: Literal["M","F"]
    is_coordinator: bool

class Trip(BaseModel):
    destination: str
    start: Annotated[str, Field(pattern=r"^\d{2}/\d{2}/\d{4}$")]  # es accetta: 11/11/2025
    end: Annotated[str, Field(pattern=r"^\d{2}/\d{2}/\d{4}$")]
    seats: Annotated[int, Field(ge=1),]
    description: str = ""
    transport_price: Annotated[int, Field(ge=0),]
    stay_price: Annotated[int, Field(ge=0),]
    act_price: Annotated[int, Field(ge=0),]
    subtitle: str = ""
    price: Annotated[int, Field(ge=0),]
    tripcode: Annotated[int, Field(gt=0),]
    tour: str = ""
    is_published: bool = False
    free_seats: Annotated[int, Field(gt=0),] = 0
    card_img: str = ""
    bg_img: str = ""
    coordinator: User

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
    
# class Quest(BaseModel):

# class Booking(BaseModel):


