from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional

from app.domain.types import StrictBool, DateStr

from app.domain.validations import (
    clean_string,
)

class UserBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str
    surname: str
    username: str
    password: str
    birthdate: DateStr
    gender: str
    is_coordinator: Optional[StrictBool] = False

    @field_validator("name", mode="after")
    @classmethod
    def _check_valid_name(cls, v: str) -> str:
        return clean_string(v)
    
    @field_validator("surname", mode="after")
    @classmethod
    def _check_valid_surname(cls, v: str) -> str:
        return clean_string(v)
    
    @field_validator("username", mode="after")
    @classmethod
    def _check_valid_username(cls, v: str) -> str:
        return clean_string(v)

class UserCreate(UserBase):
    pass

class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    uid: int

class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = None
    surname: str | None = None
    username: str | None = None
    password: str | None = None
    birthdate: DateStr | None = None
    gender: str | None = None
    is_coordinator: StrictBool | None = None
