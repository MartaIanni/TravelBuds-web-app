
from flask import Flask, request, jsonify

#Check se password inserita e' corretta
from werkzeug.security import generate_password_hash, check_password_hash
from pydantic import ValidationError
from datetime import datetime, date
#Import per env vars
import os

#Models.py
from backend.orm.models import UserORM, TripORM, BookingORM, QuestORM, Base
from backend.schemas.trip import TripUpdate, TripCreate
from backend.schemas.user import UserCreate

#DAO import:
from backend.dao.trips_dao import TripsDAO
from backend.dao.users_dao import UsersDAO
from backend.dao.quests_dao import QuestsDAO
from backend.dao.bookings_dao import BookingsDAO

#SQLAlchemy
from db.db import db 

#config.py:
from backend.config import Config

#Lettura .env nella root
from dotenv import load_dotenv
load_dotenv()

#JWT
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    unset_jwt_cookies,
    jwt_required,
    verify_jwt_in_request, 
    get_jwt_identity,
    get_jwt
)
from flask_jwt_extended.exceptions import NoAuthorizationError
from functools import wraps

#Signal handler:
import signal

#Flask-cors: permette a React di chiamare Flask:
from flask_cors import CORS


app = Flask(__name__,)

app.config.from_object(Config)

#JWT autenticazione:
jwt = JWTManager(app)

#Inizializzazione SQLAlchemy con l'app Flask (collega db all'app Flask)
db.init_app(app)
#Creazione tabelle nel database se non esistono (DA TOGLIERE IN PRODUZIONE)
with app.app_context():
    Base.metadata.create_all(db.engine)

#debug
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

def validate_and_save_trip(form_data):
    try:
        trip_id = form_data.get('tid')
        if not trip_id:
          check_trip = TripCreate(**form_data)
          new_trip = check_trip.model_dump() 
          created_trip = TripsDAO.add_trip(new_trip)
          if not created_trip:
            return {"success": False, "msg": "Errore nella creazione del viaggio."}
          return {"success": True}
        else:
          is_trip_saved = TripsDAO.get_trip_by_id(trip_id)
          if is_trip_saved:
            check_trip_update = TripUpdate(**form_data)
            updates = check_trip_update.model_dump(exclude_unset=True)
            updated_trip = TripsDAO.update_trip(trip_id, updates)
            if not updated_trip:
              return {"success": False, "msg": "Errore nel salvataggio del viaggio."}
            return {"success": True}
          else:
              return {"success": False, "msg": "Viaggio non trovato."}
    except ValidationError as e:
        # estrai messaggi leggibili
        msgs = []
        for err in e.errors():
            msg = err.get('msg', '')
            msg = msg.replace("Value error,", "").strip()
            msgs.append(msg)
        return {"success": False, "msg": msgs}

def absolute_url(path):
    return request.host_url.rstrip("/") + path

def save_uploaded_images(form_data, card, bg, old_card=None , old_bg=None ):
    images_folder = os.path.join(app.root_path, 'static', 'images')

    if card and card.filename:
        card_path = os.path.join(images_folder, card.filename)
        card.save(card_path)
        # percorso da usare nel frontend
        form_data['card_img_path'] = f'/static/images/{card.filename}'
    else:
       form_data['card_img_path'] = old_card or '/static/images/no_image.jpg'
    if bg and bg.filename:
        bg_path = os.path.join(images_folder, bg.filename)
        bg.save(bg_path)
        form_data['bg_img_path'] = f'/static/images/{bg.filename}'
    else:
        form_data['bg_img_path'] = old_bg or '/static/images/no_image.jpg'
    return form_data

def jwt_identity_required(fn=None, *, locations=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request(locations=locations)
            identity = get_jwt_identity()
            return func(identity, *args, **kwargs)
        return wrapper

    if fn is None:
        return decorator
    else:
        return decorator(fn)

@app.context_processor
def inject_user():
    identity = None
    try:
        #prova a leggere il token e se valido recupera identity:
        verify_jwt_in_request()  
        identity = get_jwt_identity()
    except NoAuthorizationError:
        pass
    if identity:
        user_id = int(identity)
        user = UsersDAO.get_user_by_id(user_id)
        return {"current_user": user}
    return {"current_user": None}

#JWT error handlers:
@jwt.unauthorized_loader
def handle_unauthorized_callback(error):
    logging.debug("JWT unauthorized: %s", error)
    # token mancante o assente
    return jsonify({"msg": "Token mancante o scaduto", "code": "unauthorized"}), 401

@jwt.invalid_token_loader
def handle_invalid_token(error):
    logging.debug("JWT invalid token: %s", error)
    # token non valido
    return jsonify({"msg": "Token non valido", "code": "invalid"}), 422

@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):
    logging.debug("JWT expired: header=%s payload=%s", jwt_header, jwt_payload)
    # token scaduto
    return jsonify({"msg": "Token scaduto", "code": "expired"}), 401

