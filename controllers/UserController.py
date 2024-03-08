from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import extract
from db import get_session
from sqlalchemy import select, func
from services.SessionService import check_token
from models.db.Story import Story
from models.db.Profile import Profile
from models.db.User import User
from models.db.Plan import Plan
from datetime import datetime

user_router = APIRouter(prefix='/user', tags=['User'])

@user_router.get("/month-stories-count", status_code=status.HTTP_200_OK)
def get_month_stories_count(session: Session = Depends(get_session), token_data: dict = Depends(check_token)):
    profiles_ids = session.execute(select(Profile.id).where(Profile.user_id == token_data.get('user_id'))).scalars().all()
    stories_this_month = session.query(Story).filter(Story.profile_id.in_(profiles_ids)).filter(extract('month', Story.created_at) == datetime.now().month).count()
    
    return { "user_id": token_data.get("user_id"), "stories_this_month": stories_this_month }

@user_router.post("/change-plan/{plan_id}", status_code=status.HTTP_200_OK)
def change_user_plan(plan_id, session: Session = Depends(get_session), token_data: dict = Depends(check_token)):
    user = session.get(User, token_data.get('user_id'))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    plan = session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    user.plan_id = plan.id
    session.commit()
    
    return True