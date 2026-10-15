import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='space_invaders_clean',
            user='root',
            password=''
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    return None

def register_player_and_score(username, score):
    connection = get_db_connection()
    if not connection:
        return

    cursor = connection.cursor()
    try:
        cursor.execute("SELECT id FROM players WHERE username = %s", (username,))
        result = cursor.fetchone()
        
        if result:
            player_id = result[0]
        else:
            cursor.execute("INSERT INTO players (username) VALUES (%s)", (username,))
            connection.commit()
            player_id = cursor.lastrowid

        cursor.execute("INSERT INTO scores (player_id, score) VALUES (%s, %s)", (player_id, score))
        connection.commit()
        print(f"Successfully saved score {score} for {username}!")
    except Error as e:
        print(f"Database error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_leaderboard(limit=10):
    connection = get_db_connection()
    if not connection:
        return []

    cursor = connection.cursor(dictionary=True)
    try:
        query = """
            SELECT players.username, scores.score, scores.achieved_at 
            FROM scores 
            JOIN players ON scores.player_id = players.id 
            ORDER BY scores.score DESC 
            LIMIT %s
        """
        cursor.execute(query, (limit,))
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching leaderboard: {e}")
        return []
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def update_player_username(old_username, new_username):
    connection = get_db_connection()
    if not connection:
        return False

    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE players SET username = %s WHERE username = %s", (new_username, old_username))
        connection.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error updating player: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# --- CHECK LOGIN FUNCTION ---
def check_login(username, password):
    connection = get_db_connection()
    if not connection:
        return False

    cursor = connection.cursor()
    try:
        query = "SELECT * FROM players WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        result = cursor.fetchone()
        return result is not None
    except Error as e:
        print(f"Login database error: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# --- NEW: REGISTER USER / CREATE ACCOUNT FUNCTION ---
def register_user(username, password):
    connection = get_db_connection()
    if not connection:
        return False, "Database connection failed!"

    cursor = connection.cursor()
    try:
        # Check if username already exists
        cursor.execute("SELECT id FROM players WHERE username = %s", (username,))
        if cursor.fetchone():
            return False, "Username already exists!"

        # Insert new player account
        cursor.execute("INSERT INTO players (username, password) VALUES (%s, %s)", (username, password))
        connection.commit()
        return True, "Account created! You can now log in."
    except Error as e:
        print(f"Registration error: {e}")
        return False, f"Registration error: {e}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()