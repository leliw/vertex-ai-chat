import logging
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm

from ampf.auth import (
    Tokens,
    ChangePasswordData,
    ResetPassword,
    ResetPasswordRequest,
)

from app.dependencies import (
    AuthServiceDep,
    AuthTokenDep,
    TokenPayloadDep,
)
from app.user.user_model import User
from gcp.gcp_oauth import OAuth

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


def get_authorization_token(request: Request) -> str:
    return request.headers.get("Authorization")


def get_google_oauth() -> OAuth:
    return OAuth()


@router.post("/google/login")
def google_login(
    auth_service: AuthServiceDep,
    oauth: Annotated[OAuth, Depends(get_google_oauth)],
    token: Annotated[str, Depends(get_authorization_token)],
) -> Tokens:
    """Login with Google OAuth."""
    # Verify google token
    user_data = oauth.verify_jwt(token)
    # Get user (if exist)
    user: User = auth_service._user_service.get_user_by_email(user_data["email"])
    if not user:
        _log.warning(f"User {user_data["email"]} not found")
        raise HTTPException(
            status_code=404, detail=f"User {user_data["email"]} not found"
        )
    if user_data["picture"] and user.picture != user_data["picture"]:
        user.picture = user_data["picture"]
        auth_service._user_service.update(user.username, user)
    # Create tokens for given user
    payload = auth_service.create_token_payload(user)
    return auth_service.create_tokens(payload)
