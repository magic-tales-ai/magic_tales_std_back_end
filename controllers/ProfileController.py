from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db import get_session
from services.SessionService import check_token
from models.db.Profile import Profile
from models.api.ProfileAPI import ProfileAPI

profile_router = APIRouter(prefix='/profile', tags=['Profile'])

@profile_router.get("/", status_code=status.HTTP_200_OK)
async def get(session: AsyncSession = Depends(get_session), token_data: dict = Depends(check_token)):
    """
    Asynchronously retrieves profiles based on the user ID provided in the token data.

    Args:
        session (AsyncSession): The database session used for the operation.
        token_data (dict): Token data containing the user's identification info.

    Returns:
        List[Profile]: A list of Profile objects associated with the user.
    """
    try:
        result = await session.execute(select(Profile).where(Profile.user_id == token_data.get('user_id')))
        return result.scalars().all()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch profiles: {e}")

@profile_router.get("/{id}", status_code=status.HTTP_200_OK)
async def get_by_id(id: int, session: AsyncSession = Depends(get_session), token_data: dict = Depends(check_token)):
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
            raise HTTPException(status_code=404, detail="Profile not found")
        return result
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch profile by ID: {e}")

@profile_router.post("/", status_code=status.HTTP_201_CREATED)
async def post(data: ProfileAPI, session: AsyncSession = Depends(get_session), token_data: dict = Depends(check_token)):
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
        instance = Profile(
            user_id=data.user_id,
            details=data.details
        )

        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        data.id = instance.id
        return data
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create profile: {e}")
