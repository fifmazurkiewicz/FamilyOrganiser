from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import httpx
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)

_jwks_cache: dict[str, Any] | None = None
_jwks_fetched_at: float | None = None
_JWKS_TTL_SECONDS = 3600


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_security_answer(answer: str) -> str:
    """Hash security answer (case-insensitive — normalize to lowercase first)."""
    return pwd_context.hash(answer.lower().strip())


def verify_security_answer(plain_answer: str, hashed_answer: str) -> bool:
    return pwd_context.verify(plain_answer.lower().strip(), hashed_answer)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode legacy app JWT (HS256 + SECRET_KEY)."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


def _fetch_jwks() -> dict[str, Any]:
    global _jwks_cache, _jwks_fetched_at
    now = datetime.now(timezone.utc).timestamp()
    if (
        _jwks_cache is not None
        and _jwks_fetched_at is not None
        and now - _jwks_fetched_at < _JWKS_TTL_SECONDS
    ):
        return _jwks_cache

    url = settings.supabase_jwks_url
    if not url:
        return {"keys": []}

    with httpx.Client(timeout=10.0) as client:
        response = client.get(url)
        response.raise_for_status()
        _jwks_cache = response.json()
        _jwks_fetched_at = now
        return _jwks_cache


def decode_supabase_token(token: str) -> Optional[dict]:
    """Verify Supabase access token (JWT secret HS256 and/or JWKS RS256)."""
    if not settings.supabase_auth_enabled:
        return None

    audience = settings.SUPABASE_JWT_AUDIENCE

    if settings.SUPABASE_JWT_SECRET.strip():
        try:
            return jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                audience=audience if audience else None,
                options={
                    "verify_aud": bool(audience),
                    "verify_iss": False,
                },
            )
        except JWTError:
            pass

    if not settings.SUPABASE_URL.strip():
        return None

    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        jwks = _fetch_jwks()
        keys = jwks.get("keys") or []
        jwk = next((k for k in keys if not kid or k.get("kid") == kid), None)
        if not jwk:
            return None
        return jwt.decode(
            token,
            jwk,
            algorithms=[jwk.get("alg") or "RS256", "RS256", "ES256"],
            audience=audience if audience else None,
            options={
                "verify_aud": bool(audience),
                "verify_iss": False,
            },
        )
    except (JWTError, httpx.HTTPError, ValueError, StopIteration):
        return None


def decode_access_token(token: str) -> tuple[Optional[dict], str]:
    """
    Return (payload, mode) where mode is 'supabase' | 'legacy' | 'invalid'.
    Prefers Supabase when configured.
    """
    if settings.supabase_auth_enabled:
        payload = decode_supabase_token(token)
        if payload:
            return payload, "supabase"

    payload = decode_token(token)
    if payload and payload.get("type") == "access":
        return payload, "legacy"

    return None, "invalid"
