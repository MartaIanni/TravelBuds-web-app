from backend.orm.models import UserORM
from db.db import db
from backend.schemas.user import UserCreate #Per usare Pydantic per la validazione

class UsersDAO:

    @staticmethod
    def get_user_by_id(user_id: int):
        #Recupera un utente dal DB tramite username
        return db.session.query(UserORM).filter_by(uid=user_id).first()

    @staticmethod
    def get_user_by_username(username: str):
        #Recupera un utente dal DB tramite username
        return db.session.query(UserORM).filter_by(username=username).first()

    #Creazione nuovo utente e salvataggio nel db
    @staticmethod
    def add_user(user_data: dict):
        
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
        finally:
            db.session.close()
