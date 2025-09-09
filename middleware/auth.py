# auth_tokens.py
import time, hmac, hashlib, base64, os
from typing import Tuple
from fastapi import Request, HTTPException, Depends
from dotenv import load_dotenv
load_dotenv()

SECRET = os.getenv("HMAC_SECRET")  # store in env, not in code
TTL = 60  # 60 seconds

def make_ephemeral_token(TTL: int = TTL) -> str:
    ts = int(time.time())
    payload = f"{ts}:{TTL}".encode("utf-8")
    sig = hmac.new(SECRET.encode(), payload, hashlib.sha256).digest()

    # base64url encode separately
    payload_b64 = base64.urlsafe_b64encode(payload).rstrip(b"=").decode()
    sig_b64 = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()

    token = f"{payload_b64}.{sig_b64}"
    return token


def verify_ephemeral_token(token: str):
    try:
        payload_b64, sig_b64 = token.split(".")
        payload_bytes = base64.urlsafe_b64decode(payload_b64 + "==")
        sig = base64.urlsafe_b64decode(sig_b64 + "==")

        payload_str = payload_bytes.decode("utf-8")
        ts_str, ttl_str = payload_str.split(":")
        ts, ttl = int(ts_str), int(ttl_str)

        expected_sig = hmac.new(SECRET.encode(), payload_bytes, hashlib.sha256).digest()
        if not hmac.compare_digest(expected_sig, sig):
            return False, "invalid signature"

        if abs(int(time.time()) - ts) > ttl:
            return False, "expired"

        return True, "valid"

    except Exception as e:
        return False, f"invalid token: {e}"

def get_token_from_header(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing token")
    return auth.split(" ")[1]