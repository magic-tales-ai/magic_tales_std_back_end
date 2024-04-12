from typing import Annotated, Optional
from fastapi import APIRouter, File, Form, UploadFile, status, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from db import get_session, transaction_context
from services.session_service import check_token, verify_password_async, hash_password_async
from services.email_service import send_email
from services.image_service import save_image_as_png
from services.user_service import check_validation_code
from models.db.story import Story
from models.db.profile import Profile
from models.db.user import User
from models.db.plan import Plan
from datetime import datetime
import logging
import os
import random

from utils.log_utils import get_logger

# Set up logging
logging.basicConfig(level=logging.INFO)
# Get a logger instance for this module
logger = get_logger(__name__)


user_router = APIRouter(prefix="/user", tags=["User"])


@user_router.get("/month-stories-count", status_code=status.HTTP_200_OK)
async def get_month_stories_count(
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(check_token),
):
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
        select(Profile.id).where(Profile.user_id == token_data.get("user_id"))
    )
    profiles_ids = profiles_result.scalars().all()

    stories_count_result = await session.execute(
        select(func.count(Story.id)).filter(
            Story.profile_id.in_(profiles_ids),
            func.extract("month", Story.created_at) == current_month,
        )
    )
    stories_this_month = stories_count_result.scalar()

    return {
        "user_id": token_data.get("user_id"),
        "stories_this_month": stories_this_month,
    }


@user_router.post("/change-plan/{plan_id}", status_code=status.HTTP_200_OK)
async def change_user_plan(
    plan_id: int,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(check_token),
):
    """
    Asynchronously changes the user's plan to a new plan.

    Args:
        plan_id (int): The ID of the new plan to assign to the user.
        session (AsyncSession): The database session for executing queries.
        token_data (dict): The user token data, including user ID.

    Returns:
        bool: True if the plan was changed successfully, False otherwise.
    """
    try:
        logger.debug("Starting transaction...")
        async with transaction_context(session):
            user = await session.get(User, token_data.get("user_id"))
            if not user:
                logger.error(f"User {token_data.get('user_id')} not found")
                raise HTTPException(status_code=404, detail="User not found")

            plan = await session.get(Plan, plan_id)
            if not plan:
                logger.error(f"Plan {plan_id} not found")
                raise HTTPException(status_code=404, detail="Plan not found")

            user.plan_id = plan.id
            # Transaction will be automatically committed here
        logger.debug("Transaction committed.")
        logger.info(f"User {user.id}'s plan changed to {plan.id}")
        return True

    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Failed to change user plan: {e}")
        raise HTTPException(status_code=500, detail="Failed to change plan")

@user_router.post("/update", status_code=status.HTTP_200_OK)
async def update_user(
    name: str = Form(None),
    last_name: str = Form(None),
    email: str = Form(None),
    username: str = Form(None),
    image: UploadFile = File(None),
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(check_token)
):
    """
    Asynchronusly update user data (name, last_name, email, username, image)

    Args:
        email (str, optional): The new email to assign to the user.
        username (str, optional): The new username to assign to the user.
        image (UploadFile, optional): The image to upload.
        session (AsyncSession): The database session for executing queries.
        token_data (dict): The user token data, including user ID.

    Returns:
        bool: True if the data (name, last_name, email, username, image) was change successfully.
    """
    try:
        logger.debug("Starting transaction...")
        async with transaction_context(session):
            user = await session.get(User, token_data.get("user_id"))
            
            if not user:
                logger.error(f"User {token_data.get('user_id')} not found")
                raise HTTPException(status_code=404, detail="User not found")
            
            if name is not None and name != user.name:
                user.name = name
                
            if last_name is not None and last_name != user.last_name:
                user.last_name = last_name
            
            if email is not None and email != user.email:
                exist_email = await session.execute(
                    select(User).where(User.email == email).where(User.id != user.id)
                )
                exist_email = exist_email.scalars().all()
                
                if exist_email is not None and len(exist_email) > 0:
                    raise HTTPException(status_code=422, detail="Email is in use.")
                
                # Generate new validation_code
                user.validation_code = random.randint(100000, 999999)
                # Send validation_code email to old email
                await send_email(user.email, "Magic Tales - Change email", f"The validation code is: {user.validation_code}")
                
                user.new_email = email
                
            if username is not None and username != user.username:
                exist_username = await session.execute(
                    select(User).where(User.username == username).where(User.id != user.id)
                )
                exist_username = exist_username.scalars().all()
                
                if exist_username is not None and len(exist_username) > 0:
                    raise HTTPException(status_code=422, detail="Username is in use.")
                
                user.username = username
                
            if image is not None:
                allowed_extensions = { '.jpg', '.jpeg', 'png' }
                filename, ext = os.path.splitext(image.filename)
                
                if ext.lower() not in allowed_extensions:
                    raise HTTPException(status_code=400, detail="File must be .jpg, .jpeg or .png")
                
                save_image_as_png("/users", image, user.id)
            # Transaction will be automatically committed here
        logger.debug("Transaction committed.")
        return True
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Failed to update user settings: {e}")
        raise HTTPException(status_code=500, detail="Failed to update settings")
    
