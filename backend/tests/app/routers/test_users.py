import logging

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from ampf.auth.auth_model import Tokens
from app.dependencies import get_email_sender, get_factory, get_server_config
from app.routers import auth, config, users
from app.user.user_service import UserService


@pytest.fixture
def client(factory, email_sender, test_config):
    logging.getLogger("ampf").setLevel(logging.DEBUG)
    app = FastAPI()
    app.dependency_overrides[get_factory] = lambda: factory
    app.dependency_overrides[get_email_sender] = lambda: email_sender
    app.dependency_overrides[get_server_config] = lambda: test_config
    app.include_router(prefix="/api", router=auth.router)
    app.include_router(prefix="/api/config", router=config.router)
    app.include_router(prefix="/api/users", router=users.router)
    UserService(factory).initialize_storege_with_user(test_config.default_user)
    client = TestClient(app)
    return client


@pytest.fixture
def access_token(client):
    response = client.post(
        "/api/login",
        data={"username": "test@test.com", "password": "test"},
    )
    assert response.status_code == 200
    r = Tokens(**response.json())
    return r.access_token


def test_get_all(client, access_token):
    # When: A GET request is made to /api/users
    response = client.get(
        "/api/users", headers={"Authorization": f"Bearer {access_token}"}
    )
    # Then: The response status code is 200
    assert response.status_code == 200
    r = response.json()
    # Then: The response is a list of users (only one, default user)
    assert isinstance(r, list)
    assert len(r) == 1
    assert "email" in r[0]
    assert "name" in r[0]


def test_post_get_put_delete(client, access_token):
    ## POST
    # Given: A new user
    user = {
        "email": "jasio@wp.pl",
        "password": "test",
        "name": "Jasio",
    }
    # When: A POST request is made to /api/users
    response = client.post(
        "/api/users",
        headers={"Authorization": f"Bearer {access_token}"},
        json=user,
    )
    # Then: The response status code is 200
    assert response.status_code == 200

    ## GET
    # When: A GET request is made to /api/users/{email}
    response = client.get(
        f"/api/users/{user['email']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    # Then: The response status code is 200
    assert response.status_code == 200
    r = response.json()
    # Then: The response is the user
    assert r["email"] == user["email"]
    assert r["name"] == user["name"]

    ## PUT
    # Given: A user with updated data
    user["name"] = "Jasio Fasola"
    # When: A PUT request is made to /api/users/{email}
    response = client.put(
        f"/api/users/{user['email']}",
        headers={"Authorization": f"Bearer {access_token}"},
        json=user,
    )
    # Then: The response status code is 200
    assert response.status_code == 200

    ## DELETE
    # When: A DELETE request is made to /api/users/{email}
    response = client.delete(
        f"/api/users/{user['email']}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    # Then: The response status code is 200
    assert response.status_code == 200


def test_register(client, access_token):
    # Given: A new user
    user = {
        "email": "admin@hanse-intelli-tech.pl",
        "firstName": "Admin",
        "lastName": "Admin",
    }
    # When: A POST request is made to /api/users/register
    response = client.post(
        "/api/users/register",
        json=user,
    )
    # Then: The response status code is 200
    assert response.status_code == 200
