
from flask import Flask, render_template, request, redirect, url_for, flash

#importazione per l'autenticazione, le sessioni e per l'hashing
from flask_login import LoginManager, login_user, login_required, logout_user,current_user

from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash


import trips_dao, users_dao, quests_dao,bookings_dao
from models import User
from datetime import datetime

#Import per env vars
import os

app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
#Verifica funzionamento env var SECRET_KEY:
#print("SECRET_KEY:", app.config['SECRET_KEY'])

login_manager = LoginManager()
login_manager.init_app(app)

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
def newtrip():
    newtrip = request.form.to_dict()

    card = request.files.get('card_img')
    bg = request.files.get('bg_img')

    if card and card.filename != '':
      card.save('static/'+card.filename)
      newtrip['card_img'] = '/static/'+card.filename

    if bg and bg.filename != '':
      bg.save('static/'+bg.filename)
      newtrip['bg_img'] = '/static/'+bg.filename

    for key in ['destination', 'start', 'end', 'description', 'transport_price',
            'stay_price', 'act_price', 'subtitle', 'price', 'tour', 'card_img',
            'bg_img', 'nights', 'username']:
        if key not in newtrip or newtrip[key] == '':
          newtrip[key] = None

    try:
        newtrip['seats'] = int(newtrip['seats'])
        newtrip['public'] = int(newtrip['public'])
        newtrip['free_seats'] = int(newtrip['seats'])
    except ValueError:
        flash("Errore di memorizzazione per: seats, public o free_seats.")
        return redirect(url_for('admin_home', username=newtrip['a_username']))

    newtrip['start'] = datetime.strptime(newtrip['start'], "%Y-%m-%d")
    newtrip['end'] = datetime.strptime(newtrip['end'], "%Y-%m-%d")

    today = datetime.today()

    if newtrip['start'] < today:
        flash("Inserisci una data di partenza successiva a quella odierna, grazie!")
        return redirect(url_for('admin_home', username=newtrip['a_username']))

    newtrip['start'] = newtrip['start'].strftime("%d/%m/%Y")
    newtrip['end'] = newtrip['end'].strftime("%d/%m/%Y")

    format = "%d/%m/%Y"
    try:
        start = datetime.strptime(newtrip['start'], format)
        end = datetime.strptime(newtrip['end'], format)

        if start >= end:
            flash("Errore: la data di ritorno deve essere successiva alla partenza.")
            return redirect(url_for('admin_home', username=newtrip['a_username']))

        newtrip['nights'] = (end - start).days
    except ValueError:
        flash("Errore: formato data non valido. Usa 'dd/mm/yy'.")
        return redirect(url_for('admin_home', username=newtrip['a_username']))

    res = trips_dao.add_trip(newtrip)

    if res:
        flash("Nuovo viaggio caricato con successo!")
        return redirect(url_for('admin_home', username=newtrip['a_username']))

    flash("Ops, qualcosa è andato storto! Riprova.")
    return redirect(url_for('admin_home', username=newtrip['a_username']))


