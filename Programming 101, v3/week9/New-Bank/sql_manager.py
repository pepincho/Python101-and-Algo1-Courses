import sqlite3
import os
import re
import hashlib
from Client import Client


class BankDatabaseManager:

    @staticmethod
    def create_from_db_and_sql(db_name, create_tables, drop_database, create_if_exists=False):
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        if not os.path.exists(db_name) or create_if_exists:

            with open(drop_database, "r") as f:
                cursor.executescript(f.read())
                conn.commit()

        with open(create_tables, "r") as f:
            cursor.executescript(f.read())
            conn.commit()

        return BankDatabaseManager(conn)

    def __init__(self, connection):
        self.conn = connection
        self.cursor = self.conn.cursor()

    @staticmethod
    def validate_password(password):
        if re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', password):
            return True
        else:
            return False

    @staticmethod
    def hash_password(password):
        hash_pass = hashlib.sha1(password.encode())
        hex_dig = hash_pass.hexdigest()

        return hex_dig

    def register(self, username, password):
        if BankDatabaseManager.validate_password(password):
            hashed_password = BankDatabaseManager.hash_password(password)
            self.cursor.execute("""INSERT INTO Clients
                (client_username, client_password)
                VALUES (?, ?)""", (username, hashed_password))
            self.conn.commit()
            return True
        else:
            return False

    def login(self, username, password):
        get_user_query = """SELECT client_id,
                                client_username,
                                client_balance,
                                client_message,
                                client_email
        FROM Clients
        WHERE client_username = ? AND client_password = ?
        LIMIT 1"""

        hashed_password = self.hash_password(password)

        self.cursor.execute(get_user_query, (username, hashed_password))
        user = self.cursor.fetchone()

        if user:
            return Client(user[0], user[1], user[2], user[3], user[4])
        else:
            False