#Flask CORS:
CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGIN']}}, supports_credentials=True)

@app.get("/")
def home():
    return jsonify({"msg": "API Running"})

@app.post("/api/login")
def api_login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    #recupero user
    user = UsersDAO.get_user_by_username(username)
    if not user or not check_password_hash(user.password, password):
        return jsonify({"msg": "Credenziali errate"}), 401

    access_token = create_access_token(identity=str(user.uid), additional_claims={"username": username, "is_coordinator": user.is_coordinator})

    return jsonify({"access_token": access_token})


@app.route("/api/me")
@jwt_required(locations=["headers"])
def api_me():

    claims = get_jwt()
    user = UsersDAO.get_user_by_username(claims.get('username'))

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "uid": user.uid,
        "username": user.username,
        "name": user.name,
        "gender": user.gender, 
        "is_coordinator": user.is_coordinator
    })

@app.route("/api/trips", methods=["GET"])
@jwt_required(locations=["headers"])
def api_get_trips():
    trips = TripsDAO.get_public_trips()
    trips_list = [
        {
            "tid": t.tid,
            "destination": t.destination,
            "nights": t.nights,
            "price": t.price,
            "card_img_path": absolute_url(t.card_img_path)
        }
        for t in trips
    ]
    return jsonify(trips_list)

@app.route('/api/trip/<int:id>')
@jwt_required(locations=["headers"])
def api_get_trip(id):
    trip = TripsDAO.get_trip_by_id(id)
    
    if not trip:
        return jsonify({"error": "Trip not found"}), 404
    
    trip_dict = {
            "tid": trip.tid,
            "destination": trip.destination,
            "description": trip.description,
            "subtitle": trip.subtitle,
            "tour": trip.tour,
            "start": trip.start,
            "end": trip.end,
            "free_seats": trip.free_seats,
            "transport_price": trip.transport_price,
            "stay_price": trip.stay_price,
            "act_price": trip.act_price,
            "nights": trip.nights,
            "price": trip.price,
            "card_img_path": absolute_url(trip.card_img_path),
            "bg_img_path": absolute_url(trip.bg_img_path),
            "coord_id": trip.coord_id,
            "coord_username": trip.coordinator.username,
            "participants": [u.username for u in trip.participants]
    }

    return jsonify(trip_dict)

@app.route("/api/user-profile")
@jwt_required(locations=["headers"])
def api_user_profile():
    claims = get_jwt()
    booked_trips = BookingsDAO.get_booked_trips(claims.get('username'))
    quests = QuestsDAO.get_u_quests(claims.get('username'))

    return jsonify({
        "trips": [
            {
                "tid": t.trip.tid,
                "destination": t.trip.destination,
                "card_img_path": absolute_url(t.trip.card_img_path)
            }
            for t in booked_trips
        ],
        "quests": [
            {
                "coord_username": q.coord.username,
                "destination": q.destination,
                "content": q.content,
                "answer": q.answer,
            }
            for q in quests
        ]
    })

