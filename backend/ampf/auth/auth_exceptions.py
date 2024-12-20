from fastapi import HTTPException


class IncorrectUsernameOrPasswordException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Incorrect username or password")


class TokenExpiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Token expired")


class InvalidTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalids token")


class InvalidRefreshTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid refresh token")


class BlackListedRefreshTokenException(HTTPException):
    def __init__(self):
        super().__init__(status_code=401, detail="Invalid token")


class IncorectOldPasswordException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Incorrect old password")


class UserNotExistsException(HTTPException):
    def __init__(self, user: str):
        super().__init__(status_code=404, detail=f"User {user} not exists")


class ResetCodeExpiredException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Reset code expired")


class ResetCodeException(HTTPException):
    def __init__(self):
        super().__init__(status_code=400, detail="Reset code error")


class InsufficientPermissionsError(HTTPException):
    def __init__(self):
        super().__init__(status_code=403, detail="Insufficient permissions.")
