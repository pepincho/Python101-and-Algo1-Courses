import getpass
from sql_manager import BankDatabaseManager


# Bank Command Interface
class BankCI:

    WELCOME_MESSAGE = """Welcome to our bank service. You are not logged in.
    Please register or login"""

    def __init__(self, controller):
        self.controller = controller

    def main_menu(self):
        print (BankCI.WELCOME_MESSAGE)

        command = input("$$$> ")

        while command != "exit":

            if command == "register":
                self.register()

            elif command == "login":
                self.login()

            elif command == "help":
                self.help()

            elif command == "reset-password":
                self.reset_password()

            else:
                print ("Not a valid command!")

            command = input("$$$> ")

    def logged_menu(self, logged_user):
        print ("Welcome, You're logged in as: " + logged_user.get_username())

        command = input("Logged>> ")

        while command != "exit":

            if command == "info":
                self.show_info(logged_user)

            elif command == "changepass":
                self.change_pass(logged_user)

            elif command == "change-message":
                self.change_message(logged_user)

            elif command == "show-message":
                self.show_message(logged_user)

            elif command == "change-email":
                self.change_email(logged_user)

            elif command == "show-email":
                self.show_email(logged_user)

            elif command == "help":
                self.help_user()

            elif command == "deposit":
                self.deposit_money(logged_user)

            elif command == "withdraw":
                self.withdraw_money(logged_user)

            else:
                print ("Not a valid command!")

            command = input("Logged>> ")

    def register(self):
        username = input("Enter your username: ")
        password = getpass.getpass(prompt="Enter your password: ")
        reg_status = self.controller.register(username, password)

        while not reg_status[0]:
            print (reg_status[1])
            username = input("Enter your username: ")
            password = getpass.getpass(prompt="Enter your password: ")
            reg_status = self.controller.register(username, password)

        print (reg_status[1])

    def login(self):
        username = input("Enter your username: ")
        password = getpass.getpass(prompt="Enter your password: ")
        login_status = self.controller.login(username, password)

        if login_status[0]:
            self.logged_menu(login_status[0])
        else:
            print (login_status[1])

    def help(self):
        for line in self.controller.help():
            print (line)

    def show_info(self, logged_user):
        for line in self.controller.show_info(logged_user):
            print (line)

    def change_password(self, logged_user):
        new_password = input("Enter new password: ")
        self.controller.change_password(new_password, logged_user)

    def change_message(self, logged_user):
        new_message = input("Enter new message: ")
        self.controller.change_message(new_message, logged_user)

    def change_email(self, logged_user):
        new_email = input("Enter new email: ")
        self.controller.change_email(new_email, logged_user)

        print("Email changed!")

    def show_email(self, logged_user):
        user_email = self.controller.show_email(logged_user)

        print ("Your email is: {}".format(user_email))

    def show_message(self, logged_user):
        message = self.controller.show_message(logged_user)

        print ("Your message is: {}".format(message))

    def help_user(self):
        for line in self.controller.help_user():
            print (line)

    def reset_password(self):
        username = input('Your username> ')
        user_email = input('Your email> ')
        is_email_valid = self.controller.validate_email(username, user_email)

        if is_email_valid:
            self.controller.send_email(username, user_email)
            response = input('Enter code from email> ')
            is_response_valid = self.controller.check_user_response(
                username, response)

            if is_response_valid:
                new_password = getpass.getpass(
                    prompt="Enter your new password: ")

                while BankDatabaseManager.validate_password(username, new_password) is False:
                    new_password = getpass.getpass(
                        prompt="Enter your new password: ")

                print (self.controller.reset_password(username, new_password))
            else:
                print ("Wrong code!")
        else:
            print ("Invalid email!")

    def deposit_money(self, logged_user):
        amount_money = input("Enter the amount of money you want to deposit in your balance: ")

        print (self.controller.deposit_money(logged_user, float(amount_money)))

    def withdraw_money(self, logged_user):
        amount_money = input("Enter the amount of money you want to withdraw from your balance: ")

        print (self.controller.withdraw_money(logged_user, float(amount_money)))
