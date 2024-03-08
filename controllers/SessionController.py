from fastapi import APIRouter, status, Depends, HTTPException, Form
from typing import Annotated
from db import get_session
from sqlalchemy.orm import Session
from sqlalchemy import select, exc
from services.SessionService import create_access_token, hash_password
from models.api.UserAPI import UserAPI
from models.api.RegisterAPI import RegisterAPI
from models.db.User import User
from models.db.Plan import Plan
import re

session_router = APIRouter(prefix='/session', tags=['Session'])

@session_router.post('/login', status_code=status.HTTP_200_OK)
def login(user: Annotated[str, Form()], password: Annotated[str, Form()], session: Session = Depends(get_session)):

    if (re.match(r"[^@]+@[^@]+\.[^@]+", user)):
        user = session.execute(select(User).where(User.email == user).where(User.password == hash_password(password))).scalars().first()
    else:
        user = session.execute(select(User).where(User.username == user).where(User.password == hash_password(password))).scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Invalid User or Password")
    
    token_data = { "user_id": user.id, "username": user.username, "email": user.email }
    access_token = create_access_token(token_data)
    
    response = UserAPI(
        id = user.id,
        username = user.username,
        email = user.email,
        token = f"Bearer {access_token}"
    )
    
    return response

@session_router.post('/login-swagger', status_code=status.HTTP_200_OK)
def login_swagger(username: Annotated[str, Form()], password: Annotated[str, Form()], session: Session = Depends(get_session)):
    user = session.execute(select(User).where(User.email == username).where(User.password == hash_password(password))).scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Invalid Email or Password")
    
    token_data = { "user_id": user.id, "email": user.email }
    access_token = create_access_token(token_data)
    
    return { "access_token": access_token, "token_type": "bearer" }
    
@session_router.post('/register', status_code=status.HTTP_200_OK)
def register(email: Annotated[str, Form()], username: Annotated[str, Form()], password: Annotated[str, Form()], session: Session = Depends(get_session)):
    free_plan = session.execute(select(Plan).where(Plan.name == 'Free Plan')).scalars().first()
    
    if not free_plan:
        raise HTTPException(status_code=404, detail="Free plan doesn't exist")

    instance = User(
        username = username,
        email = email,
        password = hash_password(password),
        plan_id = free_plan.id
    )
    
    session.add(instance)
    session.commit()
    
    data = RegisterAPI(
        id = instance.id,
        username = username,
        email = email
    )
    
    return data
        

@session_router.post('/recover-password', status_code=status.HTTP_200_OK)
def recover_password():
    return 