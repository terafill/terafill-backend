from enum import Enum
from typing import Optional
from fastapi import HTTPException, status


class ErrorCodes(Enum):
    UNKOWN_SERVER_ERROR = 1000
    EMAIL_ALREADY_REGISTERED = 1001
    INVALID_VERIFICATION_CODE = 1002
    EMAIL_DEACTIVATED = 1003
    USER_NOT_FOUND = 1004
    INVALID_CLIENT_PROOF = 1005
    SESSION_NOT_FOUND = 1006
    INVALID_SESSION = 1007
    ITEM_NOT_FOUND = 1008


class InternalServerException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        message: Optional[str] = None,
        headers: Optional[dict] = None,
    ):
        if not message:
            message = "Something went wrong. Please try again."
        super().__init__(
            status_code,
            detail={
                "error": "UNKOWN_SERVER_ERROR",
                "code": ErrorCodes.UNKOWN_SERVER_ERROR.value,
                "info": message,
            },
            headers=headers,
        )


class EmailAlreadyRegisteredException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_409_CONFLICT,
        message: Optional[str] = None,
        headers: Optional[dict] = None,
    ):
        if not message:
            message = "Email is already registered."
        super().__init__(
            status_code,
            detail={
                "error": "EMAIL_ALREADY_REGISTERED",
                "code": ErrorCodes.EMAIL_ALREADY_REGISTERED.value,
                "info": message,
            },
            headers=headers,
        )


class InvalidVerificationCodeException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        message: Optional[str] = None,
        headers: Optional[dict] = None,
    ):
        if not message:
            message = "Invalid verification code provided, please try again."
        super().__init__(
            status_code,
            detail={
                "error": "INVALID_VERIFICATION_CODE",
                "code": ErrorCodes.INVALID_VERIFICATION_CODE.value,
                "info": message,
            },
            headers=headers,
        )


class EmailDeactivatedException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        message: Optional[str] = None,
        headers: Optional[dict] = None,
    ):
        if not message:
            message = "Email is deactivated. Please contact support for resolution."
        super().__init__(
            status_code,
            detail={
                "error": "EMAIL_DEACTIVATED",
                "code": ErrorCodes.EMAIL_DEACTIVATED.value,
                "info": message,
            },
            headers=headers,
        )


class UserNotFoundException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        message: Optional[str] = None,
        headers: Optional[dict] = None,
    ):
        if not message:
            message = "User not found."
        super().__init__(
            status_code,
            detail={
                "error": "USER_NOT_FOUND",
                "code": ErrorCodes.USER_NOT_FOUND.value,
                "info": message,
            },
            headers=headers,
        )


class InvalidClientProofException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        message: Optional[str] = None,
        headers: Optional[dict] = None,
    ):
        if not message:
            message = "Invalid email or password."
        super().__init__(
            status_code,
            detail={
                "error": "INVALID_EMAIL_OR_PASSWORD",
                "code": ErrorCodes.INVALID_CLIENT_PROOF.value,
                "info": message,
            },
            headers=headers,
        )


class SessionNotFoundException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_404_NOT_FOUND,
        message: Optional[str] = None,
        headers: Optional[dict] = None,
    ):
        if not message:
            message = "Session not found."
        super().__init__(
            status_code,
            detail={
                "error": "SESSION_NOT_FOUND",
                "code": ErrorCodes.SESSION_NOT_FOUND.value,
                "info": message,
            },
            headers=headers,
        )


class InvalidSessionException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        message: Optional[str] = None,
        headers: Optional[dict] = None,
    ):
        if not message:
            message = "Invalid Session. Please login again."
        super().__init__(
            status_code,
            detail={
                "error": "INVALID_SESSION",
                "code": ErrorCodes.INVALID_SESSION.value,
                "info": message,
            },
            headers=headers,
        )


class ItemNotFoundException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_404_NOT_FOUND,
        message: Optional[str] = None,
        headers: Optional[dict] = None,
    ):
        if not message:
            message = "Item not found."
        super().__init__(
            status_code,
            detail={
                "error": "ITEM_NOT_FOUND",
                "code": ErrorCodes.ITEM_NOT_FOUND.value,
                "info": message,
            },
            headers=headers,
        )
