from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from db.supabase_client import SupabaseClient

security = HTTPBearer(auto_error=False)
supabase = SupabaseClient()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
        )

    token = credentials.credentials
    try:
        res = supabase.get_client().auth.get_user(token)
        user = getattr(res, "user", None)
        if not user:
            raise ValueError("Invalid token")
        return {"id": user.id, "email": user.email}
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def require_user_match(path_user_id: str, current_user: dict) -> None:
    if path_user_id != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: user mismatch",
        )