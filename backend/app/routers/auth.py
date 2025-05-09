import logging
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from ampf.auth import (
    Tokens,
    ChangePasswordData,
    ResetPassword,
    ResetPasswordRequest,
    APIKey,
    APIKeyInDB,
    APIKeyRequest,
)


from app.dependencies import (
    AuthServiceDep,
    AuthTokenDep,
    TokenPayloadDep,
)
from app.user.user_model import User
from ampf.auth import GoogleOAuth

_log = logging.getLogger(__name__)


router = APIRouter(tags=["Autentykacja"])

UserFormDataDep = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post("/login")
def login(auth_service: AuthServiceDep, form_data: UserFormDataDep = None) -> Tokens:
    return auth_service.authorize(form_data.username, form_data.password)


@router.post("/logout")
def logout(auth_service: AuthServiceDep, refresh_token: AuthTokenDep) -> None:
    auth_service.add_to_black_list(refresh_token)


@router.post("/token-refresh")
def refresh_token(auth_service: AuthServiceDep, refresh_token: AuthTokenDep) -> Tokens:
    return auth_service.refresh_token(refresh_token)


@router.post("/change-password")
def change_password(
    auth_service: AuthServiceDep,
    payload: ChangePasswordData,
    token_payload: TokenPayloadDep,
) -> None:
    auth_service.change_password(
        token_payload.sub, payload.old_password, payload.new_password
    )


@router.post("/reset-password-request")
def reset_password_request(auth_service: AuthServiceDep, rpr: ResetPasswordRequest):
    auth_service.reset_password_request(rpr.email)


@router.post("/reset-password")
async def reset_password_route(auth_service: AuthServiceDep, rp: ResetPassword):
    auth_service.reset_password(rp.email, rp.reset_code, rp.new_password)


@router.post("/api-keys")
async def generate_api_key(
    auth_service: AuthServiceDep, token_payload: TokenPayloadDep, request: APIKeyRequest
) -> APIKey:
    return auth_service.generate_api_key(token_payload, request)


@router.get("/api-keys")
async def get_api_keys(
    auth_service: AuthServiceDep, token_payload: TokenPayloadDep
) -> List[APIKeyInDB]:
    return auth_service.get_api_keys(token_payload)


@router.delete("/api-keys/{key_hash}")
async def delete_api_key(
    auth_service: AuthServiceDep, token_payload: TokenPayloadDep, key_hash: str
):
    return auth_service.delete_api_key(token_payload, key_hash)


def get_authorization_token(request: Request) -> str:
    return request.headers.get("Authorization")


def get_google_oauth() -> GoogleOAuth:
    return GoogleOAuth()


@router.post("/google/login")
def google_login(
    auth_service: AuthServiceDep,
    google_oauth: Annotated[GoogleOAuth, Depends(get_google_oauth)],
    token: Annotated[str, Depends(get_authorization_token)],
) -> Tokens:
    """Login with Google OAuth."""
    # Verify google token
    user_data = google_oauth.verify_jwt(token)
    # Get user (if exist)
    user: User = auth_service._user_service.get_user_by_email(user_data["email"])
    if not user:
        _log.warning(f"User {user_data['email']} not found")
        raise HTTPException(
            status_code=404, detail=f"User {user_data['email']} not found"
        )
    if user_data["picture"] and user.picture != user_data["picture"]:
        user.picture = user_data["picture"]
        auth_service._user_service.update(user.username, user)
    # Create tokens for given user
    payload = auth_service.create_token_payload(user)
    return auth_service.create_tokens(payload)
