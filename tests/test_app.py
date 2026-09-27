import os
from pathlib import Path

TEST_DB = Path("test_pocketsmart.db")
os.environ["DATABASE_URL"] = f"sqlite:///./{TEST_DB}"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["GEMINI_API_KEY"] = ""

from fastapi.testclient import TestClient

from app.database import Base, engine
from main import app


client = TestClient(app, follow_redirects=False)


def setup_module():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module():
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if TEST_DB.exists():
        TEST_DB.unlink()


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_register_and_generate_home():
    response = client.post(
        "/register",
        data={
            "name": "Test User",
            "email": "test@example.com",
            "password": "strong-password",
        },
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/dashboard"

    response = client.post(
        "/generate-home",
        data={
            "budget": "50000",
            "currency": "INR",
            "rooms": "Living room",
            "style": "Modern",
            "required_items": "Sofa, table, lights",
            "notes": "",
        },
    )
    assert response.status_code == 303
    assert response.headers["location"].startswith("/recommendations/")


def test_history_requires_authentication():
    fresh_client = TestClient(app, follow_redirects=False)
    response = fresh_client.get("/history")
    assert response.status_code == 303
    assert response.headers["location"] == "/login"
