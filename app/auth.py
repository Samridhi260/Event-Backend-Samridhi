""" from fastapi import Header, HTTPException
from typing import Optional
from firebase_admin import auth as admin_auth

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = authorization.split(" ", 1)[1]
    try:
        decoded = admin_auth.verify_id_token(token)  # works with Auth emulator
        return decoded  # contains 'uid'
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {e}") """


from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth as admin_auth

bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)
):
    if credentials is None or (credentials.scheme or "").lower() != "bearer":
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    token = credentials.credentials
    try:
        decoded = admin_auth.verify_id_token(token)
        return decoded  # contains 'uid'
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {e}")