@app.route('/draft_validation', methods=['POST'])
def draft_validation():
    action = request.form.get('action')
    drafttrip = request.form.to_dict()

    card = request.files.get('card_img')
    bg = request.files.get('bg_img')

    if card and card.filename != '':
      card.save('static/'+card.filename)
      drafttrip['card_img'] = 'S345271_07-02-2025/static/'+card.filename

    if bg and bg.filename != '':
      bg.save('static/'+bg.filename)
      drafttrip['bg_img'] = 'S345271_07-02-2025/static/'+bg.filename

    required_fields = ['destination', 'start', 'end', 'description', 'transport_price',
                       'stay_price', 'act_price', 'subtitle', 'price', 'tour', 'card_img',
                       'bg_img', 'nights', 'a_username','tripcode']

    for key in required_fields:
        if key not in drafttrip or drafttrip[key] == '':
          drafttrip[key] = None

    try:
        drafttrip['seats'] = int(drafttrip['seats'])
        drafttrip['free_seats'] = int(drafttrip['seats'])
    except ValueError:
        flash("Errore di memorizzazione per: seats, public o free_seats.")
        return redirect(url_for('admin_home', username=drafttrip['a_username']))

    format = "%d/%m/%Y"
    try:
        drafttrip['start'] = datetime.strptime(drafttrip['start'], "%Y-%m-%d").strftime(format)
        drafttrip['end'] = datetime.strptime(drafttrip['end'], "%Y-%m-%d").strftime(format)

        start = datetime.strptime(drafttrip['start'], format)
        end = datetime.strptime(drafttrip['end'], format)

        if start >= end:
            flash("Errore: la data di ritorno deve essere successiva alla partenza.")
            return redirect(url_for('admin_home', username=drafttrip['a_username']))

        drafttrip['nights'] = (end - start).days
    except ValueError:
        flash("Errore: formato data non valido. Usa 'dd/mm/yy'.")
        return redirect(url_for('admin_home', username=drafttrip['a_username']))

    res = trips_dao.save_trip(drafttrip)

    if not res:
        flash("Ops, la bozza non è stata salvata! Riprova.")
        return redirect(url_for('admin_home', username=drafttrip['a_username']))

    if action == 'post':

      for key in required_fields:
        if not drafttrip[key]:
          flash("Completa tutti i campi del viaggio per pubblicare!")
          return redirect(url_for('admin_home', username=drafttrip['a_username']))

      res = trips_dao.public_trip(drafttrip['tripcode'])

      if not res:
          flash("Ops, pubblicazione del viaggio non riuscita! Riprova.")
          return redirect(url_for('admin_home', username=drafttrip['a_username']))

    return redirect(url_for('admin_home', username=drafttrip['a_username']))


@app.route('/delete_validation', methods=['POST'])
def del_trip():
    tripcode = request.form.get("tripcode")
    username = request.form.get("username")

    res = trips_dao.delete_trip(tripcode)
    if res:
        flash("Viaggio eliminato con successo!", "success")
    else:
        flash("Errore nell'eliminazione del viaggio.", "danger")
    return redirect(url_for('admin_home', username=username))

@app.route('/booking', methods=['POST'])
@login_required
def booking():
  book_info = request.form.to_dict()

  isbooked = bookings_dao.get_if_booked(book_info['u_username'],book_info['tripcode'])

  if isbooked:
      flash("Il viaggio è già stato prenotato!")
      return redirect(url_for('user_home', username=book_info['u_username']))

  bookingtrip = trips_dao.get_trip(book_info['tripcode'])
  mybookings = bookings_dao.get_booked_trips(book_info['u_username'])

  trip_start = datetime.strptime(bookingtrip['start'], "%d/%m/%Y")
  trip_end = datetime.strptime(bookingtrip['end'], "%d/%m/%Y")

  for booking in mybookings:
    booking_trip = trips_dao.get_trip(booking['tripcode'])
    test_start = datetime.strptime(booking_trip['start'], "%d/%m/%Y")
    test_end = datetime.strptime(booking_trip['end'], "%d/%m/%Y")

    if (trip_start <= test_end and trip_end >= test_start):
      flash("Le date del viaggio si sovrappongono con una prenotazione esistente!")
      return redirect(url_for('user_home', username=book_info['u_username']))

  today = datetime.today()

  if trip_start < today:
      flash("Siamo già partiti! La prossima volta sarai dei nostri!")
      return redirect(url_for('user_home', username=book_info['u_username']))

  if bookingtrip['free_seats'] == 0:
      flash("Siamo al completo! La prossima volta sarai dei nostri!")
      return redirect(url_for('user_home', username=book_info['u_username']))

  free_seats = bookingtrip['free_seats'] - 1
  seats=trips_dao.update_seats(book_info['tripcode'],free_seats)
  res=bookings_dao.new_booking(book_info)

  if (res == True) and (seats == True) :
    flash("Prenotazione completata con successo!")
  else:
    flash('Ops qualcosa è andato storto! Riprova')

  return redirect(url_for('user_home', username=book_info['u_username']))

