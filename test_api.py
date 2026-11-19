import requests
import time

BASE_URL = "http://127.0.0.1:5000"

# Generate a unique test username
username = "testuser" + str(int(time.time()))
password = "TestPass@123"

print("REGISTRATION TEST STARTED")

# Register test user
register_response = requests.post(
    f"{BASE_URL}/api/auth/register",
    json={
        "username": username,
        "password": password
    }
)

print("\nREGISTRATION RESULT:")
print(register_response.status_code)
print(register_response.json())

# Login test user
login_response = requests.post(
    f"{BASE_URL}/api/auth/login",
    json={
        "username": username,
        "password": password
    }
)

print("\nLOGIN RESULT:")
print(login_response.status_code)
print(login_response.json())

print("\nTESTING COMPLETED")