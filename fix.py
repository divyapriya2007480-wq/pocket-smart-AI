import os
code = '''
from datetime import datetime, timedelta
import bcrypt
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
SECRET_KEY = "divya-super-secret-key-12345-pocketsmart"
ALGORITHM = "HS256"
def hash_password(p): return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
def get_password_hash(p): return hash_password(p)
def verify_password(p,h):
    try: return bcrypt.checkpw(p.encode(), h.encode())
    except: return False
def create_access_token(data, expires_delta=None):
    to_encode=data.copy()
    expire=datetime.utcnow()+(expires_delta or timedelta(minutes=60))
    to_encode.update({"exp":expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
def decode_access_token(token):
    try: return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError: return None
def get_current_user(token=Depends(oauth2_scheme), db=Depends(get_db)):
    payload=decode_access_token(token)
    if not payload: raise HTTPException(status_code=401, detail="Could not validate credentials")
    uid=payload.get("sub")
    user=None
    try: user=db.query(models.User).filter(models.User.id==int(uid)).first()
    except: pass
    if not user: user=db.query(models.User).filter(models.User.email==str(uid)).first()
    if not user: raise HTTPException(status_code=401, detail="Could not validate credentials")
    return user
'''
with open("app/security.py","w",encoding="utf-8") as f: f.write(code)
print("security.py fixed")

if os.path.exists("pocketsmart.db"):
    os.remove("pocketsmart.db")
    print("db deleted")
else:
    print("db already gone")

print("DONE DA MA - ipo server start pannu")