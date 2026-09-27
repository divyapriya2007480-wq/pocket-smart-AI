from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.security import decode_access_token, oauth2_scheme
from app import models

def get_session_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    if token.startswith("Bearer "):
        token = token[7:]
    payload = decode_access_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    try:
        # Try both id and email
        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        if not user:
            user = db.query(models.User).filter(models.User.email == str(user_id)).first()
        return user
    except:
        # if sub is email, int() will fail - so search by email
        try:
            user = db.query(models.User).filter(models.User.email == str(user_id)).first()
            return user
        except:
            return None

def require_session_user(request: Request, db: Session = Depends(get_db)):
    user = get_session_user(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_303_SEE_OTHER, headers={"Location": "/login"})
    return user

def require_api_user(request: Request, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    # For API routes, check Authorization header or cookie
    auth = request.headers.get("Authorization")
    final_token = None
    if auth and auth.startswith("Bearer "):
        final_token = auth[7:]
    else:
        final_token = request.cookies.get("access_token") or token

    if not final_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    if final_token.startswith("Bearer "):
        final_token = final_token[7:]

    payload = decode_access_token(final_token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token")

    try:
        user = db.query(models.User).filter(models.User.id == int(user_id)).first()
        if not user:
            user = db.query(models.User).filter(models.User.email == str(user_id)).first()
    except:
        user = db.query(models.User).filter(models.User.email == str(user_id)).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user