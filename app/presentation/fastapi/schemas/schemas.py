from pydantic import BaseModel, EmailStr, Field
import uuid


# ── Auth ───────────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# ── User ───────────────────────────────────────────────────────────────────────

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    is_active: bool
    is_superuser: bool


class UsersListResponse(BaseModel):
    users: list[UserResponse]
    total: int


class AdminChangePasswordRequest(BaseModel):
    user_id: uuid.UUID
    new_password: str = Field(min_length=8, max_length=128)


class ChangeMyPasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, max_length=128)


# ── Subscribe ──────────────────────────────────────────────────────────────────

class SubscribeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    ip: str
    port: str
    payload: str


class SubscribesListResponse(BaseModel):
    subscribes: list[SubscribeResponse]
    total: int


class CreateSubscribeRequest(BaseModel):
    user_id: uuid.UUID
    ip: str
    port: str
    payload_template: str = Field(
        description="Шаблон с {ip} и {port} плейсхолдерами",
        examples=["vless://uuid@{ip}:{port}?security=reality&sni=max.ru&...#savebit"]
    )


class UpdateSubscribeRequest(BaseModel):
    ip: str | None = None
    port: str | None = None
    payload_template: str | None = None


# ── Notifications ──────────────────────────────────────────────────────────────

class SendToAllRequest(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=5000)


class SendToUserRequest(BaseModel):
    user_id: uuid.UUID
    subject: str = Field(min_length=1, max_length=200)
    message: str = Field(min_length=1, max_length=5000)


class NotificationSentResponse(BaseModel):
    sent_to: int
    message: str


# ── Common ────────────────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
