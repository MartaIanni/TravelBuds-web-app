import sqlite3, trips_dao

def get_if_booked(username, tripcode):
    query = 'SELECT * FROM bookings WHERE u_username = ? AND tripcode = ?'

    connection = sqlite3.connect('travelbuds.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(query, (username,tripcode,))

    res = cursor.fetchone()

    cursor.close()
    connection.close()

    return res

def get_booked_trips(username):
    query = 'SELECT * FROM bookings WHERE u_username = ?'

    connection = sqlite3.connect('travelbuds.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(query, (username,))

    res = cursor.fetchall()

    cursor.close()
    connection.close()

    return res

def new_booking(booking):
    query = 'INSERT INTO bookings(u_username,tripcode,destination,card_img) VALUES (?,?,?,?)'

    connection = sqlite3.connect('travelbuds.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    success = False

    try:
        cursor.execute(query, (booking['u_username'],booking['tripcode'],booking['destination'], booking['card_img']))
        connection.commit()
        success = True
    except Exception as e:
        print('Error', str(e))
        connection.rollback()

    cursor.close()
    connection.close()

    return success