@app.route("/api/coord-profile")
@jwt_required(locations=["headers"])
def api_coord_profile():
    claims = get_jwt()
    public_trips = TripsDAO.get_username_public_trips(claims.get('username'))
    draft_trips = TripsDAO.get_draft_trips()
    quests = QuestsDAO.get_c_quests(claims.get('username'))

    return jsonify({
        "p_trips": [ {
                "tid": trip.tid,
                "destination": trip.destination,
                "description": trip.description,
                "subtitle": trip.subtitle,
                "tour": trip.tour,
                "start": trip.start,
                "end": trip.end,
                "free_seats": trip.free_seats,
                "transport_price": trip.transport_price,
                "stay_price": trip.stay_price,
                "act_price": trip.act_price,
                "nights": trip.nights,
                "price": trip.price,
                "card_img_path": absolute_url(trip.card_img_path),
                "bg_img_path": absolute_url(trip.bg_img_path),
                "coord_id": trip.coord_id,
                "coord_username": trip.coordinator.username,
                "participants": [u.username for u in trip.participants]
        } for trip in public_trips ],
        "d_trips": [ {
                "tid": trip.tid,
                "destination": trip.destination,
                "description": trip.description,
                "subtitle": trip.subtitle,
                "tour": trip.tour,
                "start": trip.start,
                "end": trip.end,
                "free_seats": trip.free_seats,
                "transport_price": trip.transport_price,
                "stay_price": trip.stay_price,
                "act_price": trip.act_price,
                "nights": trip.nights,
                "price": trip.price,
                "card_img_path": absolute_url(trip.card_img_path),
                "bg_img_path": absolute_url(trip.bg_img_path),
                "coord_id": trip.coord_id,
                "coord_username": trip.coordinator.username,
                "participants": [u.username for u in trip.participants]
        } for trip in draft_trips ],
        "quests": [
            {
                "quest_id": q.qid,
                "user_username": q.user.username,
                "destination": q.destination,
                "content": q.content,
                "answer": q.answer,
            }
            for q in quests
        ]
    })

@app.route('/api/booking', methods=['POST'])
@jwt_identity_required(locations=["headers"])
def booking(identity):
    claims = get_jwt()
    book_data = request.get_json(silent=True)
    tripcode = book_data.get('tid') if book_data else None

    if not tripcode:
        return jsonify({"success": False, "msg": "Viaggio non trovato"}), 404

    trip = TripsDAO.get_trip_by_id(tripcode)
    if not trip:
        return jsonify({"success": False, "msg": "Viaggio non trovato"}), 404

    user_id = int(identity)
    if BookingsDAO.check_is_booked(user_id, trip.tid):
        return jsonify({"success": False, "msg": "Il viaggio è già stato prenotato!"}), 400

    mybookings = BookingsDAO.get_booked_trips(claims.get('username'))
    trip_start = datetime.strptime(trip.start, "%d/%m/%Y").date()
    trip_end = datetime.strptime(trip.end, "%d/%m/%Y").date()

    for booking in mybookings:
        booking_trip = booking.trip
        test_start = datetime.strptime(booking_trip.start, "%d/%m/%Y").date()
        test_end = datetime.strptime(booking_trip.end, "%d/%m/%Y").date()
        if (trip_start <= test_end and trip_end >= test_start):
            return jsonify({"success": False, "msg": "Le date del viaggio si sovrappongono con una prenotazione esistente!"}), 400

    if trip_start < date.today():
        return jsonify({"success": False, "msg": "Siamo già partiti! La prossima volta sarai dei nostri!"}), 400

    if trip.free_seats == 0:
        return jsonify({"success": False, "msg": "Siamo al completo! La prossima volta sarai dei nostri!"}), 400

    free_seats = trip.free_seats - 1
    seats = TripsDAO.update_seats(trip.tid, free_seats)
    book_load = {
        'user_id': user_id,
        'trip_id': trip.tid,
        'card_img_path': book_data.get('card_img_path', '')
    }
    res = BookingsDAO.add_booking(book_load)

    if res and seats:
        return jsonify({"success": True, "msg": "Prenotazione completata con successo!"}), 200
    else:
        return jsonify({"success": False, "msg": "Ops qualcosa è andato storto! Riprova"}), 500
    

@app.route('/api/questbox', methods=['POST'])
@jwt_identity_required(locations=["headers"])
def u_quest(identity):
    claims = get_jwt()
    quest_info = request.get_json(silent=True)

    if not quest_info or 'content' not in quest_info:
        return jsonify({"success": False, "msg": "Contenuto della domanda mancante"}), 400

    #Recupero coordinatore a cui è destinata la domanda tramite il viaggio
    tripcode = quest_info.get('trip_id')
    trip_obj = TripsDAO.get_trip_by_id(tripcode)
    if not trip_obj:
        return jsonify({"success": False, "msg": "Viaggio non trovato"}), 404

    u_user = trip_obj.coordinator  #coordinatore del viaggio
    quest_data = {
        "user_id": identity,
        "coord_id": u_user.uid,
        "trip_id": trip_obj.tid,
        "destination": trip_obj.destination,
        "content": quest_info['content'],
        "answer": None,
    }

    success = QuestsDAO.add_quest(quest_data)
    if success:
        return jsonify({"success": True, "msg": "Domanda inviata correttamente!"})
    else:
        return jsonify({"success": False, "msg": "Errore nell'invio della domanda"}), 500


