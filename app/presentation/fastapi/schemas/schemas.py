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


class ChangePasswordRequest(BaseModel):
    user_id: uuid.UUID
    new_password: str = Field(min_length=8, max_length=128)


# ── Subscribe ──────────────────────────────────────────────────────────────────

class SubscribeResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    ip: str
    port: str
    payload: str  # payload с подставленными ip и port


class SubscribesListResponse(BaseModel):
    subscribes: list[SubscribeResponse]
    total: int


class CreateSubscribeRequest(BaseModel):
    user_id: uuid.UUID
    ip: str
    port: str
    # payload — шаблон, {ip} и {port} будут подставлены автоматически
    # пример: vless://uuid@{ip}:{port}?security=reality&...#rkn-pidarasi-leo-wl
    payload_template: str = Field(
        description="VLESS payload template with {ip} and {port} placeholders",
        examples=["vless://60975a6b-8eb9-413a-b555-7a9e024083d8@{ip}:{port}?security=reality&sni=max.ru&fp=chrome&pbk=7jQJYJL6CuVXCyUsMHLxrAKLvyNs6OPEuWcKNYyltk8&sid=c66fc3a3&spx=/&type=tcp&flow=xtls-rprx-vision&encryption=none#rkn-pidarasi-leo-wl"]
    )


class UpdateSubscribeRequest(BaseModel):
    ip: str | None = None
    port: str | None = None
    payload_template: str | None = None


class MessageResponse(BaseModel):
    message: str
