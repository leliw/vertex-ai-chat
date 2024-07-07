"""Test client for FastAPI app."""

from typing import Any
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.main import app, session_manager, SessionData


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


# Create a global test client for the FastAPI app.
# This way, the test client can be imported and used in other test files.
# The FastAPI app is created only once when the main module is imported.

app_test_client = CookieAwareTestClient(app)
user_data = {"email": "jasio.fasola@gmail.com", "name": "Jasio Fasola"}
# Replace the create_session_for_user method with a lambda function that returns a SessionData object with the user_data dictionary.
# This way, the session_manager will always return the same user data when creating a new session without the need to authenticate.
session_manager.create_session_for_user = lambda _: SessionData(user=user_data)
