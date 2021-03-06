import sqlite3
import os
import re
import hashlib
from Client import Client
import datetime
from settings import BLOCK_FOR_N_MINUTES, PASSWORD_MIN_LENGTH


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
    def validate_password(username, password):
        are_there_digits = re.search(r'\d+', password)
        are_there_uppercase_letter = re.search(r'[A-Z]+', password)
        enough_length = len(password) >= PASSWORD_MIN_LENGTH
        are_there_symbols = re.search('[\-\/\@\?\!\,\.\#\&\*]+', password)

        if are_there_digits and are_there_uppercase_letter and enough_length and are_there_symbols and username not in password:
            return True
        else:
            return False

    @staticmethod
    def hash_password(password):
        hash_pass = hashlib.sha1(password.encode())
        hex_dig = hash_pass.hexdigest()

        return hex_dig

    def register(self, username, password):
        try:
            if BankDatabaseManager.validate_password(username, password):
                hashed_password = BankDatabaseManager.hash_password(password)
                self.cursor.execute("""INSERT INTO Clients
                    (client_username, client_password)
                    VALUES (?, ?)""", (username, hashed_password))
                self.conn.commit()
                return True
            else:
                return False
        except:
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

    def is_user_registered(self):
        pass

    def add_blocked_user(self, username):
        self.cursor.execute("""SELECT client_id FROM Clients
            WHERE client_username = ?""", (username, ))
        cleint_id = self.cursor.fetchone()[0]
        blocked_on_date = datetime.datetime.now()

        self.cursor.execute("""INSERT INTO Blocked_Clients
        (blocked_client_id, blocked_client_date)
        VALUES (?, ?)""", (cleint_id, blocked_on_date))
        self.conn.commit()

    def get_blocked_users(self):
        return self.cursor.execute("""SELECT client_username FROM Clients
            INNER JOIN Blocked_Clients
            ON Clients.client_id = Blocked_Clients.blocked_client_id""")

    def update_blocked_users(self):
        time = datetime.datetime.now() - \
            datetime.timedelta(minutes=BLOCK_FOR_N_MINUTES)
        self.cursor.execute("""DELETE FROM Blocked_Clients
            WHERE blocked_client_date <= ? """, (time, ))
        self.conn.commit()

    def reset_password(self, username, new_password):
        self.cursor.execute("""UPDATE Clients
            SET client_password = ?
            WHERE client_username = ?""", (BankDatabaseManager.hash_password(new_password), username))
        self.conn.commit()

    def change_email(self, new_email, logged_user):
        self.cursor.execute("""UPDATE Clients
            SET client_email = ?
            WHERE client_id = ?""", (new_email, logged_user.get_id()))
        self.conn.commit()
        logged_user.set_email(new_email)

    def get_email(self, username):
        self.cursor.execute("""SELECT client_email
            FROM Clients
            WHERE client_username = ?""", (username, ))

        return self.cursor.fetchone()[0]

    def change_message(self, new_message, logged_user):
        current_user_id = logged_user.get_id()
        self.cursor.execute("""UPDATE Clients
            SET client_message = ?
            WHERE client_id = ?""", (new_message, current_user_id))
        self.conn.commit()

    def get_message(self, username):
        self.cursor.execute("""SELECT client_message
            FROM Clients
            WHERE client_username = ?""", (username, ))

        return self.cursor.fetchone()[0]

    def change_password(self, new_password, logged_user):
        current_user_id = logged_user.get_id()
        new_hashed_password = BankDatabaseManager.hash_password(new_password)
        self.cursor.execute("""UPDATE Clients
            SET client_password = ?
            WHERE client_id = ?""", (new_hashed_password, current_user_id))
        self.conn.commit()

    def get_hashed_password(self, username):
        self.cursor.execute("""SELECT client_password
            FROM Clients
            WHERE client_username = ?""", (username, ))
        return self.cursor.fetchone()[0]

    def get_balance(self, logged_user):
        current_user_id = logged_user.get_id()
        self.cursor.execute("""SELECT client_balance
            FROM Clients
            WHERE client_id = ?""", (current_user_id, ))

        return float(self.cursor.fetchone()[0])

    def deposit_money(self, logged_user, amount_money):
        current_user_id = logged_user.get_id()
        money = self.get_balance(logged_user) + amount_money
        self.cursor.execute("""UPDATE Clients
            SET client_balance = ?
            WHERE client_id = ?""", (money, current_user_id))
        self.conn.commit()

        logged_user.set_balance(money)

    def withdraw_money(self, logged_user, amount_money):
        current_user_id = logged_user.get_id()
        money = self.get_balance(logged_user) - amount_money

        if money < 0:
            return False

        self.cursor.execute("""UPDATE Clients
            SET client_balance = ?
            WHERE client_id = ?""", (money, current_user_id))
        self.conn.commit()

        logged_user.set_balance(money)

        return True
