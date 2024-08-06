from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.dependencies import get_current_user_id
from app.routers import agents


@pytest.fixture
def client(tmp_path):
    app = FastAPI()
    app.include_router(agents.router, prefix="/api/agents")

    client = TestClient(app)
    app.dependency_overrides[get_current_user_id] = lambda: "test_user"
    return client


def test_create_agent(client):
    response = client.post(
        "/api/agents",
        json={"name": "test", "model_name": "test_model"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "test"

    client.delete("/api/agents/test")


def test_get_all_and_return_default(client):
    response = client.get("/api/agents")

    r = response.json()
    assert response.status_code == 200
    assert len(r) == 1
    assert r[0]["name"] == "gemini-1.5-flash"

    client.delete("/api/agents/gemini-1.5-flash")


def test_get_agent(client):
    response = client.post(
        "/api/agents",
        json={"name": "test", "model_name": "test_model"},
    )
    assert response.status_code == 200
    response = client.get("/api/agents")
    r = response.json()
    assert response.status_code == 200
    assert len(r) == 1
    assert r[0]["name"] == "test"

    response = client.get("/api/agents/test")
    r = response.json()
    assert response.status_code == 200
    assert r["model_name"] == "test_model"

    client.delete("/api/agents/test")


def test_put_agent(client):
    response = client.put(
        "/api/agents/test",
        json={"name": "test", "model_name": "test_model"},
    )
    assert response.status_code == 200

    response = client.get("/api/agents/test")
    r = response.json()
    assert response.status_code == 200
    assert r["model_name"] == "test_model"

    client.delete("/api/agents/test")
