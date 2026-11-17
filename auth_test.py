from auth import create_users_table, register_user, login_user
from getpass import getpass

create_users_table()

print("===== SMART EXPENSE TRACKER =====")

username = input("Enter username: ")
password = input("Enter password: ")

result = register_user(username, password)

if result:
    print("Registration successful!")
else:
    print("Username already exists!")

print("\n===== LOGIN TEST =====")

login_username = input("Enter username: ")
login_password = input("Enter password: ")

if login_user(login_username, login_password):
    print("Login successful!")
else:
    print("Invalid username or password!")