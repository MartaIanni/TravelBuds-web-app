import os
from datetime import timedelta

class Config:

    basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  
    DB_PATH = os.path.abspath(os.path.join(basedir, 'db', 'site.db')) 
    #Secret Key Flask
    SECRET_KEY = os.environ.get("SECRET_KEY")

    #Database: URI corretta per SQLite
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    #JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY") 
    JWT_TOKEN_LOCATION = ["cookies"]
    JWT_ACCESS_COOKIE_PATH = "/"
    JWT_REFRESH_COOKIE_PATH = "/token/refresh"
    JWT_COOKIE_SECURE = os.getenv("JWT_COOKIE_SECURE", "False").lower() == "true" 
    JWT_COOKIE_CSRF_PROTECT = os.getenv("JWT_COOKIE_CSRF_PROTECT", "False").lower() == "true"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    #CORS:
    CORS_ORIGIN = os.getenv("CORS_ORIGIN", "http://localhost:5173")