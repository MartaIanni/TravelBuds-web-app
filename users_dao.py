import sqlite3

def get_user_by_username(username):
    query = 'SELECT * FROM users WHERE username = ?'

    connection = sqlite3.connect('travelbuds.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(query, (username,))

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    return result

def new_user(n_user):
    query = 'INSERT INTO users(name,surname,birthdate,gender,username,password,admin) VALUES (?,?,?,?,?,?,?)'

    connection = sqlite3.connect('travelbuds.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    success = False

    try:
        cursor.execute(query, (n_user['name'],n_user['surname'],n_user['birthdate'],
                               n_user['gender'], n_user['username'], n_user['password'],0))
        connection.commit()
        success = True
    except Exception as e:
        print('Error', str(e))
        connection.rollback()

    cursor.close()
    connection.close()

    return success

