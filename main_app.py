
from flask import Flask, render_template, request, redirect, url_for, flash, g, jsonify

#Check se password inserita e' corretta
from werkzeug.security import generate_password_hash, check_password_hash
from pydantic import ValidationError
from datetime import datetime, date
#Import per env vars
import os

#Models.py
from app.orm.models import UserORM, TripORM, BookingORM, QuestORM, Base
from app.schemas.trip import TripUpdate, TripCreate
from app.schemas.user import UserCreate

#DAO import:
from app.dao.trips_dao import TripsDAO
from app.dao.users_dao import UsersDAO
from app.dao.quests_dao import QuestsDAO
from app.dao.bookings_dao import BookingsDAO

#SQLAlchemy
from db.db import db 

#config.py:
from app.config import Config

#JWT
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies,
    jwt_required,
    verify_jwt_in_request, 
    get_jwt_identity,
    get_jwt
)
from flask_jwt_extended.exceptions import NoAuthorizationError
from functools import wraps


app = Flask(__name__)

#Sostituzione con config.py:
  # basedir = os.path.abspath(os.path.dirname(__file__))
  # db_path = os.path.join(basedir, 'db', 'site.db')
  # app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
  # app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
  # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object(Config)

jwt = JWTManager(app)

#Inizializzazione SQLAlchemy con l'app Flask (collega db all'app Flask)
db.init_app(app)
#Creazione tabelle nel database se non esistono
with app.app_context():
    Base.metadata.create_all(db.engine)

#debug
import logging
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

def validate_and_save_trip(form_data):
    try:
        trip_id = form_data.get('tid')
        if not trip_id:
          check_trip = TripCreate(**form_data)
          new_trip = check_trip.model_dump() 
          created_trip = TripsDAO.add_trip(new_trip)
          if not created_trip:
            flash("Errore nella creazione del viaggio.")
            return False
          return True
        else:
          is_trip_saved = TripsDAO.get_trip_by_id(trip_id)
          if is_trip_saved:
            check_trip_update = TripUpdate(**form_data)
            updates = check_trip_update.model_dump(exclude_unset=True)
            updated_trip = TripsDAO.update_trip(trip_id, updates)
            if not updated_trip:
              flash("Errore nel salvataggio del viaggio.")
              return False
            return True
          else:
              flash("Viaggio non trovato.")
              return False
    except ValidationError as e:
        for err in e.errors():
            msg = err.get('msg', '')
            msg = msg.replace("Value error,", "").strip()
            flash(msg)
        return False
    
def save_uploaded_images(form_data, card, bg, old_card=None , old_bg=None ):
    if card and card.filename:
        card_path = os.path.join(app.root_path, 'static', card.filename)
        card.save(card_path)
        form_data['card_img_path'] = '/static/' + card.filename
    else:
       form_data['card_img_path'] = old_card or ''
    if bg and bg.filename:
        bg_path = os.path.join(app.root_path, 'static', bg.filename)
        bg.save(bg_path)
        form_data['bg_img_path'] = '/static/' + bg.filename
    else:
        form_data['bg_img_path'] = old_bg or ''
    return form_data

def clean_numeric_fields(data: dict, numeric_fields: list):
    for field in numeric_fields:
        if data.get(field) == "":
            data[field] = None
    return data


def jwt_identity_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        identity = get_jwt_identity()
        return fn(identity, *args, **kwargs)
    return wrapper

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

#Error handlers:
@jwt.unauthorized_loader
def handle_unauthorized_callback(error):
    #token mancante o non valido
    flash("Devi autenticarti per accedere a questa pagina.")
    return redirect(url_for('home'))

@jwt.invalid_token_loader
def handle_invalid_token(error):
    flash("Token non valido. Accedi di nuovo.")
    return redirect(url_for('home'))

@jwt.expired_token_loader
def handle_expired_token(jwt_header, jwt_payload):
    flash("La sessione è scaduta. Effettua di nuovo l’accesso.")
    return redirect(url_for('home'))


@app.route('/')
def home():
  return render_template('login.html')

@app.route('/admin_home/<username>')
@jwt_required()
def admin_home(username):
    p_trips = TripsDAO.get_username_public_trips(username)
    d_trips = TripsDAO.get_draft_trips()
    quests = QuestsDAO.get_c_quests(username)
    return render_template('admin_home.html', p_trips=p_trips, d_trips=d_trips, quests=quests)

@app.route('/user_home')
@jwt_required()
#X
#username non utilizzato
def user_home():
  trips = TripsDAO.get_public_trips()
  return render_template('user_home.html', trips=trips)

