import sqlite3

def get_u_quests(username):
    query = 'SELECT * FROM quests WHERE u_username = ?'
    #Contiene: quest, u_username, answer, destination, a_username
    connection = sqlite3.connect('S345271_07-02-2025/db/travelbuds.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(query, (username,))

    res = cursor.fetchall()


    cursor.close()
    connection.close()

    return res

def get_a_quests(username):

    query = 'SELECT * FROM quests WHERE a_username = ? AND (answer IS NULL OR LENGTH(answer) = 0)'

    connection = sqlite3.connect('S345271_07-02-2025/db/travelbuds.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(query, (username,))

    res = cursor.fetchall()

    cursor.close()
    connection.close()

    return res

def add_answer(questid, answer):
    connection = sqlite3.connect('S345271_07-02-2025/db/travelbuds.db')
    cursor = connection.cursor()
    connection.row_factory = sqlite3.Row

    query = "UPDATE quests SET answer = ? WHERE questid = ?"

    try:
        cursor.execute(query, (answer, questid))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Exception as e:
        print("Errore nel caricamento della risposta nel database:", e)
        cursor.close()
        connection.close()
        return False

def add_quest(quest_info):
    query = 'INSERT INTO quests(quest,u_username,destination,a_username) VALUES (?,?,?,?)'

    connection = sqlite3.connect('S345271_07-02-2025/db/travelbuds.db')
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    success = False

    try:
        cursor.execute(query, (quest_info.get('quest'),quest_info.get('u_username'),
                               quest_info.get('trip_destination'),quest_info.get('a_username')
        ))
        connection.commit()
        success = True
    except Exception as e:
        print('Error:', str(e))
        connection.rollback()

    cursor.close()
    connection.close()

    return success