from app.orm.models import UserORM, QuestORM
from app.db.db import db
from app.schemas.quest import QuestCreate

class QuestsDAO:

    #Ritorno tutto le quests del viaggiatore
    @staticmethod
    def get_u_quests(username: str):
        user = db.session.query(UserORM).filter(UserORM.username == username).first()
        if not user:
            return []
        return user.quests_to
    
    #Ritorno tutto le quests al coordinatore
    @staticmethod
    def get_c_quests(username: str):
        user = db.session.query(UserORM).filter(UserORM.username == username).first()
        if not user:
            return []
        return user.quests_from

    @staticmethod
    def add_answer(quest_id: int, answer: str):
        quest = db.session.query(QuestORM).filter(QuestORM.qid == quest_id).first()
        if not quest:
            return False
        try:
            quest.answer = answer
            db.session.commit()
            return True
        except Exception as e:
            print("Errore nel caricamento della risposta:", e)
            db.session.rollback()
            return False
    
    @staticmethod
    def add_quest(quest_data: dict):
        try:
            check_new_quest = QuestCreate(**quest_data)
            new_quest = check_new_quest.model_dump()
            quest_orm = QuestORM(**new_quest)
            db.session.add(quest_orm)
            db.session.commit()
            return True
        except Exception as e:
            print("Errore sul caricamento della nuova domanda:", e)
            db.session.rollback()
            return False
