from datetime import datetime
#Pydantic:
from pydantic import BaseModel, Field, SecretStr, field_validator, computed_field
#Annotated: vincoli sui fields
#Literal: limitare i valori di un field
from typing import Literal, Annotated

#Utilizzo di self
from typing_extensions import Self


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
    start: Annotated[str, Field(pattern=r"^[0-9/]$")]
    end: Annotated[str, Field(pattern=r"^[0-9/]$")]
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
    nigths: Annotated[int, Field(gt=0),]
    coordinator: User

    #NEWTRIP:

    #Start sia successiva alla data odierna
    @field_validator("start")
    @classmethod
    def validate_date_start(self, v : str):
        #Recupero la data odierna
        if not datetime.strptime(v, "%Y-%m-%d") > datetime.today():
            raise ValueError("Start successivo a data odierna")
        return v
    
    #End sia successivo alla data di start
    @field_validator("end")
    @classmethod
    def validate_date_end(self, v : str):
        if not datetime.strptime(v, "%Y-%m-%d") > datetime.strptime(self.end, "%Y-%m-%d") :
            raise ValueError("Start successivo a data odierna")
        return v
    
    #Calcolo del computed field (nigths)
    @computed_field
    def nigths_fill(self):
        end = datetime.strptime(self.end, "%Y-%m-%d")
        start = datetime.strptime(self.start, "%Y-%m-%d")
        #Se start e end presenti ritorna il numero di notti altrimenti ritorna default value 0
        if self.start and self.end:
            self.nigths = (end-start).days
        return 0

# class Quest(BaseModel):

# class Booking(BaseModel):


