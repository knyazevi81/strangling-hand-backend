class AppException(Exception):
    code: int = 400
    message: str = "Application error"

    def __init__(self, message: str | None = None):
        self.message = message or self.__class__.message
        super().__init__(self.message)


# ── Auth ───────────────────────────────────────────────────────────────────────

class InvalidCredentialsError(AppException):
    code = 401
    message = "Invalid email or password"


class TokenExpiredError(AppException):
    code = 401
    message = "Token has expired"


class NotAuthenticatedError(AppException):
    code = 401
    message = "Not authenticated"


class ForbiddenError(AppException):
    code = 403
    message = "Forbidden"


# ── User ───────────────────────────────────────────────────────────────────────

class UserAlreadyExistsError(AppException):
    code = 409
    message = "User with this email already exists"


class UserNotFoundError(AppException):
    code = 404
    message = "User not found"


class UserInactiveError(AppException):
    code = 403
    message = "User account is not activated yet"


# ── Subscribe ──────────────────────────────────────────────────────────────────

class SubscribeNotFoundError(AppException):
    code = 404
    message = "Subscribe not found"


class SubscribeAlreadyExistsError(AppException):
    code = 409
    message = "Subscribe already exists for this user"
