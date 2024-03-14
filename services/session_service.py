from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import asyncio
from concurrent.futures import ThreadPoolExecutor
import datetime
import jwt
import os
import bcrypt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="session/login-swagger")


async def check_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")]
        )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def create_access_token(data):
    data["exp"] = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
        minutes=int(os.getenv("JWT_EXP_TIME_IN_MINUTES"))
    )
    encoded_jwt = jwt.encode(
        data, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM")
    )
    return encoded_jwt


def refresh_access_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(
            token, os.getenv("JWT_SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")]
        )  # decode method includes validation
        payload["exp"] = datetime.datetime.now(
            tz=datetime.timezone.utc
        ) + datetime.timedelta(minutes=int(os.getenv("JWT_EXP_TIME_IN_MINUTES")))
        encoded_jwt = jwt.encode(
            payload, os.getenv("JWT_SECRET_KEY"), algorithm=os.getenv("JWT_ALGORITHM")
        )
        return encoded_jwt
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


def hash_password(password: str) -> str:
    """
    Hashes a password using bcrypt.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    # bcrypt uses its own internally generated salt
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against the hashed version.

    Args:
        plain_password (str): The plain text password to verify.
        hashed_password (str): The hashed password to verify against.

    Returns:
        bool: True if the verification passed, False otherwise.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


executor = ThreadPoolExecutor()


async def hash_password_async(password: str) -> str:
    loop = asyncio.get_event_loop()
    hashed_password = await loop.run_in_executor(executor, hash_password, password)
    return hashed_password


async def verify_password_async(plain_password: str, hashed_password: str) -> bool:
    loop = asyncio.get_event_loop()
    is_valid = await loop.run_in_executor(
        executor, verify_password, plain_password, hashed_password
    )
    return is_valid
