from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from ampf.storage_in_memory import AmpfInMemoryFactory
from app.config import DefaultUserConfig, ServerConfig
from app.dependencies import get_factory, get_server_config
from app.routers import auth, config


@pytest.fixture
def client():
    app = FastAPI()
    app.dependency_overrides[get_factory] = lambda: AmpfInMemoryFactory()
    test_config = ServerConfig(
        default_user=DefaultUserConfig(email="test@test", password="test")
    )
    app.dependency_overrides[get_server_config] = lambda: test_config
    app.include_router(auth.router, prefix="/api")
    app.include_router(config.router, prefix="/api/config")
    client = TestClient(app)
    return client


def test_login_ok(client):
    # When: Default user logs in
    response = client.post(
        "/api/login",
        data={"username": "test@test", "password": "test"},
    )
    # Then: The response status code is 200
    assert response.status_code == 200


def test_login_wrong_password(client):
    # When: Default user logs in with wrong password
    response = client.post(
        "/api/login",
        data={"username": "test@test", "password": "wrong"},
    )
    # Then: The response status code is 401
    assert response.status_code == 401


def test_login_wrong_username(client):
    # When: Default user logs in with wrong password
    response = client.post(
        "/api/login",
        data={"username": "admin@test", "password": "test"},
    )
    # Then: The response status code is 401
    assert response.status_code == 401
