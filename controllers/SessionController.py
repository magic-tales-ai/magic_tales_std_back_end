from fastapi import APIRouter, status, Depends, HTTPException, Form
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import get_session
from services.SessionService import create_access_token, hash_password
from models.api.UserAPI import UserAPI
from models.api.RegisterAPI import RegisterAPI
from models.db.User import User
from models.db.Plan import Plan
import re

session_router = APIRouter(prefix='/session', tags=['Session'])

@session_router.post('/login', status_code=status.HTTP_200_OK)
async def login(user: Annotated[str, Form()], password: Annotated[str, Form()], session: AsyncSession = Depends(get_session)):
    # Hash the password
    hashed_password = hash_password(password)  # Ensure hash_password is suitable for async or doesn't need to be awaited
    
    query = select(User).where(User.password == hashed_password)
    if re.match(r"[^@]+@[^@]+\.[^@]+", user):
        query = query.where(User.email == user)
    else:
        query = query.where(User.username == user)
    
    result = await session.execute(query)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Invalid User or Password")
    
    token_data = {"user_id": user.id, "username": user.username, "email": user.email}
    access_token = create_access_token(token_data)  # Ensure create_access_token is suitable for async or doesn't need to be awaited
    
    response = UserAPI(
        id=user.id,
        username=user.username,
        email=user.email,
        token=f"Bearer {access_token}"
    )
    
    return response

@session_router.post('/register', status_code=status.HTTP_200_OK)
async def register(email: Annotated[str, Form()], username: Annotated[str, Form()], password: Annotated[str, Form()], session: AsyncSession = Depends(get_session)):
    query = select(Plan).where(Plan.name == 'Free Plan')
    result = await session.execute(query)
    free_plan = result.scalars().first()
    
    if not free_plan:
        raise HTTPException(status_code=404, detail="Free plan doesn't exist")
    
    instance = User(
        username=username,
        email=email,
        password=hash_password(password),
        plan_id=free_plan.id
    )
    
    session.add(instance)
    await session.commit()  # Async commit
    
    data = RegisterAPI(
        id=instance.id,
        username=username,
        email=email
    )
    
    return data

@session_router.post('/login-swagger', status_code=status.HTTP_200_OK)
async def login_swagger(username: Annotated[str, Form()], password: Annotated[str, Form()], session: AsyncSession = Depends(get_session)):
    hashed_password = hash_password(password)  # Ensure hash_password is suitable for async or doesn't need to be awaited
    
    query = select(User).where(User.email == username, User.password == hashed_password)
    result = await session.execute(query)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="Invalid Email or Password")
    
    token_data = {"user_id": user.id, "email": user.email}
    access_token = create_access_token(token_data)  # Ensure create_access_token is suitable for async or doesn't need to be awaited
    
    return {"access_token": access_token, "token_type": "bearer"}

@session_router.post('/recover-password', status_code=status.HTTP_200_OK)
async def recover_password(email: Annotated[str, Form()], session: AsyncSession = Depends(get_session)):
    # Assuming you have a function to handle the password recovery process.
    # This is a placeholder implementation. Implement your logic here.
    try:
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Placeholder for sending a password recovery email or similar process.
        # await send_recovery_email(user.email)  # Make sure this is an async operation if it involves IO.
        
        return {"status": "success", "message": "Recovery email sent."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to initiate password recovery: {str(e)}")

