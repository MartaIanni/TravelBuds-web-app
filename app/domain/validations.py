"""
Funzioni di validazione/normalizzazione riusabili.
Nessuna dipendenza dai modelli per evitare cicli.
"""

#Check se password inserita e' corretta
from werkzeug.security import check_password_hash

from datetime import datetime

def validate_password(db_password: str, input_password: str) -> None:
    if not check_password_hash(db_password, input_password):
            raise ValueError("La password inserita non è corretta! Riprova.")

def validate_start_after_today(start_date: str) -> str:
    start = datetime.strptime(start_date, "%d/%m/%Y")
    if start.date() < datetime.today().date():
        raise ValueError("La data di inizio deve essere successiva a oggi.")
    return start_date

def validate_end_after_start(start_date: str, end_date: str) -> str:
    start = datetime.strptime(start_date, "%d/%m/%Y")
    end = datetime.strptime(end_date, "%d/%m/%Y")
    if end <= start:
        raise ValueError("La data di fine deve essere successiva a quella di inizio.")
    return end_date

#Toglie spazi se prima o dopo la stringa e controlla se e' una stringa
def clean_string(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("Deve essere una stringa")
    return value.strip()


