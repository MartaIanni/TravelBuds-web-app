
from flask import Flask, render_template, request, redirect, url_for, flash

#importazione per l'autenticazione, le sessioni e per l'hashing
from flask_login import LoginManager, login_user, login_required, logout_user,current_user # type: ignore

from flask_session import Session # type: ignore
from werkzeug.security import generate_password_hash
from pydantic import ValidationError

import trips_dao, users_dao, quests_dao,bookings_dao

#Models.py
from app.orm.models import User, Trip, UserRegistration, Quest, Booking
from datetime import datetime

#SQLAlchemy
from flask_sqlalchemy import SQLAlchemy
from app import db

#Import per env vars
import os

app = Flask(__name__)

# Variabili d'ambiente:
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
DB_PATH = os.environ.get('DB_PATH')
#Verifica funzionamento env vars:
#print("SECRET_KEY:", app.config['SECRET_KEY'])

# URI corretta per SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

db = SQLAlchemy(app)
db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)

def validate_and_save_trip(form_data):
    try:
        trip = Trip(**form_data)
        saved_t = trips_dao.save_trip(trip.model_dump())
        if not saved_t:
            flash("Errore nel salvataggio del viaggio.")
            return False
        return True
    except ValidationError as e:
        flash(f"Errore di validazione: {e}")
        return False
    
def save_uploaded_images(form_data, card, bg):
    if card and card.filename != '':
        card.save('static/' + card.filename)
        form_data['card_img_path'] = '/static/' + card.filename
    if bg and bg.filename != '':
        bg.save('static/' + bg.filename)
        form_data['bg_img_path'] = '/static/' + bg.filename
    return form_data


@app.route('/')
def home():
  return render_template('login.html')

@app.route('/admin_home/<username>')
@login_required
def admin_home(username):

  p_trips=trips_dao.get_mypublic_trips(username)
  d_trips=trips_dao.get_draft_trips(username)
  quests=quests_dao.get_a_quests(username)

  for trip in p_trips:
     trip['participants'] = trips_dao.get_u_list(trip['tripcode'])

  return render_template('admin_home.html', p_trips=p_trips, d_trips=d_trips, quests=quests)

@app.route('/user_home/<username>')
@login_required
def user_home(username):
  #username di u
  trips = trips_dao.get_public_trips()
  return render_template('user_home.html', trips=trips)

@app.route('/user_profile/<username>')
@login_required
def user_profile(username):
  b_trips=bookings_dao.get_booked_trips(username)
  quests=quests_dao.get_u_quests(username)
  u=users_dao.get_user_by_username(username)

  return render_template('user_profile.html', b_trips=b_trips, quests=quests, user=u)

@app.route('/trip/<int:id>')
@login_required
def trip(id):
    #username di u
    trip = trips_dao.get_trip(id)
    return render_template('trip.html', trip=trip)

@app.route('/newtrip_validation', methods=['POST'])
@login_required
def newtrip():
    form_data_newtrip = request.form.to_dict()

    #Recupero dei file immagini
    card = request.files.get('card_img')
    bg = request.files.get('bg_img')

    #Controllo se esistono immagini card e bg, salvataggio in /static e modifica path per memorizzarlo sul db:
    form_data_newtrip = save_uploaded_images(form_data_newtrip,card,bg)

    #Controllo presenza info coordinatore dal form
    c_username = form_data_newtrip.get("username")
    
    #Recupero del coordinatore dal db tramite lo username
    coord_dict = users_dao.get_user_by_username(c_username)
    if not coord_dict:
       flash(f"Errore: coordinatore {c_username} non trovato!")
       return redirect(url_for('admin_home', username = current_user.username))
    #trasformo le info di coord da dict a model User
    coord_model= User(**coord_dict)

#CONTROLLI VARI (sostituiti con pydantic):

    for field in ['seats', 'transport_price', 'stay_price', 'act_price', 'free_seats']:
      if not form_data_newtrip.get(field):
          form_data_newtrip[field] = 0
    
    #Aggiungo il modello coordinatore al dict form_data_newtrip
    form_data_newtrip['coordinator'] = coord_model

    #Validazione e salvataggio del viaggio:
    if validate_and_save_trip(form_data_newtrip):
        flash("Nuovo viaggio caricato con successo!")
    else:
        flash("Ops, qualcosa è andato storto! Riprova.")
    return redirect(url_for('admin_home', username=c_username))


