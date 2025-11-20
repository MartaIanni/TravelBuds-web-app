from pydantic import BaseModel, ConfigDict

class BookingBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    card_img_path: str
    user_id: int
    trip_id: int
    
class BookingCreate(BookingBase):
    pass

class BookingRead(BookingBase):
    model_config = ConfigDict(from_attributes=True)
    bid: int