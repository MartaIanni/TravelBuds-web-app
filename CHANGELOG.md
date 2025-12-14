# 📜 CHANGELOG

## [Non rilasciato]

> Bug conosciuti:
>
> - (RISOLTO) Il pulsante “Rispondi” del coordinatore blocca la pagina dopo l’invio della domanda.

### 🔧 Aggiunto

- File CHANGELOG.md per tracciare le modifiche future.
- Inserimento dei file immagini, del db e della variabile d’ambiente per SECRET_KEY.
- Dependencies: inserimento di .gitignore e requirements.txt.
- Pydantic: inserimento di validations.py
- SQLAlchemy: package app/ con suddivisione nei packages domain/, orm/ e schemas/. File see_bd.py per generazione db iniziale.
- Docker: Dockerfile e docker-compose.yaml per creazione image per development.
- JWT Authentication: implementazione autenticazione lato client (main_app.py).

### 🧩 Modificato

- Pulizia della struttura del progetto.
- Pydantic: costruzione dei modelli (models.py) e separazione delle validazioni (validation.py) senza l'utilizzo di ORM (SQLAlchemy)
- SQLAlchemy: conversione con i modelli ORM dei file in app/domain, app/orm, app/schemas, dei templates/ e di main_app.py.
- JWT Authentication: modifica di main_app.py per implementare autenticazione con token lato client.
- React + Tailwind: conversione del frontend dal rendering di template HTML a pagine con React e Tailwind.

### 🗑️ Rimosso

- Configurazioni hardcoded nel codice.

## [1.0.0] — 2025-11-07

> Prima versione stabile di TravelBuds (Flask + SQLite).

### 🔧 Aggiunto

- Funzionalità di login e registrazione utente.
- Gestione viaggi e prenotazioni.
- Template HTML con interfaccia utente di base.
- Gestione immagini statiche e dei dati (utenti, viaggi).

### 🐛 Corretto

- In fase di revisione (bug non ancora risolti).
