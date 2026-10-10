from typing import Any
from fastapi import HTTPException, status


class SplitwiseException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: dict[str, Any] | None = None,
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class UserAlreadyExistsException(SplitwiseException):
    def __init__(self, detail: str = "User with this email or phone already exists"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class InvalidCredentialsException(SplitwiseException):
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class UnauthorizedException(SplitwiseException):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class NotFoundException(SplitwiseException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ForbiddenException(SplitwiseException):
    def __init__(self, detail: str = "You do not have permission to perform this action"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class ValidationException(SplitwiseException):
    def __init__(self, detail: str = "Invalid business rule operation"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class ConflictException(SplitwiseException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
