from fastapi import APIRouter, status, Depends, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db import get_session, transaction_context
from services.session_service import check_token
from models.db.profile import Profile
from models.api.profile_api import ProfileAPI
import logging
import os

from utils.log_utils import get_logger

# Set up logging
logging.basicConfig(level=logging.INFO)
# Get a logger instance for this module
logger = get_logger(__name__)

profile_router = APIRouter(prefix="/profile", tags=["Profile"])


@profile_router.get("/", status_code=status.HTTP_200_OK)
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


@profile_router.get("/{id}", status_code=status.HTTP_200_OK)
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


@profile_router.post("/{id}/upload-image", status_code=status.HTTP_200_OK)
async def upload_image_by_profile_id(
    id: int,
    image: UploadFile=File(...),
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(check_token),
):
    """
    Asynchronusly upload a profile image by its ID. If image already exists, will be replaced

    Args:
        id (int): The ID of the profile.
        image (UploadFile, optional): The image to upload.
        session (AsyncSession): The database session used for the operation.
        token_data (dict): Token data for authentication and authorization.

    Returns:
        dict: A message indicating the outcome of the uploading attempt.
    """
    try:
        profile = await session.get(Profile, id)
        profiles_folder = os.getenv("STATIC_FOLDER") + "/profiles"
        allowed_extensions = { '.jpg', '.jpeg', 'png' }
        filename, ext = os.path.splitext(image.filename)
        
        if ext.lower() not in allowed_extensions:
            raise HTTPException(status_code=400, detail="File must be .jpg, .jpeg or .png")
        
        if profile is None:
            logger.info(f"Profile with ID: {id} not found")
            raise HTTPException(status_code=404, detail="Profile not found")
        
        # If the folder "static/profiles" doesn't exists, we create
        if not os.path.exists(profiles_folder):
            os.makedirs(profiles_folder)
        
        # Save image (the filename will be the profile id)
        with open(os.path.join(profiles_folder, str(id) + ".png"), "wb") as buffer:
            buffer.write(image.file.read())
            
        return {"message": "Image upload successfully"}
    except SQLAlchemyError as e:
        logger.error(f"Failed to upload image: {e}")
        # Rollback is handled automatically if an exception occurs within the with block
        raise HTTPException(status_code=500, detail="Failed to upload image")
    
@profile_router.get("/{id}/image", status_code=status.HTTP_200_OK)
async def get_image_by_profile_id(
    id: int,
    session: AsyncSession = Depends(get_session),
    token_data: dict = Depends(check_token),
):
    """
    Asynchronusly get a profile image file by its ID

    Args:
        id (int): The ID of the profile.
        session (AsyncSession): The database session used for the operation.
        token_data (dict): Token data for authentication and authorization.

    Returns:
        FileResponse: The profile image file
    """
    try:
        profile = await session.get(Profile, id)
        profiles_folder = os.getenv("STATIC_FOLDER") + "/profiles"
        
        if profile is None:
            logger.info(f"Profile with ID: {id} not found")
            raise HTTPException(status_code=404, detail="Profile not found")
        
        image_path = os.path.join(profiles_folder, str(id) + ".png")
        
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image not found")
        
        return FileResponse(image_path)
    except SQLAlchemyError as e:
        logger.error(f"Failed to get image: {e}")
        # Rollback is handled automatically if an exception occurs within the with block
        raise HTTPException(status_code=500, detail="Failed to get image")

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