@app.route('/api/newtrip_validation', methods=['POST'])
@jwt_identity_required(locations=["headers"])
def newtrip(identity):
    claims = get_jwt()
    form_data = request.form.to_dict()
    action = form_data.pop("action", "draft")  # default: salva bozza
    
    #Recupero dei file
    card = request.files.get('card_img_path')
    bg = request.files.get('bg_img_path')

    #Salvataggio immagini
    form_data = save_uploaded_images(form_data, card, bg)

    #Inserimento coord_id tra i dati
    coord = UsersDAO.get_user_by_username(claims.get("username"))
    if not coord:
        return jsonify({"success": False, "msg": "Coordinatore non trovato"}), 400

    form_data['coord_id'] = coord.uid

    #Conversioni
    form_data['transport_price'] = int(form_data.get('transport_price') or 0)
    form_data['stay_price'] = int(form_data.get('stay_price') or 0)
    form_data['act_price'] = int(form_data.get('act_price') or 0)

    form_data['start'] = datetime.strptime(form_data['start'], "%Y-%m-%d").strftime("%d/%m/%Y")
    form_data['end'] = datetime.strptime(form_data['end'], "%Y-%m-%d").strftime("%d/%m/%Y")

    #Salvataggio bozza
    trip_id = validate_and_save_trip(form_data)
    if not trip_id:
        return jsonify({"success": False, "msg": "Errore nel salvataggio della bozza"}), 400

    #Pubblicazione immediata
    if action == "post":
        if (
            form_data.get('card_img_path') == '/static/images/no_image.jpg' or
            form_data.get('bg_img_path') == '/static/images/no_image.jpg'
        ):
            return jsonify({"success": False, "msg": "Inserire un'immagine diversa da quella di default"}), 400
        
        ok = TripsDAO.public_trip(trip_id)
        if not ok:
            return jsonify({"success": False, "msg": "Errore nella pubblicazione del viaggio"}), 400
        return jsonify({"success": True, "msg": "Viaggio pubblicato!"})
    else:
        return jsonify({"success": True, "msg": "Bozza salvata con successo!"})

@app.route('/api/draft_validation', methods=['POST'])
@jwt_identity_required(locations=["headers"])
def draft_validation(identity):
    claims = get_jwt()

    form_data = request.form.to_dict()
    action = form_data.pop("action", "draft")

    # Recupero tid
    tid_d = form_data.get("tid")
    if not tid_d:
        return jsonify({"success": False, "msg": "tid mancante"}), 400

    d_tripcode = int(tid_d)

    # Recupero bozza dal DB
    draft = TripsDAO.get_trip_by_id(d_tripcode)
    if not draft:
        return jsonify({"success": False, "msg": "Bozza non trovata"}), 404

    # Files
    card = request.files.get('card_img_path')
    bg = request.files.get('bg_img_path')

    # Processa immagini preservando le precedenti se non aggiornate
    form_data = save_uploaded_images(
        form_data, 
        card, bg,
        old_card=draft.card_img_path,
        old_bg=draft.bg_img_path
    )

    # Conversioni
    form_data['transport_price'] = int(form_data.get('transport_price') or 0)
    form_data['stay_price'] = int(form_data.get('stay_price') or 0)
    form_data['act_price'] = int(form_data.get('act_price') or 0)

    form_data['start'] = datetime.strptime(form_data['start'], "%Y-%m-%d").strftime("%d/%m/%Y")
    form_data['end'] = datetime.strptime(form_data['end'], "%Y-%m-%d").strftime("%d/%m/%Y")

    # Salvataggio bozza aggiornata
    ok = validate_and_save_trip(form_data)
    if not ok:
        return jsonify({"success": False, "msg": "Errore nel salvataggio della bozza"}), 400

    # PUBBLICA
    if action == "post":
        # controllo immagine caricata nuova e non default no_image
        if (
            form_data.get('card_img_path') == '/static/images/no_image.jpg' or
            form_data.get('bg_img_path') == '/static/images/no_image.jpg'
        ):
            return jsonify({"success": False, "msg": "Inserire un'immagine diversa da quella di default"}), 400
        # controllo che tutti i campi esistano
        required = [
        "destination", "start", "end", "description",
        "transport_price", "stay_price", "act_price",
        "subtitle", "tour", "card_img_path", "bg_img_path"
        ]

        for key in required:
            if not form_data.get(key):
                return jsonify({"success": False, "msg": f"Manca: {key}"}), 400

        ok = TripsDAO.public_trip(d_tripcode)
        if not ok:
            return jsonify({"success": False, "msg": "Errore nella pubblicazione"}), 400

        return jsonify({"success": True, "msg": "Viaggio pubblicato!"})

    return jsonify({"success": True, "msg": "Bozza aggiornata!"})

