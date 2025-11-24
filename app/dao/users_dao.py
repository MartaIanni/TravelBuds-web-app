from app.orm.models import UserORM
from db.db import db
from app.schemas.user import UserCreate #Per usare Pydantic per la validazione

class UsersDAO:

    @staticmethod
    def get_user_by_id(user_id: int):
        #Recupera un utente dal DB tramite username
        return db.session.query(UserORM).filter_by(uid=user_id).first()
        #db.session: gestisce automaticamente commit, rollback e connessioni.

    @staticmethod
    def get_user_by_username(username: str):
        #Recupera un utente dal DB tramite username
        return db.session.query(UserORM).filter_by(username=username).first()
        #db.session: gestisce automaticamente commit, rollback e connessioni.

    #Creazione nuovo utente e salvataggio nel db
    @staticmethod
    def add_user(user_data: dict):
        #user_data può essere un dict (dal form) o uno schema Pydantic.
        
        try:
            #Validazione Pydantic:
            check_new_user = UserCreate(**user_data)
            #Conversione in dict
            new_user = check_new_user.model_dump()
            #Creazione ORM e salvataggio
            user_orm = UserORM(**new_user)
            db.session.add(user_orm)
            db.session.commit()
            return True
        except Exception as e:
            print("Error:", e)
            db.session.rollback()
            return False
