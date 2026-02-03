"""Auth stub: when DISABLE_AUTH=TRUE, by default for portfolio, always returns dev user. No Firebase."""

import os
from typing import Dict, Any
from fastapi import HTTPException, status


def get_user_from_token(auth_header: str) -> Dict[str, Any]:
    """Returns user info. If DISABLE_AUTH=TRUE or DEVELOPMENT=true, returns dev user without validating token."""
    if (
        os.getenv("DISABLE_AUTH", "TRUE").upper() == "TRUE"
        or os.getenv("DEVELOPMENT", "true").lower() == "true"
    ):
        return {
            "uid": os.getenv("DEV_UID", "portfolio-dev"),
            "email": os.getenv("DEV_EMAIL", "dev@portfolio.demo"),
            "email_verified": True,
            "custom_claims": {"dev": True},
        }
    if not auth_header or not auth_header.strip().lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    # Portfolio demo: no real Firebase; require DISABLE_AUTH for unauthenticated demo
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Auth disabled: set DISABLE_AUTH=TRUE for demo",
    )
