from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import datetime
import hashlib
import jwt
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="session/login-swagger")

async def check_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
def create_access_token(data):
    data["exp"] = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=int(os.getenv("JWT_EXP_TIME_IN_MINUTES")))
    encoded_jwt = jwt.encode(data, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM"))
    return encoded_jwt

def refresh_access_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")]) # decode method includes validation
        payload["exp"] = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=int(os.getenv("JWT_EXP_TIME_IN_MINUTES")))
        encoded_jwt = jwt.encode(payload, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM"))
        return encoded_jwt
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def hash_password(password: str):
    hash_object = hashlib.sha256()
    hash_object.update(password.encode())
    hashed_password = hash_object.hexdigest()
    
    return hashed_password