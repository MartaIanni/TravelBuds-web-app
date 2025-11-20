
from pydantic import BaseModel, field_validator, model_validator
from app.domain.types import StrictBool, DateStr
from datetime import datetime

from app.domain.validations import (
    validate_start_after_today,
    validate_end_after_start,
)

try:
    from typing import Self, Optional #Python 3.11
except Exception:
    from typing_extensions import Self  #se Python piu' vecchio si importa Self da typing_extensions

#INSERIRE VALIDAZIONI/NORMALIZZAZIONI sui fields

class TripBase(BaseModel):
    destination: str 
    description: Optional[str] = None
    subtitle: Optional[str] = None
    tour: Optional[str] = None
    start: DateStr
    end: DateStr  
    max_seats: Optional[int] = 0
    free_seats: Optional[int] = 0
    transport_price: Optional[int] = 0
    stay_price: Optional[int] = 0
    act_price: Optional[int] = 0
    card_img_path: Optional[str] = ''
    bg_img_path: Optional[str] = ''
    is_published: StrictBool = False
    coord_id: int

    @field_validator("start", mode="before")
    @classmethod
    def _check_start_after_today(cls, v: DateStr) -> DateStr:
        return validate_start_after_today(v)
    
    @model_validator(mode="after")
    def _check_end_after_start(self) -> Self:
        validate_end_after_start(self.start, self.end)
        return self

class TripCreate(TripBase):
    pass

class TripUpdate(BaseModel):
    destination: str | None = None
    description: str | None = None
    subtitle: str | None = None
    tour: str | None = None
    start: DateStr | None = None
    end: DateStr | None = None
    max_seats: int | None = None
    free_seats: int | None = None
    transport_price: int | None = None
    stay_price: int | None = None
    act_price: int | None = None
    card_img_path: str | None = None
    bg_img_path: str | None = None
    is_published: StrictBool | None = None

    @model_validator(mode="after")
    def _check_end_after_start(self) -> Self:
        if self.start and self.end:
            validate_end_after_start(self.start, self.end)
        return self
    
    @field_validator("start", mode="before")
    @classmethod
    def _check_start_after_today(cls, v: str) -> str:
        if v:
            return validate_start_after_today(v)
        return v

class TripRead(TripBase):
    id: int
    price: int
    nights: int