@app.route('/user_profile/<username>')
@jwt_required()
def user_profile(username):
  booked_trips=BookingsDAO.get_booked_trips(username)
  quests=QuestsDAO.get_u_quests(username)
  user=UsersDAO.get_user_by_username(username)
  return render_template('user_profile.html', b_trips=booked_trips, quests=quests, user=user)

@app.route('/trip/<int:id>')
@jwt_required()
def trip(id):
    trip = TripsDAO.get_trip_by_id(id)
    return render_template('trip.html', trip=trip)

@app.route('/newtrip_validation', methods=['POST'])
@jwt_identity_required
def newtrip(identity):
    claims = get_jwt()
    form_data_newtrip = request.form.to_dict()

    #Recupero dei file immagini
    card = request.files.get('card_img_path')
    bg = request.files.get('bg_img_path')

    #Controllo se esistono immagini card e bg, salvataggio in /static e modifica path per memorizzarlo sul db:
    form_data_newtrip = save_uploaded_images(form_data_newtrip, card, bg)

    #Controllo presenza info coordinatore dal form
    c_username = claims.get('username')
    
    #Recupero del coordinatore dal db tramite lo username
    coord_orm = UsersDAO.get_user_by_username(c_username)
    if not coord_orm:
       flash(f"Errore: coordinatore {c_username} non trovato!")
       return redirect(url_for('admin_home', username = claims.get('username')))
    form_data_newtrip['coord_id'] = coord_orm.uid

    form_data_newtrip['transport_price'] = int(form_data_newtrip.get('transport_price') or 0)
    form_data_newtrip['stay_price'] = int(form_data_newtrip.get('stay_price') or 0)
    form_data_newtrip['act_price'] = int(form_data_newtrip.get('act_price') or 0)
    form_data_newtrip['start'] = datetime.strptime(form_data_newtrip['start'], "%Y-%m-%d").strftime("%d/%m/%Y")
    form_data_newtrip['end'] = datetime.strptime(form_data_newtrip['end'], "%Y-%m-%d").strftime("%d/%m/%Y")

    #Validazione e salvataggio del viaggio:
    if validate_and_save_trip(form_data_newtrip):
        flash("Nuovo viaggio caricato con successo!")
    return redirect(url_for('admin_home', username=claims.get('username')))


@app.route('/draft_validation', methods=['POST'])
@jwt_identity_required
def draft_validation(identity):
    claims = get_jwt()
    form_data_draft = request.form.to_dict()
    action = form_data_draft.pop("action", None)

    #Recupero dei file immagini
    card = request.files.get('card_img_path')
    bg = request.files.get('bg_img_path')
    
    #Creazione modello User da inserire in form_data
    a_user = UsersDAO.get_user_by_username(claims.get('username'))
    if not a_user:
       flash("Coordinatore corrente non trovato.")
       return redirect(url_for('admin_home', username=claims.get('username')))
    form_data_draft['coord_id'] = a_user.uid

    #Controllo la presenza del viaggio nel db:
    d_tripcode = int(form_data_draft.get("tid"))

    if d_tripcode:
      draft_orm = TripsDAO.get_trip_by_id(d_tripcode)
      if not draft_orm:
        flash(f"Errore: viaggio con codice {d_tripcode} non trovato.")
        return redirect(url_for('admin_home', username = claims.get('username')))
  
    old_card=draft_orm.card_img_path
    old_bg=draft_orm.bg_img_path
    #Controllo se esistono immagini card e bg, salvataggio in /static e modifica path per memorizzarlo sul db:
    form_data_draft = save_uploaded_images(form_data_draft, card, bg, old_card, old_bg)

    form_data_draft['transport_price'] = int(form_data_draft.get('transport_price') or 0)
    form_data_draft['stay_price'] = int(form_data_draft.get('stay_price') or 0)
    form_data_draft['act_price'] = int(form_data_draft.get('act_price') or 0)
    form_data_draft['start'] = datetime.strptime(form_data_draft['start'], "%Y-%m-%d").strftime("%d/%m/%Y")
    form_data_draft['end'] = datetime.strptime(form_data_draft['end'], "%Y-%m-%d").strftime("%d/%m/%Y")
    
    #Validazione e salvataggio del viaggio
    if not validate_and_save_trip(form_data_draft):
        flash("Ops, la bozza non è stata salvata! Riprova.")
        return redirect(url_for('admin_home', username=claims.get('username')))

    #Se click su bottone 'Pubblica':
    if action == 'post':
      required_fields = [
            'destination', 
            'start', 
            'end', 
            'description', 
            'transport_price',
            'stay_price', 
            'act_price', 
            'subtitle', 
            'tour',
            'card_img_path', 
            'bg_img_path', 
            'tid'
        ]
    #Controllo che tutti i campi siano stati compilati
      for key in required_fields:
        if not form_data_draft.get(key):
          flash(f"Campo mancante: {key}. Completa tutti i campi del viaggio per pubblicare!")
          return redirect(url_for('admin_home', username=claims.get('username')))
    #Salvataggio del viaggio nel db
      res = TripsDAO.public_trip(d_tripcode)

      if not res:
        flash("Ops, pubblicazione del viaggio non riuscita! Riprova.")
      else:
            flash("Viaggio pubblicato con successo!")
    else:
        flash("Bozza salvata con successo!")
    return redirect(url_for('admin_home', username=claims.get('username')))


