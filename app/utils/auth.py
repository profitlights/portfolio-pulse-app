"""Supabase authentication helpers."""
from __future__ import annotations

import os
from functools import lru_cache

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import Client, create_client

security_scheme = HTTPBearer(auto_error=False)


def _build_client() -> Client | None:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_ANON_KEY")
    if not url or not key:
        return None
    return create_client(url, key)


@lru_cache(maxsize=1)
def get_supabase_client() -> Client | None:
    try:
        return _build_client()
    except Exception:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security_scheme),
):
    client = get_supabase_client()
    allow_anon = os.getenv("ALLOW_ANON", "false").lower() == "true"
    if client is None:
        if allow_anon:
            return {"id": "anon-user"}
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase credentials are not configured.",
        )
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token.")
    try:
        user = client.auth.get_user(credentials.credentials)
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Supabase token.") from exc
    if user is None or user.user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Supabase user.")
    return {"id": user.user.id}
