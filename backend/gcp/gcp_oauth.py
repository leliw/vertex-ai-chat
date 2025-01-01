"""Google OAuth2 class."""

import os
from typing import Any, Optional
from pydantic import BaseModel
import requests
from jose import jwt
from jose.exceptions import JWTError

GOOGLE_URL_PUBLIC_KEYS = "https://www.googleapis.com/oauth2/v1/certs"


class UserData(BaseModel):
    email: str
    name: str
    given_name: Optional[str] = None
    family_name: Optional[str] = None
    picture: Optional[str] = None


class GcpOAuth:
    """Google OAuth2 class."""

    def __init__(
        self,
        client_id: str = None,
    ):
        self.client_id = os.getenv("GOOGLE_OAUTH_CLIENT_ID", client_id)
        self._google_public_keys = self._get_google_public_keys()

    def _get_google_public_keys(self):
        r = requests.get(GOOGLE_URL_PUBLIC_KEYS)
        keys = r.json()
        return keys

    def verify_jwt(self, token) -> dict[str, Any] | None:
        """Verify Google JWT token and return decoded token."""
        if token.startswith("Bearer "):
            token = token.split(" ")[1]
        try:
            decoded_token = jwt.decode(
                token,
                self._google_public_keys,
                algorithms=["RS256"],
                audience=self.client_id,
            )
            decoded_token["email"] = decoded_token["email"].lower()
            return decoded_token
        except JWTError:
            return None
