"""Unit tests for auth/security helpers."""

from datetime import timedelta

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    hash_security_answer,
    verify_password,
    verify_security_answer,
)


class TestPasswordHashing:
    def test_hash_and_verify_password(self):
        hashed = hash_password("Secret123!")
        assert hashed != "Secret123!"
        assert verify_password("Secret123!", hashed) is True
        assert verify_password("wrong", hashed) is False

    def test_security_answer_is_case_insensitive(self):
        hashed = hash_security_answer("  BlueDog  ")
        assert verify_security_answer("bluedog", hashed) is True
        assert verify_security_answer("BLUEDOG", hashed) is True
        assert verify_security_answer("other", hashed) is False


class TestJwtTokens:
    def test_access_token_roundtrip(self):
        token = create_access_token({"sub": "user-1"}, expires_delta=timedelta(minutes=5))
        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user-1"
        assert payload["type"] == "access"

    def test_refresh_token_type(self):
        token = create_refresh_token({"sub": "user-2"})
        payload = decode_token(token)
        assert payload is not None
        assert payload["type"] == "refresh"
        assert payload["sub"] == "user-2"

    def test_decode_invalid_token(self):
        assert decode_token("not.a.valid.jwt") is None
