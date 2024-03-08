from fastapi import APIRouter, status, Depends
from db import get_session
from services.SessionService import check_token
from sqlalchemy.orm import Session
from sqlalchemy import select
from models.db.Profile import Profile
from models.api.ProfileAPI import ProfileAPI

profile_router = APIRouter(prefix='/profile', tags=['Profile'])

@profile_router.get("/", status_code=status.HTTP_200_OK)
def get(session: Session = Depends(get_session), token_data: dict = Depends(check_token)):
    return session.execute(select(Profile).where(Profile.user_id == token_data.get('user_id'))).scalars().all()

@profile_router.get("/{id}", status_code=status.HTTP_200_OK)
def get_by_id(id, session: Session = Depends(get_session), token_data: dict = Depends(check_token)):
    return session.get(Profile, id)

@profile_router.post("/", status_code=status.HTTP_200_OK)
def post(data: ProfileAPI, session: Session = Depends(get_session), token_data: dict = Depends(check_token)):
    instance = Profile (
        user_id = data.user_id,
        details = data.details
    )
    
    session.add(instance)
    session.commit()
    
    data.id = instance.id
    
    return data