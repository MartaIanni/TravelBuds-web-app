from pydantic import BaseModel, ConfigDict

class QuestBase(BaseModel):
    content: str
    answer: str | None = None
    destination: str
    user_id: int 
    coord_id: int
    trip_id: int

class QuestCreate(QuestBase):
    pass

class QuestUpdate(BaseModel):
    content: str 
    answer: str | None = None
    destination: str

class QuestRead(QuestBase):
    qid: int
#X  Da controllare
    coord_id: int
    user_id:int