@app.route('/delete_validation', methods=['POST'])
@jwt_identity_required
def del_trip(identity):
    claims = get_jwt()
    tripcode = int(request.form.get("tid"))

    #Controllo presenza del viaggio da cancellare nel db
    if not TripsDAO.get_trip_by_id(tripcode) or not tripcode:
      flash(f"Errore: viaggio con codice {tripcode} non trovato.")
      return redirect(url_for('admin_home', username = claims.get('username')))

    #Eliminazione del viaggio
    res = TripsDAO.delete_trip(tripcode)
    if res:
        flash("Viaggio eliminato con successo!", "success")
    else:
        flash("Errore nell'eliminazione del viaggio.", "danger")
    return redirect(url_for('admin_home', username=claims.get('username')))

@app.route('/booking', methods=['POST'])
@jwt_identity_required
def booking(identity):
  claims = get_jwt()
  book_data = request.form.to_dict()
  tripcode = book_data.get('tid')
  trip = TripsDAO.get_trip_by_id(tripcode)
  if not tripcode:
        flash("Viaggio non trovato.")
        return redirect(url_for('user_home', username=claims.get('username')))
  #Controllo se gia' presente tra le prenotazioni dell'utente:
  user_id = int(identity)
  if BookingsDAO.check_is_booked(user_id, trip.tid):
        flash("Il viaggio è già stato prenotato!")
        return redirect(url_for('user_home', username=claims.get('username')))

  mybookings = BookingsDAO.get_booked_trips(claims.get('username'))

  trip_start = datetime.strptime(trip.start, "%d/%m/%Y").date()
  trip_end = datetime.strptime(trip.end, "%d/%m/%Y").date()

  for booking in mybookings:
    booking_trip = booking.trip
    test_start = datetime.strptime(booking_trip.start, "%d/%m/%Y").date()
    test_end = datetime.strptime(booking_trip.end, "%d/%m/%Y").date()

    if (trip_start <= test_end and trip_end >= test_start):
      flash("Le date del viaggio si sovrappongono con una prenotazione esistente!")
      return redirect(url_for('user_home', username=claims.get('username')))

  today = date.today()

  if trip_start < today:
      flash("Siamo già partiti! La prossima volta sarai dei nostri!")
      return redirect(url_for('user_home', username=claims.get('username')))

  if trip.free_seats == 0:
      flash("Siamo al completo! La prossima volta sarai dei nostri!")
      return redirect(url_for('user_home', username=claims.get('username')))

  free_seats = trip.free_seats - 1
  seats=TripsDAO.update_seats(trip.tid, free_seats)
  book_load = {
     'user_id': user_id,
     'trip_id': trip.tid,
     'card_img_path': book_data.get('card_img_path', '')
  }
  res=BookingsDAO.add_booking(book_load)

  if res and seats :
    flash("Prenotazione completata con successo!")
  else:
    flash('Ops qualcosa è andato storto! Riprova')

  return redirect(url_for('user_home', username=claims.get('username')))

@app.route('/admin_answer_validation', methods=['POST'])
@jwt_identity_required
def answer_validation(identity):
    claims = get_jwt()
    ans_info = request.form.to_dict()
    quest_id = ans_info.get('quest_id')
    answer = ans_info.get('answer')
    #Aggiunge la risposta alla quest
    success = QuestsDAO.add_answer(quest_id , answer)

    if success:
      flash("Risposta caricata!")
    else:
      flash("Ci sono stati problemi nel caricamento della tua risposta! Riprova.")
    return redirect(url_for('admin_home', username=claims.get('username')))

