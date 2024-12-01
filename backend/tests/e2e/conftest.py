import json
from typing import Dict
from fastapi import Response
from fastapi.testclient import TestClient
import pytest


from ampf.auth.auth_model import TokenExp
from app.dependencies import get_email_sender, get_factory, get_server_config
from app.main import app


class AuthClient(TestClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_header = None

    def set_auth_header(self, auth_header):
        self.auth_header = auth_header

    def get(self, *args, status_code: int = 200, **kwargs) -> Response | Dict:
        if self.auth_header:
            kwargs["headers"] = self.auth_header
        response = super().get(*args, **kwargs)
        return self._response(response, status_code)

    def post(self, *args, status_code: int = 200, **kwargs):
        if self.auth_header:
            kwargs["headers"] = self.auth_header
        response = super().post(*args, **kwargs)
        return self._response(response, status_code)

    def put(self, *args, **kwargs):
        if self.auth_header:
            kwargs["headers"] = self.auth_header
        return super().put(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.auth_header:
            kwargs["headers"] = self.auth_header
        return super().delete(*args, **kwargs)

    def _response(self, response: Response, status_code: int = 200) -> Response | Dict:
        assert response.status_code == status_code
        if response.status_code == status_code:
            if "application/json" in response.headers.get("content-type"):
                return response.json()
            if "text/event-stream" in response.headers.get("content-type"):
                return json.loads(f"[{response.text}]")
        return response


@pytest.fixture
def client(factory, email_sender, test_config):
    """Create a FastAPI test client where the app is the main FastAPI app."""

    app.dependency_overrides[get_factory] = lambda: factory
    app.dependency_overrides[get_email_sender] = lambda: email_sender
    app.dependency_overrides[get_server_config] = lambda: test_config

    client = AuthClient(app)
    # Clear token_black_list
    factory.create_compact_storage("token_black_list", TokenExp, "token").drop()
    # Login
    r = client.post(
        "/api/login",
        data={"username": "test@test.com", "password": "test"},
    )
    auth_header = {"Authorization": f"Bearer {r['access_token']}"}
    client.set_auth_header(auth_header)

    yield client
    # Logout
    client.post(
        "/api/logout", headers={"Authorization": f"Bearer {r['refresh_token']}"}
    )
