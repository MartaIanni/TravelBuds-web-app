# 📜 CHANGELOG

Tutti i cambiamenti rilevanti del progetto sono documentati in questo file.
Il formato segue le convenzioni di [Keep a Changelog](https://keepachangelog.com/it-IT/1.1.0/)
e il versionamento semantico [SemVer](https://semver.org/lang/it/).

---

## [Non rilasciato]

> Modifiche attualmente in sviluppo non ancora incluse in una release ufficiale.

> Bug conosciuti:
>
> - Il pulsante “Rispondi” del coordinatore blocca la pagina dopo l’invio della domanda.

### 🔧 Aggiunto

- File CHANGELOG.md per tracciare le modifiche future.
- Inserimento dei file immagini, del db e della variabile d’ambiente per SECRET_KEY.
- Dependencies: inserimento di .gitignore e requirements.txt.

### 🧩 Modificato

- Pulizia della struttura del progetto.

### 🗑️ Rimosso

- Configurazioni hardcoded nel codice.

### 🐛 Corretto

- ***

## [1.0.0] — 2025-11-07

> Prima versione stabile di TravelBuds (Flask + SQLite).

### 🔧 Aggiunto

- Funzionalità di login e registrazione utente.
- Gestione viaggi e prenotazioni.
- Template HTML con interfaccia utente di base.
- Gestione immagini statiche e dei dati (utenti, viaggi).

### 🧩 Modificato

-

### 🗑️ Rimosso

-

### 🐛 Corretto

-
- In fase di revisione (bug non ancora risolti).

---

## Linee guida per mantenere il changelog

1. Ogni release **deve aggiungere** una sezione `[x.y.z] — AAAA-MM-GG`.
2. Classificare i cambiamenti in: `Aggiunto`, `Modificato`, `Rimosso`, `Corretto` (aggiungi eventualmente `Sicurezza`, `Documentazione`, `Build`, `CI`, `Test`).
3. Evitare voci poco informative (“varie modifiche”); ogni bullet deve essere chiaro e atomico.
4. Aggiornare il changelog **prima** di creare il tag Git della release.
5. Le modifiche non rilasciate restano nella sezione `[Non rilasciato]` e vengono spostate nella nuova versione al momento del tag.
