import os
import sys

# Ensure the service root is on sys.path so `from app.main import app` resolves
SERVICE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if SERVICE_ROOT not in sys.path:
    sys.path.insert(0, SERVICE_ROOT)

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}

def test_recommend():
    r = client.get("/api/recommendations/123?limit=3")
    assert r.status_code == 200
    j = r.json()
    assert j["user_id"] == "123"
    assert len(j["recommendations"]) == 3
