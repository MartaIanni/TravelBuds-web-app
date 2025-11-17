from pydantic import BaseModel, ConfigDict

class QuestBase(BaseModel):
    model_config = ConfigDict(extra="forbid")
    content: str
    answer: str | None = None
    destination: str

class QuestCreate(QuestBase):
    pass

class QuestUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    content: str 
    answer: str | None = None
    destination: str

class QuestRead(QuestBase):
    model_config = ConfigDict(from_attributes=True)
    qid: int
#X  Da controllare
    coord_id: int
    user_id:int
