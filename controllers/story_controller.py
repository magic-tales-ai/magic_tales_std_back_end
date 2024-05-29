from typing import List
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from db import get_session, transaction_context
from services.session_service import check_token
from services.files_service import get_image_as_byte_64, get_story_as_file_response
from magic_tales_models.models.profile import Profile
from magic_tales_models.models.story import Story
from models.dto.story import Story as StoryDTO
from models.api.story_api import StoryAPI
import logging

from utils.log_utils import get_logger

# Set up logging
logging.basicConfig(level=logging.INFO)
# Get a logger instance for this module
logger = get_logger(__name__)


story_router = APIRouter(prefix="/story", tags=["Story"])


@story_router.get("/", status_code=status.HTTP_200_OK, response_model=List[StoryDTO])
async def get(
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(check_token),
):
    """
    Asynchronously fetches stories associated with the user's profiles.

    Args:
        session (AsyncSession): Dependency injection to provide an async session.
        token_data (dict): User token data obtained from the dependency `check_token`.

    Returns:
        List[Story]: A list of Story objects.
    """
    try:
        profiles_ids = await session.execute(
            select(Profile.id).where(Profile.user_id == token_data.get("user_id"))
        )
        profiles_ids = profiles_ids.scalars().all()

        stories = await session.execute(
            select(Story).filter(Story.profile_id.in_(profiles_ids))
        )
        stories = stories.scalars().all()
        for story in stories:
            story.profile.image = get_image_as_byte_64('/profiles', story.profile.id)

        return stories
    except SQLAlchemyError as e:
        logger.error(f"Failed to fetch stories: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch stories")


@story_router.get("/{id}", status_code=status.HTTP_200_OK, response_model=StoryDTO)
async def get_by_id(
    id: int,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(check_token),
):
    """
    Asynchronously retrieves a story by its ID.

    Args:
        id (int): The ID of the story to retrieve.
        session (AsyncSession): Dependency injection to provide an async session.
        token_data (dict): User token data obtained from the dependency `check_token`.

    Returns:
        Story: The Story object if found.
    """
    try:
        story = await session.get(Story, id)
        if not story or story.profile.user_id != token_data.get("user_id"):
            raise HTTPException(
                status_code=404, detail="Story not found or access denied"
            )
            
        story.profile.image = get_image_as_byte_64('/profiles', story.profile.id)
        return story
    except SQLAlchemyError as e:
        logger.error(f"Failed to fetch story by ID: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch story by ID")


@story_router.post("/", status_code=status.HTTP_200_OK)
async def post(
    data: StoryAPI,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(check_token),
):
    """
    Asynchronously creates a new story.

    Args:
        data (StoryAPI): The story data to create a new story.
        session (AsyncSession): Dependency injection to provide an async session.
        token_data (dict): User token data obtained from the dependency `check_token`.

    Returns:
        StoryAPI: The created Story object with its new ID.
    """
    try:
        logger.debug("Starting transaction...")
        async with transaction_context(session):
            instance = Story(
                profile_id=data.profile_id,
                title=data.title,
                features=data.features,
                synopsis=data.synopsis,
                last_successful_step=data.last_successful_step,
            )
            session.add(instance)
        logger.debug("Transaction committed.")
        await session.refresh(instance)
        data.id = instance.id
        return data
    except SQLAlchemyError as e:
        await session.rollback()  # Explicit rollback in case of SQLAlchemy errors
        logger.error(f"Failed to create story: {e}")
        raise HTTPException(status_code=500, detail="Failed to create story")


@story_router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete(
    id: int,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(check_token),
):
    """
    Asynchronously deletes a story by its ID after verifying ownership.

    Args:
        id (int): The ID of the story to delete.
        session (AsyncSession): Dependency injection to provide an async session.
        token_data (dict): User token data obtained from the dependency `check_token`.

    Returns:
        dict: A message indicating the outcome of the deletion attempt.
    """
    try:
        logger.debug("Starting transaction...")
        async with transaction_context(session):
            result = await session.execute(
                select(Story)
                .join(Profile)
                .filter(Story.id == id, Profile.user_id == token_data.get("user_id"))
            )
            story = result.scalars().first()
            if not story:
                raise HTTPException(
                    status_code=404, detail="Story not found or not owned by the user"
                )
            session.delete(story)
        logger.debug("Transaction committed.")
        return {"message": "Story deleted successfully"}
    except SQLAlchemyError as e:
        await session.rollback()  # Explicit rollback in case of SQLAlchemy errors
        logger.error(f"Failed to delete story: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete story")

@story_router.get("/{id}/download", status_code=status.HTTP_200_OK)
async def get_by_id(
    id: int,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(check_token),
):
    """
    Asynchronously retrieves a story file by its ID.

    Args:
        id (int): The ID of the story to retrieve.
        session (AsyncSession): Dependency injection to provide an async session.
        token_data (dict): User token data obtained from the dependency `check_token`.

    Returns:
        Story: The Story file if found.
    """
    try:
        story = await session.get(Story, id)
        if not story or story.profile.user_id != token_data.get("user_id"):
            raise HTTPException(
                status_code=404, detail="Story not found or access denied"
            )
        return get_story_as_file_response(story.story_folder)
    except SQLAlchemyError as e:
        logger.error(f"Failed to fetch story by ID: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch story by ID")