@user_router.post("/change-email-validate", status_code=status.HTTP_200_OK)
async def change_email_validation(
    validation_code: Annotated[int, Form()],
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(check_token)
):
    """
    Asynchronusly check validation code to change email. Change the email if the validation code is valid

    Args:
        validation_code (int): The validation code that the user received by email.
        session (AsyncSession): The database session for executing queries.
        token_data (dict): The user token data, including user ID.

    Returns:
        bool: True if the email was validate successfully.
    """
    try:
        logger.debug("Starting transaction...")
        async with transaction_context(session):
            user = await session.get(User, token_data.get("user_id"))
            if not user:
                logger.error(f"User {token_data.get('user_id')} not found")
                raise HTTPException(status_code=404, detail="User not found")
            
            if not check_validation_code(validation_code, user.validation_code):
                raise HTTPException(status_code=422, detail="Validation code is not valid")
            
            user.email = user.new_email
            user.new_email = None
            user.validation_code = None
            # Transaction will be automatically committed here
        logger.debug("Transaction committed.")
        return True
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Failed to validate user email: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate email")
    
@user_router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    old_password: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
    repeated_new_password: Annotated[str, Form()],
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(check_token)
):
    """
    Asynchronusly change the user password

    Args:
        old_password (str): The actual user password
        new_password (str): The new user password
        repeated_new_password (str): The repeated new user password for validation
        session (AsyncSession): The database session for executing queries.
        token_data (dict): The user token data, including user ID.

    Returns:
        bool: True if the password was change successfully
    """
    try:
        logger.debug("Starting transaction...")
        async with transaction_context(session):
            user = await session.get(User, token_data.get("user_id"))
            if not user:
                logger.error(f"User {token_data.get('user_id')} not found")
                raise HTTPException(status_code=404, detail="User not found")
            
            if not await verify_password_async(old_password, user.password):
                logger.error(f"Old password '{old_password}' is not valid")
                raise HTTPException(status_code=422, detail="Old password is not valid")
            
            if new_password != repeated_new_password:
                logger.error(f"The new_password '{new_password}' and repeated_new_password '{repeated_new_password}' aren't the same")
                raise HTTPException(status_code=422, detail="The new password and repeated new password must be the same")
            
            user.password = await hash_password_async(new_password)
            # Transaction will be automatically committed here
        logger.debug("Transaction committed.")
        return True
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Failed to change user password: {e}")
        raise HTTPException(status_code=500, detail="Failed to change password")
    
@user_router.post("/resend-validation-code", status_code=status.HTTP_200_OK)
async def resend_validation_code(
    email: Annotated[str, Form()],
    session: AsyncSession = Depends(get_session)
):
    """
    Asynchronusly resend the validation code to the user email

    Args:
        email (str): The email to send the new validation code
        session (AsyncSession): The database session for executing queries.

    Returns:
        bool: True if the email was send successfully
    """
    try:
        logger.debug("Starting transaction...")
        async with transaction_context(session):
            user = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
            if not user:
                logger.error(f"User {email} not found")
                raise HTTPException(status_code=404, detail="User not found")
            
            # Generate new validation_code
            user.validation_code = random.randint(100000, 999999)
            # Send validation_code email to old email
            await send_email(user.email, "Magic Tales - New validation code", f"The validation code is: {user.validation_code}")
        
            # Transaction will be automatically committed here
        logger.debug("Transaction committed.")
        return True
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Failed to change user password: {e}")
        raise HTTPException(status_code=500, detail="Failed to change password")