import pytest
from app.utils.hash_utils import HashUtils
from app.utils.jwt_utils import JWTUtils
from datetime import timedelta


def test_hash_and_verify():
    pw = "myS3cret!"
    hashed = HashUtils.hash_password(pw)
    assert hashed != pw
    assert HashUtils.verify_password(pw, hashed)
    assert not HashUtils.verify_password("wrong", hashed)


def test_jwt_create_and_decode():
    payload = {"admin_id": "testid", "email": "a@b.com", "organization_name": "org1"}
    token = JWTUtils.create_access_token(payload, expires_delta=timedelta(seconds=60))
    assert isinstance(token, str) and len(token) > 0

    decoded = JWTUtils.decode_access_token(token)
    assert decoded.admin_id == payload["admin_id"]
    assert decoded.email == payload["email"]
    assert decoded.organization_name == payload["organization_name"]
