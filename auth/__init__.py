"""Optional auth for portfolio. When DISABLE_AUTH=TRUE, returns a dev user. TRUE is the default."""

from .auth_stub import get_user_from_token

__all__ = ["get_user_from_token"]
