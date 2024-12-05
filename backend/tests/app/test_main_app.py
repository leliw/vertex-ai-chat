from typing import Any
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest

from app.main import app


class CookieAwareTestClient(TestClient):
    """Test client that stores and sends cookies with requests."""

    def __init__(self, app: FastAPI):
        super().__init__(app)
        self.cookies = {}

    def request(self, method: str, url: str, **kwargs: Any) -> Any:
        """Send a request with cookies."""
        if self.cookies:
            kwargs["cookies"] = self.cookies

        response = super().request(method, url, **kwargs)
        self.cookies.update(response.cookies)
        return response


@pytest.fixture
def client():
    return CookieAwareTestClient(app)


def test_config_get(client):
    # When: GET request to /api/config
    response = client.get("/api/config")
    # Then: Response status code is 200
    assert 200 == response.status_code
    # And: Response contains the config
    assert "version" in response.json().keys()