@app.route('/admin_answer_validation', methods=['POST'])
@login_required
def answer_validation():
    ans_info = request.form.to_dict()

    success = False
    success = quests_dao.add_answer(ans_info['questid'], ans_info['answer'])

    if success:
      flash("Risposta caricata!")
    else:
      flash("Ci sono stati problemi nel caricamento della tua risposta! Riprova.")

    flash("Ci sono stati problemi nel caricamento della tua risposta! Riprova.")
    return redirect(url_for('admin_home', username=ans_info['username']))

@app.route('/questbox', methods=['POST'])
def u_quest():
    quest_info = request.form.to_dict()

    u_user = users_dao.get_user_by_username(quest_info['u_username'])
    if not u_user:
      flash("Username inserito sbagliato! Riprova")
      return redirect(url_for('user_home', username=quest_info['u_username']))

    success = False
    success = quests_dao.add_quest(quest_info)

    if success:
      flash("Domanda inviata!")
      return redirect(url_for('trip',id=quest_info['tripcode']))

    flash("Ci sono stati problemi nel caricamento della tua domanda! Riprova.")
    return redirect(url_for('trip'))


@app.route('/user_login', methods=['POST'])
def user_login():
    user_info = request.form.to_dict()
    user_db = users_dao.get_user_by_username(user_info['username'])

    if not user_db or not check_password_hash(user_db['password'], user_info['password']):
        flash("Username o password errati!")
        return redirect(url_for('home'))
    else:
      new = User(name=user_db['name'], surname=user_db['surname'], birthdate=user_db['birthdate'], gender=user_db['gender'], username=user_db['username'], password=user_db['password'], admin=user_db['admin'] )
      #Autenticazione
      login_user(new, True)

    if user_db['admin'] == 1:
        return redirect(url_for('admin_home', username=user_info['username']))
    else:
        return redirect(url_for('user_home', username=user_info['username']))


@app.route('/signup', methods=['POST'])
def signup():
  newuser_info = request.form.to_dict()

  user = users_dao.get_user_by_username(newuser_info['username'])
  if user:
    flash('Nome utente già iscritto')
    return redirect(url_for('home'))

  if newuser_info['gender'] == 'M':
     newuser_info['gender'] = 'S345271_07-02-2025/static/man.jpg'
  else:
     newuser_info['gender'] = 'S345271_07-02-2025/static/woman.jpg'
  print(newuser_info)


  if newuser_info ['name'] == '':
    flash('Completa tutti i campi per iscriverti')
    return redirect(url_for('home'))
  if newuser_info ['surname'] == '':
    flash('Completa tutti i campi per iscriverti')
    return redirect(url_for('home'))
  if newuser_info ['birthdate'] == '':
    flash('Completa tutti i campi per iscriverti')
    return redirect(url_for('home'))
  if newuser_info ['gender'] == '':
    flash('Completa tutti i campi per iscriverti')
    return redirect(url_for('home'))
  if newuser_info ['username'] == '':
    flash('Completa tutti i campi per iscriverti')
    return redirect(url_for('home'))
  if newuser_info ['password'] == '':
    flash('Completa tutti i campi per iscriverti')
    return redirect(url_for('home'))

  newuser_info['birthdate'] = datetime.strptime(newuser_info['birthdate'], "%Y-%m-%d").strftime("%d/%m/%Y")
  newuser_info['password'] = generate_password_hash(newuser_info['password'])

  success = False
  success = users_dao.new_user(newuser_info)

  if success:
      flash('Iscrizione avvenuta con successo!')
      return redirect(url_for('home'))

  flash('Iscrizione non completata! Riprovare')
  return redirect(url_for('home'))

@login_manager.user_loader
def load_user(user_id):

    user_db = users_dao.get_user_by_username(user_id)
    user = User(name=user_db['name'], surname=user_db['surname'], birthdate=user_db['birthdate'],
                 gender=user_db['gender'], username=user_db['username'], password=user_db['password'],
                 admin=user_db['admin'] )

    return user


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))
