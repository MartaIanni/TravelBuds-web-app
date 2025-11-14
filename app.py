
from flask import Flask, render_template, request, redirect, url_for, flash

#importazione per l'autenticazione, le sessioni e per l'hashing
from flask_login import LoginManager, login_user, login_required, logout_user,current_user # type: ignore

from flask_session import Session # type: ignore
from werkzeug.security import generate_password_hash
from pydantic import ValidationError

import trips_dao, users_dao, quests_dao,bookings_dao
#Models.py
from models import User, Trip, UserRegistration
from datetime import datetime

#Import per env vars
import os

app = Flask(__name__)

# Variabili d'ambiente:
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
DB_PATH = os.environ.get('DB_PATH')
#Verifica funzionamento env vars:
#print("SECRET_KEY:", app.config['SECRET_KEY'])

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

    #Controllo se esistono immagini card e bg, salvataggio in /static e modifica path per 
    #memorizzarlo sul db
    # if card and card.filename != '':
    #   card.save('static/' + card.filename)
    #   form_data_newtrip['card_img_path'] = '/static/' + card.filename

    # if bg and bg.filename != '':
    #   bg.save('static/' + bg.filename)
    #   form_data_newtrip['bg_img_path'] = '/static/' + bg.filename

    form_data_newtrip = save_uploaded_images(form_data_newtrip,card,bg)

    #Controllo presenza info coordinatore dal form
    c_username = form_data_newtrip.get("username")
    # if not c_username:
    #    flash(f"Errore: coordinatore {c_username} inesistente!")
    #    return redirect(url_for('admin_home', username = current_user.username))
    
    #Recupero del coordinatore dal db tramite lo username
    coord_dict = users_dao.get_user_by_username(c_username)
    if not coord_dict:
       flash(f"Errore: coordinatore {c_username} non trovato!")
       return redirect(url_for('admin_home', username = current_user.username))
    #trasformo le info di coord da dict a model User
    coord_model= User(**coord_dict)

    #Conversione dei campi:
    #  try:
    #     newtrip['seats'] = int(newtrip['seats'])
    #     newtrip['public'] = int(newtrip['public'])
    #     newtrip['free_seats'] = int(newtrip['seats'])
    # except ValueError:
    #     flash("Errore di memorizzazione per: seats, public o free_seats.")
    #     return redirect(url_for('admin_home', username=newtrip['a_username']))

#CONTROLLI VARI (sostituiti con pydantic):

    for field in ['seats', 'transport_price', 'stay_price', 'act_price', 'free_seats']:
      if not form_data_newtrip.get(field):
          form_data_newtrip[field] = 0

    # try:
    #    form_data_newtrip['seats'] = int(form_data_newtrip.get('seats',0))
    #    form_data_newtrip['transport_price'] = int(form_data_newtrip.get('transport_price',0))
    #    form_data_newtrip['stay_price'] = int(form_data_newtrip.get('stay_price',0))
    #    form_data_newtrip['act_price'] = int(form_data_newtrip.get('act_price',0))
    #   #  form_data_newtrip['price'] = int(form_data_newtrip.get('price',0))
    #    form_data_newtrip['free_seats'] = int(form_data_newtrip.get('free_seats',0))
    #   #  form_data_newtrip['tripcode'] = int(form_data_newtrip.get('tripcode',0))
    # except ValueError:
    #    flash("Errore nei valori numerici durante la conversione.")
    #    return redirect(url_for('admin_home', username=c_username))
    
    #Aggiungo il modello coordinatore al dict form_data_newtrip
    form_data_newtrip['coordinator'] = coord_model


    # for key in ['destination', 'start', 'end', 'description', 'transport_price',
    #         'stay_price', 'act_price', 'subtitle', 'price', 'tour', 'card_img',
    #         'bg_img', 'nights', 'username']:
    #     if key not in newtrip or newtrip[key] == '':
    #       newtrip[key] = None

    # newtrip['start'] = datetime.strptime(newtrip['start'], "%Y-%m-%d")
    # newtrip['end'] = datetime.strptime(newtrip['end'], "%Y-%m-%d")

    # today = datetime.today()

  #Controllo se data start e' successiva a quella odierna:
  #Validazione pydantic ok manca invio risultato per messaggio flash
    # if newtrip['start'] < today:
    #     flash("Inserisci una data di partenza successiva a quella odierna, grazie!")
    #     return redirect(url_for('admin_home', username=newtrip['a_username']))

  #Controllo se data di end successiva a data di start:
  #Validazione pydantic ok manca invio risultato per messaggio flash
    # newtrip['start'] = newtrip['start'].strftime("%d/%m/%Y")
    # newtrip['end'] = newtrip['end'].strftime("%d/%m/%Y")

    # format = "%d/%m/%Y"
    # try:
    #     start = datetime.strptime(newtrip['start'], format)
    #     end = datetime.strptime(newtrip['end'], format)

    #     if start >= end:
    #         flash("Errore: la data di ritorno deve essere successiva alla partenza.")
    #         return redirect(url_for('admin_home', username=newtrip['a_username']))

      #Calcolo delle notti tramite le due date start end:
      #Pydantic computed field ok
    #     newtrip['nights'] = (end - start).days
    # except ValueError:
    #     flash("Errore: formato data non valido. Usa 'dd/mm/yy'.")
    #     return redirect(url_for('admin_home', username=newtrip['a_username']))

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

  #Controllo se esistono immagini card e bg, salvataggio in /static e modifica path per 
  #memorizzarlo sul db
    if card and card.filename != '':
      card.save('static/' + card.filename)
      form_data_draft['card_img_path'] = '/static/' + card.filename

    if bg and bg.filename != '':
      bg.save('static/' + bg.filename)
      form_data_draft['bg_img_path'] = '/static/' + bg.filename

