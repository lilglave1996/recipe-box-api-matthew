
from app import create_app
from app.extensions import limiter
from config import TestingConfig

# Enable rate limiting before the app is created.
TestingConfig.RATELIMIT_ENABLED = True

app = create_app("testing")
client = app.test_client()

print("Testing POST /login")

for i in range(1, 7):
    response = client.post("/login", json={})
    print(f"Request {i}: HTTP {response.status_code}")

# Clear rate-limit counters before the next test.
with app.app_context():
    limiter.reset()

print("\nTesting POST /register")

for i in range(1, 5):
    response = client.post("/register", json={})
    print(f"Request {i}: HTTP {response.status_code}")

print("\nTesting GET /recipes")

with app.app_context():
    limiter.reset()

for i in range(1, 11):
    response = client.get("/recipes")
    print(f"Request {i}: HTTP {response.status_code}")