@app.route('/draft_validation', methods=['POST'])
@login_required
def draft_validation():
    
    action = request.form.get('action')
    form_data_draft = request.form.to_dict()

    #Recupero dei file immagini
    card = request.files.get('card_img')
    bg = request.files.get('bg_img')

  #Controllo se esistono immagini card e bg, salvataggio in /static e modifica path per memorizzarlo sul db:
    form_data_draft = save_uploaded_images(form_data_draft,card,bg)

#CONTROLLI VARI: sostituiti con Pydantic
    
    #Creazione modello User da inserire in form_data
    a_user = users_dao.get_user_by_username(current_user.username)
    form_data_draft['coordinator'] = a_user

    #Controllo la presenza del viaggio nel db:
    d_tripcode = form_data_draft.get("tripcode")
    draft_dict = trips_dao.get_trip(d_tripcode)
    if not draft_dict:
       flash(f"Errore: viaggio con codice {d_tripcode} non trovato.")
       return redirect(url_for('admin_home', username = current_user.username))
    
    #Validazione e salvataggio del viaggio
    if not validate_and_save_trip(form_data_draft):
        flash("Ops, la bozza non è stata salvata! Riprova.")
        return redirect(url_for('admin_home', username=current_user.username))

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
            'price', 
            'tour',
            'card_img_path', 
            'bg_img_path', 
            'tripcode'
        ]
    #Controllo che tutti i campi siano stati compilati
      for key in required_fields:
        if not form_data_draft[key]:
          flash(f"Campo mancante: {key}. Completa tutti i campi del viaggio per pubblicare!")
          return redirect(url_for('admin_home', username=current_user.username))
    #Salvataggio del viaggio nel db
      res = trips_dao.public_trip(form_data_draft['tripcode'])

      if not res:
        flash("Ops, pubblicazione del viaggio non riuscita! Riprova.")
      else:
            flash("Viaggio pubblicato con successo!")
    else:
        flash("Bozza salvata con successo!")
    return redirect(url_for('admin_home', username=current_user.username))


@app.route('/delete_validation', methods=['POST'])
@login_required
def del_trip():
    tripcode = request.form.get("tripcode")

    #Controllo presenza del viaggio da cancellare nel db
    if not trips_dao.get_trip(tripcode):
      flash(f"Errore: viaggio con codice {tripcode} non trovato.")
      return redirect(url_for('admin_home', username = current_user.username))

    #Eliminazione del viaggio
    res = trips_dao.delete_trip(tripcode)
    if res:
        flash("Viaggio eliminato con successo!", "success")
    else:
        flash("Errore nell'eliminazione del viaggio.", "danger")
    return redirect(url_for('admin_home', username=current_user.username))

@app.route('/booking', methods=['POST'])
@login_required
def booking():
  book_data = request.form.to_dict()

  #Controllo se gia' presente tra le prenotazioni dell'utente:
  isbooked = bookings_dao.get_if_booked(current_user.username, book_data['tripcode'])
  if isbooked:
      flash("Il viaggio è già stato prenotato!")
      return redirect(url_for('user_home', username=current_user.username))

  bookingtrip = trips_dao.get_trip(book_data['tripcode'])
  mybookings = bookings_dao.get_booked_trips(current_user.username)

  trip_start = datetime.strptime(bookingtrip['start'], "%d/%m/%Y")
  trip_end = datetime.strptime(bookingtrip['end'], "%d/%m/%Y")

  for booking in mybookings:
    booking_trip = trips_dao.get_trip(booking['tripcode'])
    test_start = datetime.strptime(booking_trip['start'], "%d/%m/%Y")
    test_end = datetime.strptime(booking_trip['end'], "%d/%m/%Y")

    if (trip_start <= test_end and trip_end >= test_start):
      flash("Le date del viaggio si sovrappongono con una prenotazione esistente!")
      return redirect(url_for('user_home', username=current_user.username))

  today = datetime.today()

  if trip_start < today:
      flash("Siamo già partiti! La prossima volta sarai dei nostri!")
      return redirect(url_for('user_home', username=current_user.username))

  if bookingtrip['free_seats'] == 0:
      flash("Siamo al completo! La prossima volta sarai dei nostri!")
      return redirect(url_for('user_home', username=current_user.username))

  free_seats = bookingtrip['free_seats'] - 1
  seats=trips_dao.update_seats(book_data['tripcode'],free_seats)
  res=bookings_dao.new_booking(book_data)

  if (res == True) and (seats == True) :
    flash("Prenotazione completata con successo!")
  else:
    flash('Ops qualcosa è andato storto! Riprova')

  return redirect(url_for('user_home', username=current_user.username))

