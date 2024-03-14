from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import get_session
from services.SessionService import check_token
from models.db.Profile import Profile
from models.db.Story import Story
from models.api.StoryAPI import StoryAPI

story_router = APIRouter(prefix='/story', tags=['Story'])

@story_router.get("/", status_code=status.HTTP_200_OK)
async def get(session: AsyncSession = Depends(get_session), token_data: dict = Depends(check_token)):
    """
    Asynchronously fetches stories associated with the user's profiles.

    Args:
        session (AsyncSession): Dependency injection to provide an async session.
        token_data (dict): User token data obtained from the dependency `check_token`.

    Returns:
        List[Story]: A list of Story objects.
    """
    profiles_ids = await session.execute(
        select(Profile.id).where(Profile.user_id == token_data.get('user_id'))
    )
    profiles_ids = profiles_ids.scalars().all()
    
    stories = await session.execute(
        select(Story).filter(Story.profile_id.in_(profiles_ids))
    )
    return stories.scalars().all()

@story_router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_by_id(id: int, session: AsyncSession = Depends(get_session), token_data: dict = Depends(check_token)):
    """
    Asynchronously retrieves a story by its ID.

    Args:
        id (int): The ID of the story to retrieve.
        session (AsyncSession): Dependency injection to provide an async session.
        token_data (dict): User token data obtained from the dependency `check_token`.

    Returns:
        Story: The Story object if found.
    """
    result = await session.get(Story, id)
    if not result:
        raise HTTPException(status_code=404, detail="Story not found")
    return result

@story_router.post("/", status_code=status.HTTP_200_OK)
async def post(data: StoryAPI, session: AsyncSession = Depends(get_session), token_data: dict = Depends(check_token)):
    """
    Asynchronously creates a new story.

    Args:
        data (StoryAPI): The story data to create a new story.
        session (AsyncSession): Dependency injection to provide an async session.
        token_data (dict): User token data obtained from the dependency `check_token`.

    Returns:
        StoryAPI: The created Story object with its new ID.
    """
    instance = Story(
        profile_id=data.profile_id,
        title=data.title,
        synopsis=data.synopsis,
        last_successful_step=data.last_successful_step
    )
    
    session.add(instance)
    await session.commit()
    await session.refresh(instance)
    
    data.id = instance.id
    return data

@story_router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete(id: int, session: AsyncSession = Depends(get_session), token_data: dict = Depends(check_token)):
    """
    Asynchronously deletes a story by its ID after verifying ownership.

    Args:
        id (int): The ID of the story to delete.
        session (AsyncSession): Dependency injection to provide an async session.
        token_data (dict): User token data obtained from the dependency `check_token`.

    Returns:
        dict: A message indicating the outcome of the deletion attempt.
    """
    # Retrieve the story along with its associated profile in a single query
    result = await session.execute(
        select(Story).join(Profile).filter(Story.id == id, Profile.user_id == token_data.get('user_id'))
    )
    story = result.scalars().first()
    
    if not story:
        raise HTTPException(status_code=404, detail="Story not found or not owned by the user")

    await session.delete(story)
    await session.commit()
    
    return {"message": "Story deleted successfully"}