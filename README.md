# **TravelBuds-web-app**

Implementazione di un sito web base per **viaggi organizzati**, con una home su cui vengono pubblicate le singole proposte di viaggio che è possibile consultare e prenotare e un profilo utente dove si ha un riepilogo delle prenotazioni e delle domande poste ai coordinatori.

Esempio di **login**:

Username: giuliogorcia

PW: giulio_gorcia

## Avvio

- Aprire il terminale nella **directory del progetto**.
- Creare un **ambiente virtuale** e attivarlo tramite le seguenti istruzioni:

  `python3 -m venv venv`

  `. venv/bin/activate`

- Installare le **dipendenze**:

  `pip install flask flask-login flask-session werkzeug pydantic flask-sqlalchemy`

- Verifica se **Flask** funziona correttamente tramite l'interprete Python:

  `python`

  `import flask`

  Se quest'ultima istruzione non riporta risultati è stato installato correttamente.
  Uscire dall'interprete:

  `exit()`

- **Avvio** del server:

  `python main_app.py`

- **Avvio** del server con Nodemon:

  `nodemon --exec python main_app.py`

## Stop

- Fermare l'esecuzione del server:

  `control + C`