@app.route('/admin_answer_validation', methods=['POST'])
@login_required
def answer_validation():
    ans_info = request.form.to_dict()

    #Aggiunge la risposta alla quest
    success = False
    success = quests_dao.add_answer(ans_info['questid'], ans_info['answer'])

    if success:
      flash("Risposta caricata!")
    else:
      flash("Ci sono stati problemi nel caricamento della tua risposta! Riprova.")
    return redirect(url_for('admin_home', username=ans_info['username']))

@app.route('/questbox', methods=['POST'])
@login_required
def u_quest():
    quest_info = request.form.to_dict()

    #Controllo sullo username inserito:
    u_user = users_dao.get_user_by_username(quest_info['u_username'])
    if not u_user:
      flash(f"L'username {quest_info['u_username']} non esiste! Riprova")
      return redirect(url_for('user_home', username=current_user.username))

    success = False
    success = quests_dao.add_quest(quest_info)

    if success:
      flash("Domanda inviata!")
    else:
      flash("Ci sono stati problemi nel caricamento della tua domanda! Riprova.")

    return redirect(url_for('trip', id=quest_info['tripcode']))


@app.route('/user_login', methods=['POST'])
def user_login():
    user_data = request.form.to_dict()

    #Controllo che ci sia lo user registrato:
    user_db = users_dao.get_user_by_username(user_data['username'])
    if not user_db:
        flash("Username non trovato. Controlla e riprova.")
        return redirect(url_for('home'))

    #Controllo se la password inserita e' corretta
    user_data['db_password'] = user_db['password']
    UserRegistration(**user_data)

    new_user = User(**user_db)

    #Autenticazione
    login_user(new_user, True)

    #Ridirezionamento pagina rispetto al tipo di utente
    if user_db.get('admin') == 1:
        return redirect(url_for('admin_home', username=user_data['username']))
    else:
        return redirect(url_for('user_home', username=user_data['username']))


@app.route('/signup', methods=['POST'])
def signup():
  #Conversione dati form in dizionario python
  newuser_data = request.form.to_dict()
  #Recupero User e verifica se gia' registrato
  user = users_dao.get_user_by_username(newuser_data.get('username'))
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
  newuser_data['password'] = generate_password_hash(newuser_data['password'])

  #Controllo presenza campi primari:
  try:
     User(**newuser_data)
  except ValueError as e:
     flash(f"Errore nella validazione della registrazione: {e}")

  #Prova di inserimento del nuovo User nel db
  success = users_dao.new_user(newuser_data)

  if success:
    flash('Iscrizione avvenuta con successo!')
  else:
    flash('Iscrizione non completata! Riprovare')
  return redirect(url_for('home'))

@login_manager.user_loader
def load_user(user_id):

    user_db = users_dao.get_user_by_username(user_id)

#X  Evita crash se utente non trovato
    if not user_db:   
        return None

    coord = user_db.get('admin', 0) == 1

    return User(
                name=user_db['name'],
                surname=user_db['surname'], 
                username=user_db['username'],
                password=user_db['password'], 
                birthdate=user_db['birthdate'], 
                gender=user_db['gender'], 
                is_coordinator=coord
              )

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout effettuato con successo.")
    return redirect(url_for('home'))
