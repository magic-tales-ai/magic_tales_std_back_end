from typing import List
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db import get_session, transaction_context
from services.session_service import check_token
from models.db.profile import Profile
from models.dto.profile import Profile as ProfileDTO
from models.api.profile_api import ProfileAPI
import logging

from utils.log_utils import get_logger

# Set up logging
logging.basicConfig(level=logging.INFO)
# Get a logger instance for this module
logger = get_logger(__name__)

profile_router = APIRouter(prefix="/profile", tags=["Profile"])


@profile_router.get("/", status_code=status.HTTP_200_OK, response_model=List[ProfileDTO])
async def get(
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(check_token),
):
    """
    Asynchronously retrieves profiles based on the user ID provided in the token data.

    Args:
        session (AsyncSession): The database session used for the operation.
        token_data (dict): Token data containing the user's identification info.

    Returns:
        List[Profile]: A list of Profile objects associated with the user.
    """
    try:
        result = await session.execute(
            select(Profile).where(Profile.user_id == token_data.get("user_id"))
        )
        profiles = result.scalars().all()
        if not profiles:
            logger.info(f"No profiles found for user ID: {token_data.get('user_id')}")
        return profiles
    except SQLAlchemyError as e:
        logger.error(f"Failed to fetch profiles: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")


@profile_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=ProfileDTO)
async def get_by_id(
    id: int,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(check_token),
):
    """
    Asynchronously retrieves a profile by its ID.

    Args:
        id (int): The ID of the profile to retrieve.
        session (AsyncSession): The database session used for the operation.
        token_data (dict): Token data for authentication and authorization.

    Returns:
        Profile: The Profile object if found, otherwise raises HTTPException.
    """
    try:
        result = await session.get(Profile, id)
        if result is None:
            logger.info(f"Profile with ID: {id} not found")
            raise HTTPException(status_code=404, detail="Profile not found")
        return result
    except SQLAlchemyError as e:
        logger.error(f"Failed to fetch profile by ID: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")


@profile_router.post("/", status_code=status.HTTP_201_CREATED)
async def post(
    data: ProfileAPI,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(check_token),
):
    """
    Asynchronously creates a new profile.

    Args:
        data (ProfileAPI): The profile data to create.
        session (AsyncSession): The database session used for the operation.
        token_data (dict): Token data for authentication and authorization.

    Returns:
        ProfileAPI: The created Profile data, including its new ID.
    """
    try:
        logger.debug("Starting transaction...")
        async with transaction_context(session):
            instance = Profile(user_id=data.user_id, details=data.details)
            session.add(instance)
            # The transaction will be committed at the end of the with block
            # if no exceptions occur.
        logger.debug("Transaction committed.")
        # After successful commit, refresh to get the new ID
        await session.refresh(instance)
        data.id = instance.id
        logger.info(
            f"Created new profile with ID: {data.id} for user ID: {data.user_id}"
        )
        return data
    except SQLAlchemyError as e:
        logger.error(f"Failed to create profile: {e}")
        # Rollback is handled automatically if an exception occurs within the with block
        raise HTTPException(status_code=500, detail="Failed to create profile")