@app.route('/api/delete_validation', methods=['POST'])
@jwt_identity_required(locations=["headers"])
def del_trip(identity):
    claims = get_jwt()
    tripcode = request.form.get("tid")

    # Controllo input
    if not tripcode:
        return jsonify({"success": False, "msg": "ID del viaggio mancante"}), 400

    try:
        tripcode = int(tripcode)
    except ValueError:
        return jsonify({"success": False, "msg": "ID del viaggio non valido"}), 400

    # Controllo presenza del viaggio nel DB
    if not TripsDAO.get_trip_by_id(tripcode):
        return jsonify({"success": False, "msg": f"Viaggio con codice {tripcode} non trovato"}), 404

    # Eliminazione del viaggio
    res = TripsDAO.delete_trip(tripcode)
    if res:
        return jsonify({"success": True, "msg": "Viaggio eliminato con successo!"})
    else:
        return jsonify({"success": False, "msg": "Errore nell'eliminazione del viaggio"}), 500

@app.route('/api/coord_answer_validation', methods=['POST'])
@jwt_identity_required(locations=["headers"])
def coord_answer_validation(identity):
    try:
        data = request.get_json(silent=True)
        quest_id = data.get('quest_id')
        answer = data.get('answer')

        if not quest_id or not answer:
            return jsonify({"success": False, "msg": "quest_id o answer mancanti"}), 400

        success = QuestsDAO.add_answer(quest_id, answer)
        if success:
            return jsonify({"success": True, "msg": "Risposta caricata!"})
        else:
            return jsonify({"success": False, "msg": "Problemi nel caricamento della risposta"}), 500
    except Exception as e:
        import traceback
        print("ERRORE completo:\n", traceback.format_exc())
        return jsonify({"success": False, "msg": str(e)}), 500

@app.route('/api/signup', methods=['POST'])
def signup():
    newuser_data = request.form.to_dict()

    #Check se username gia' utilizzato
    user = UsersDAO.get_user_by_username(newuser_data.get('username'))
    if user:
        return jsonify({"success": False, "message": "Username già utilizzato"}), 400

    #Inserisce immagine in base al gender
    newuser_data['gender'] = '/static/man.jpg' if newuser_data['gender'] == 'M' else '/static/woman.jpg'
    newuser_data['birthdate'] = datetime.strptime(newuser_data['birthdate'], "%Y-%m-%d").strftime("%d/%m/%Y")
    #Hashing della password
    newuser_data['password'] = generate_password_hash(newuser_data.get('password'))

    #Validazione dati tramite modelli
    try:
        check_user = UserCreate(**newuser_data)
    except ValidationError as e:
        return jsonify({"success": False, "errors": e.errors()}), 400

    #Aggiunge lo user
    success = UsersDAO.add_user(check_user.model_dump())

    if success:
        return jsonify({"success": True, "message": "Registrazione completata!"})
    else:
        return jsonify({"success": False, "message": "Errore nella registrazione"}), 500

@app.route("/api/logout", methods=["POST","GET"])
def logout():
    resp = jsonify({"success": True, "msg": "Logout effettuato con successo"})
    unset_jwt_cookies(resp)
    return resp

#Funzione chiamata quando si riceve SIGINT o SIGTERM per chiudere correttamente la sessione
#e l'engine SQLAlchemy.
def handle_shutdown_signal(signum, frame):
    logging.info("\nRicevuto segnale %s. Chiusura server...", signum)

    # Prova a chiudere la sessione solo se l'app context è attivo
    try:
        with app.app_context():
            try:
                db.session.remove()
                logging.info("Sessione DB rimossa correttamente.")
            except Exception as e:
                logging.exception("Errore durante rimozione sessione DB: %s", e)
    except RuntimeError:
        logging.warning("Nessun app context attivo, salto la chiusura DB.")
    finally:
        sys.exit(0)

#Collegamento della funzione ai segnali
signal.signal(signal.SIGINT, handle_shutdown_signal)
signal.signal(signal.SIGTERM, handle_shutdown_signal)

if __name__ == "__main__":
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "0") == "1"
    app.run(host=host, port=port, debug=debug)