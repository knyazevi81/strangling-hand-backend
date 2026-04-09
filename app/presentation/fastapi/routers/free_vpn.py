from typing import Annotated

import httpx
import random
from urllib.parse import urlparse, parse_qs

from fastapi import APIRouter, Depends

from app.domain.models.models import User
from app.domain.exceptions.base import AppException
from app.presentation.fastapi.dependencies import get_current_user

router = APIRouter(prefix="/free-vpn", tags=["free-vpn"])

SOURCE_URL = (
    "https://raw.githubusercontent.com/kort0881/vpn-vless-configs-russia"
    "/refs/heads/main/githubmirror/ru-sni-local/vless.txt"
)


def _is_valid(line: str) -> bool:
    """Оставляем только vless:// с security=reality."""
    line = line.strip()
    if not line.startswith("vless://"):
        return False
    try:
        parsed = urlparse(line)
        params = parse_qs(parsed.query)
        security = params.get("security", [""])[0]
        return security == "reality"
    except Exception:
        return False


@router.get(
    "/configs",
    summary="Банк бесплатных VPN подключений (только для активных пользователей)",
    response_model=list[dict],
)
async def get_free_configs(
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[dict]:
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(SOURCE_URL)
            response.raise_for_status()
    except Exception as exc:
        raise AppException("Не удалось получить список подключений") from exc

    lines = response.text.splitlines()
    valid = [line.strip() for line in lines if _is_valid(line)]

    # возвращаем 50 случайных уникальных
    sample = random.sample(valid, min(50, len(valid)))

    return [{"url": url} for url in sample]
