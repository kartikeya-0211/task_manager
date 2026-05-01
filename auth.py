from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
import models, os

SECRET = os.environ.get("SECRET_KEY", "changeme123")
pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer = HTTPBearer()

def hash_password(p): return pwd.hash(p)
def verify_password(p, h): return pwd.verify(p, h)

def create_token(data: dict):
    data["exp"] = datetime.utcnow() + timedelta(hours=72)
    return jwt.encode(data, SECRET, algorithm="HS256")

def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    db: Session = Depends(get_db)
):
    try:
        payload = jwt.decode(creds.credentials, SECRET, algorithms=["HS256"])
        user = db.query(models.User).filter(models.User.id == int(payload["sub"])).first()
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user