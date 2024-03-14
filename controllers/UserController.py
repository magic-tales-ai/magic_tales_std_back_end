from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import get_session
from sqlalchemy import func
from services.SessionService import check_token
from models.db.Story import Story
from models.db.Profile import Profile
from models.db.User import User
from models.db.Plan import Plan
from datetime import datetime

user_router = APIRouter(prefix='/user', tags=['User'])

@user_router.get("/month-stories-count", status_code=status.HTTP_200_OK)
async def get_month_stories_count(session: AsyncSession = Depends(get_session), token_data: dict = Depends(check_token)):
    """
    Asynchronously counts the stories created by the user in the current month.

    Args:
        session (AsyncSession): The database session for executing queries.
        token_data (dict): The user token data, including user ID.

    Returns:
        dict: A dictionary with the user ID and the count of stories created this month.
    """
    current_month = datetime.now().month
    profiles_result = await session.execute(
        select(Profile.id).where(Profile.user_id == token_data.get('user_id'))
    )
    profiles_ids = profiles_result.scalars().all()
    
    stories_count_result = await session.execute(
        select(func.count(Story.id)).filter(
            Story.profile_id.in_(profiles_ids),
            func.extract('month', Story.created_at) == current_month
        )
    )
    stories_this_month = stories_count_result.scalar()
    
    return { "user_id": token_data.get("user_id"), "stories_this_month": stories_this_month }

@user_router.post("/change-plan/{plan_id}", status_code=status.HTTP_200_OK)
async def change_user_plan(plan_id: int, session: AsyncSession = Depends(get_session), token_data: dict = Depends(check_token)):
    """
    Asynchronously changes the user's plan to a new plan.

    Args:
        plan_id (int): The ID of the new plan to assign to the user.
        session (AsyncSession): The database session for executing queries.
        token_data (dict): The user token data, including user ID.

    Returns:
        bool: True if the plan was changed successfully, False otherwise.
    """
    user = await session.get(User, token_data.get('user_id'))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    plan = await session.get(Plan, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    user.plan_id = plan.id
    await session.commit()
    
    return True
