from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, name, surname, birthdate, gender, username, password, admin):
        self.name = name
        self.surname = surname
        self.birthdate = birthdate
        self.gender = gender
        self.username = username
        self.password = password
        self.admin = admin

    def get_id(self):
        return self.username
