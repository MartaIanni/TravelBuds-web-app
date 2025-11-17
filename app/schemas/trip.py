
from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from app.domain.types import StrictBool, DateStr

from app.domain.validations import (
    validate_start_after_today,
    validate_end_after_start,
)

try:
    from typing import Self #Python 3.11
except Exception:
    from typing_extensions import Self  #se Python piu' vecchio si importa Self da typing_extensions

#INSERIRE VALIDAZIONI/NORMALIZZAZIONI sui fields

class TripBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    destination: str
    description: str
    subtitle: str
    tour: str
    start: DateStr
    end: DateStr  
    max_seats: int
    seats: int
    transport_price: int
    stay_price: int
    act_price: int
    card_img_path: str
    bg_img_path: str
    is_published: StrictBool

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
    model_config = ConfigDict(extra="forbid")

    destination: str | None = None
    description: str | None = None
    subtitle: str | None = None
    tour: str | None = None
    start: DateStr | None = None
    end: DateStr | None = None
    max_seats: int | None = None
    seats: int | None = None
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
    model_config = ConfigDict(from_attributes=True)
    id: int
