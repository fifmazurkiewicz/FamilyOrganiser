from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ForbiddenError(HTTPException):
    def __init__(self, detail: str = "Access denied") -> None:
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthorizedError(HTTPException):
    def __init__(self, detail: str = "Not authenticated") -> None:
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)


class ConflictError(HTTPException):
    def __init__(self, detail: str = "Resource already exists") -> None:
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)


class BusinessLogicError(HTTPException):
    def __init__(self, detail: str) -> None:
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


class GroupLimitExceededError(BusinessLogicError):
    def __init__(self) -> None:
        super().__init__("Family group member limit reached (max 20)")


class AccountLockedError(ForbiddenError):
    def __init__(self) -> None:
        super().__init__("Account is locked. Please contact an administrator.")
