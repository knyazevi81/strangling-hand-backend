from pydantic import BaseModel, EmailStr
from enum import StrEnum
import uuid


# ── Auth tokens ────────────────────────────────────────────────────────────────

class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    type: TokenType
    exp: int


# ── User ───────────────────────────────────────────────────────────────────────

class User(BaseModel):
    id: uuid.UUID
    email: str
    is_active: bool
    is_superuser: bool

    model_config = {"from_attributes": True}


# ── Subscribe ──────────────────────────────────────────────────────────────────

class Subscribe(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    ip: str
    port: str
    payload: str

    model_config = {"from_attributes": True}
