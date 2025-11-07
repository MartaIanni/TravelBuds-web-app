import sqlite3

def get_trip(trip_id):
    query = 'SELECT * FROM trips WHERE tripcode = ?'

    connection = sqlite3.connect('travelbuds.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(query, (trip_id,))

    res = cursor.fetchone()

    cursor.close()
    connection.close()

    return res

def get_public_trips():
    query = 'SELECT * FROM trips WHERE public = 1'
    connection = sqlite3.connect('travelbuds.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(query)

    res = cursor.fetchall()

    cursor.close()
    connection.close()

    return res

def get_draft_trips(username):
    query = 'SELECT * FROM trips WHERE public = 0 AND a_username = ?'
    connection = sqlite3.connect('travelbuds.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(query,(username,))

    res = cursor.fetchall()

    cursor.close()
    connection.close()

    return res

def get_mypublic_trips(username):
    query = 'SELECT * FROM trips WHERE public = 1 AND a_username = ?'
    connection = sqlite3.connect('travelbuds.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(query,(username,))

    res = cursor.fetchall()

    cursor.close()
    connection.close()

    #Converte ogni riga in un dizionario per aggiungere partecipants dopo
    return [dict(trip) for trip in res]

def get_u_list(tripcode):
    query = 'SELECT u_username FROM bookings WHERE tripcode = ?'

    connection = sqlite3.connect('travelbuds.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(query, (tripcode,))

    list = cursor.fetchall()

    cursor.close()
    connection.close()

    # Estrazione dei soli nomi utente dalla lista di tuple
    return [user[0] for user in list]


def add_trip(trip):
    query = 'INSERT INTO trips(destination,start,end,seats,description,transport_price,stay_price,act_price,subtitle,price,tour,public,free_seats,card_img,bg_img,nights,a_username) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)'

    connection = sqlite3.connect('travelbuds.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    success = False

    try:
        cursor.execute(query, (
            trip.get('destination'), trip.get('start'), trip.get('end'), trip.get('seats'),
            trip.get('description'), trip.get('transport_price'), trip.get('stay_price'),
            trip.get('act_price'), trip.get('subtitle'), trip.get('price'), trip.get('tour'),
            trip.get('public'), trip.get('free_seats'), trip.get('card_img'), trip.get('bg_img'),
            trip.get('nights'), trip.get('a_username')
        ))
        connection.commit()
        success = True
    except Exception as e:
        print('Error:', str(e))
        connection.rollback()


    cursor.close()
    connection.close()

    return success

def delete_trip(tripcode):

    query = 'DELETE FROM trips WHERE tripcode = ?'

    connection = sqlite3.connect('travelbuds.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(query, (tripcode,))
    success = False

    if cursor.rowcount > 0:
        success = True

    connection.commit()
    cursor.close()
    connection.close()

    return success


def save_trip(drafttrip):
    connection = sqlite3.connect('travelbuds.db')
    cursor = connection.cursor()
    connection.row_factory = sqlite3.Row

    query = "UPDATE trips SET destination = ?, start = ?, end = ?, description = ?, transport_price = ?, stay_price = ?, act_price = ?, subtitle = ?, price = ?, tour = ?, card_img = ?, bg_img = ?, nights = ?, seats = ?, free_seats = ?, a_username = ? WHERE tripcode = ?"
    values = (
            drafttrip['destination'], drafttrip['start'], drafttrip['end'], drafttrip['description'],
            drafttrip['transport_price'], drafttrip['stay_price'], drafttrip['act_price'],
            drafttrip['subtitle'], drafttrip['price'], drafttrip['tour'], drafttrip['card_img'],
            drafttrip['bg_img'], drafttrip['nights'], drafttrip['seats'], drafttrip['free_seats'],
            drafttrip['a_username'], drafttrip['tripcode']
        )

    try:
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print("Errore nel salvataggio della bozza:", e)
        cursor.close()
        connection.close()
        return False

def public_trip(tripcode):
    connection = sqlite3.connect('travelbuds.db')
    cursor = connection.cursor()
    connection.row_factory = sqlite3.Row

    query = "UPDATE trips SET public = 1 WHERE tripcode = ?"

    try:
        cursor.execute(query, (tripcode,))
        connection.commit()
        cursor.close()
        connection.close()
        return cursor.rowcount > 0
    except Exception as e:
        print("Errore nella pubblicazione del viaggio:", e)
        cursor.close()
        connection.close()
        return False

def update_seats(tripcode,update):
    query = 'UPDATE trips SET free_seats = ? WHERE tripcode = ?'
    connection = sqlite3.connect('travelbuds.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    try:
        cursor.execute(query,(update,tripcode,))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print("Errore nell'aggiornamento dei posti disponibili:", e)
        cursor.close()
        connection.close()
        return False