#CONTROLLI VARI: sostituiti con Pydantic

  # #Riempimento dei campi non compilati nel form con None
  #   for key in required_fields:
  #       if key not in form_data_draft or form_data_draft[key] == '':
  #         form_data_draft[key] = None

    # try:
    #     #Conversione dei valori dal form da number -> int
    #     form_data_draft['seats'] = int(form_data_draft['seats'])
    #     form_data_draft['free_seats'] = int(form_data_draft['seats'])
    # except ValueError:
    #     flash("Errore di memorizzazione per: seats, public o free_seats.")
    #     return redirect(url_for('admin_home', username=form_data_draft['a_username']))

    # format = "%d/%m/%Y"
    # try:
    #     #Controllo data ritorno successiva a quella di partenza
    #     form_data_draft['start'] = datetime.strptime(form_data_draft['start'], "%Y-%m-%d").strftime(format)
    #     form_data_draft['end'] = datetime.strptime(form_data_draft['end'], "%Y-%m-%d").strftime(format)

    #     start = datetime.strptime(form_data_draft['start'], format)
    #     end = datetime.strptime(form_data_draft['end'], format)

    #     if start >= end:
    #         flash("Errore: la data di ritorno deve essere successiva alla partenza.")
    #         return redirect(url_for('admin_home', username=form_data_draft['a_username']))
    #   #Calcolo delle notti con start e end
    #     form_data_draft['nights'] = (end - start).days
    # except ValueError:
    #     flash("Errore: formato data non valido. Usa 'dd/mm/yy'.")
    #     return redirect(url_for('admin_home', username=form_data_draft['a_username']))
    
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
            'destination', 'start', 'end', 'description', 'transport_price',
            'stay_price', 'act_price', 'subtitle', 'price', 'tour',
            'card_img_path', 'bg_img_path', 'tripcode'
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
    # username = request.form.get("username")

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
  # u_username = book_data['u_username']

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

    #user_data: contiene [username,password,db_password]
    #userd_db: contiene tutti i dati dello User

    #Controllo se la password inserita e' corretta
    user_data['db_password'] = user_db['password']
    UserRegistration(**user_data)

    # if not user_db or not check_password_hash(user_db['password'], user_data['password']):
    #     flash("Username o password errati!")
    #     return redirect(url_for('home'))
    # else:

    #Memorizzazione del nuovo field is_coordinator
    # if user_db['admin'] == 1: 
    #    user_data['is_coordinator'] = True
    # else: 
    #    user_data['is_coordinator'] = False

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
  #print(newuser_data)

  # #Controllo presenza campi primari:
  try:
     User(**newuser_data)
  except ValueError as e:
     flash(f"Errore nella validazione della registrazione: {e}")

  # if newuser_data ['name'] == '':
  #   flash('Completa tutti i campi per iscriverti')
  #   return redirect(url_for('home'))
  # if newuser_data ['surname'] == '':
  #   flash('Completa tutti i campi per iscriverti')
  #   return redirect(url_for('home'))
  # if newuser_data ['birthdate'] == '':
  #   flash('Completa tutti i campi per iscriverti')
  #   return redirect(url_for('home'))
  # if newuser_data ['gender'] == '':
  #   flash('Completa tutti i campi per iscriverti')
  #   return redirect(url_for('home'))
  # if newuser_data ['username'] == '':
  #   flash('Completa tutti i campi per iscriverti')
  #   return redirect(url_for('home'))
  # if newuser_data ['password'] == '':
  #   flash('Completa tutti i campi per iscriverti')
  #   return redirect(url_for('home'))

  #Conversione da formato datetime in formato stringa
  newuser_data['birthdate'] = datetime.strptime(newuser_data['birthdate'], "%Y-%m-%d").strftime("%d/%m/%Y")
  
  #Hashing della password
  newuser_data['password'] = generate_password_hash(newuser_data['password'])

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
