import requests

API = "http://localhost:9099/identitytoolkit.googleapis.com/v1"
API_KEY = "fake-api-key"  # emulator accepts any key

EMAIL = "testuser@example.com"
PASSWORD = "test12345"

def signup(email, password):
    resp = requests.post(
        f"{API}/accounts:signUp?key={API_KEY}",
        json={"email": email, "password": password, "returnSecureToken": True},
        timeout=10,
    )
    return resp

def signin(email, password):
    resp = requests.post(
        f"{API}/accounts:signInWithPassword?key={API_KEY}",
        json={"email": email, "password": password, "returnSecureToken": True},
        timeout=10,
    )
    return resp

# Try to sign up first; if the email exists, fall back to sign-in
r = signup(EMAIL, PASSWORD)
if r.status_code != 200:
    # Likely EMAIL_EXISTS -> sign-in
    r = signin(EMAIL, PASSWORD)
    r.raise_for_status()
else:
    r.raise_for_status()

data = r.json()
print(data["idToken"])