@app.route('/questbox', methods=['POST'])
@jwt_identity_required
def u_quest(identity):
    claims = get_jwt()
    quest_info = request.form.to_dict()

    #Controllo sullo username inserito:
    u_user = UsersDAO.get_user_by_username(quest_info['username'])
    if not u_user:
      flash(f"L'username {quest_info['username']} non esiste! Riprova")
      return redirect(url_for('user_home', username=claims.get('username')))

    quest_info['user_id'] = u_user.uid

    success = QuestsDAO.add_quest(quest_info)
    if success:
      flash("Domanda inviata!")
    else:
      flash("Ci sono stati problemi nel caricamento della tua domanda! Riprova.")

    tripcode = quest_info.get('trip_id')
    trip_obj = TripsDAO.get_trip_by_id(tripcode)
    return redirect(url_for('trip', id=trip_obj.tid))


@app.route('/user_login', methods=['POST'])
def user_login():
    user_data = request.form.to_dict()

    #debug:
    logging.debug("Login attempt: %s", user_data)

    #Controllo che user sia registrato:
    user_db = UsersDAO.get_user_by_username(user_data.get('username'))
    if not user_db:
        
        #debug:
        logging.debug("User not found")

        flash("Username non trovato. Controlla e riprova.")
        return redirect(url_for('home'))

    #Controllo se la password inserita e' corretta:
    if not check_password_hash(user_db.password, user_data.get('password')):
        
        #debug:
        logging.debug("Password errata")

        flash("Password errata. Riprova.")
        return redirect(url_for('home'))

    #Autenticazione:
    #Creazione del JWT token con le info in identity per l'utente:
    identity = str(user_db.uid)
    additional_claims = {
       "username": user_db.username, 
       "is_coordinator": user_db.is_coordinator
    }
    access_token = create_access_token(identity=identity, additional_claims=additional_claims)
    refresh_token = create_refresh_token(identity=identity, additional_claims=additional_claims)

    #debug:
    logging.debug("JWT creati. Access: %s", access_token)

    #Prepara la response che reindirizza l'utente (coord o meno) e setta cookie
    if user_db.is_coordinator:
        target = url_for('admin_home', username=additional_claims.get('username'))
    else:
        target = url_for('user_home', username=additional_claims.get('username'))

    resp = redirect(target)
    #Setta cookie (anche con CSRF: flask-jwt-extended gestisce)
    set_access_cookies(resp, access_token)
    set_refresh_cookies(resp, refresh_token)

    #debug:
    logging.debug("Cookie settati nella response: %s", resp.headers)

    return resp

@app.route('/signup', methods=['POST'])
def signup():
  #Conversione dati form in dizionario python
  newuser_data = request.form.to_dict()
  #Recupero User e verifica se gia' registrato
  user = UsersDAO.get_user_by_username(newuser_data.get('username'))
  if user:
    flash('Username già utilizzato.')
    return redirect(url_for('home'))

  #Inserimento img profilo a seconda del gender
  if newuser_data.get('gender') == 'M':
     newuser_data['gender'] = '/static/man.jpg'
  else:
     newuser_data['gender'] = '/static/woman.jpg'

  #Conversione da formato datetime in formato stringa
  newuser_data['birthdate'] = datetime.strptime(newuser_data['birthdate'], "%Y-%m-%d").strftime("%d/%m/%Y")
  
  #Hashing della password
  newuser_data['password'] = generate_password_hash(newuser_data.get('password'))

  #Controllo presenza campi primari:
  try:
     check_user = UserCreate(**newuser_data)
  except ValidationError as e:
     for err in e.errors():
        field = err.get('loc')[0]   # il nome del campo
        msg = err.get('msg', '')
        # pulizia messaggio: toglie "Value error," e spazi
        clean_msg = msg.replace("Value error,", "").strip()
        flash(f"Errore nel campo '{field}': {clean_msg}")
     return redirect(url_for('home'))

  #Prova di inserimento del nuovo User nel db
  success = UsersDAO.add_user(check_user.model_dump())

  if success:
    flash('Iscrizione avvenuta con successo!')
  else:
    flash('Iscrizione non completata! Riprovare')
  return redirect(url_for('home'))


@app.route("/logout", methods=["POST","GET"])
def logout():
    resp = redirect(url_for('home'))
    #Rimozione dei cookies
    unset_jwt_cookies(resp)
    flash("Logout effettuato con successo.")
    return resp

#debug: per capire se il server vede il token e cosa succede quando cerca di leggerlo
@app.before_request
def log_jwt():
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        logging.debug("JWT identity: %s", identity)
    except Exception as e:
        logging.debug("JWT error: %s", e)

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000)