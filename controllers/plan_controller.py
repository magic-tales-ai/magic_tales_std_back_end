from fastapi import APIRouter, status, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select  # Use future select for compatibility with async
from db import get_session, AsyncSession
from models.db.plan import Plan
import logging
import os

from utils.log_utils import get_logger

# Set up logging
logging.basicConfig(level=logging.INFO)
# Get a logger instance for this module
logger = get_logger(__name__)


plan_router = APIRouter(prefix="/plan", tags=["Plan"])


@plan_router.get("/", status_code=status.HTTP_200_OK)
async def get(session: AsyncSession = Depends(get_session)):
    """
    Asynchronously retrieves all plans from the database.

    Args:
        session (AsyncSession): The database session used to execute queries.

    Returns:
        List[Plan]: A list of Plan objects representing all plans found in the database.

    Raises:
        HTTPException: An exception is raised if there is an issue accessing the database or if no plans are found.
    """
    try:
        result = await session.execute(select(Plan))
        plans = result.scalars().all()
        if not plans:
            # If no plans are found, log the event and raise a 404 HTTPException
            logger.info("No plans found in the database.")
            raise HTTPException(status_code=404, detail="No plans found")
        return plans
    except SQLAlchemyError as e:
        # Log the specific database error and raise a 500 HTTPException
        logger.error(f"Database error while fetching plans: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")
    
@plan_router.get("/{id}/image", status_code=status.HTTP_200_OK)
async def get_image_by_plan_id(id: int, session: AsyncSession = Depends(get_session)):
    """
    Asynchronusly get a plan image file by its ID

    Args:
        id (int): The ID of the plan.
        session (AsyncSession): The database session used for the operation.

    Returns:
        FileResponse: The plan image file
    """
    try:
        plan = await session.get(Plan, id)
        plan_images_folder = os.getenv("STATIC_FOLDER") + "/plans"
        
        if plan is None:
            logger.info(f"Plan with ID: {id} not found")
            raise HTTPException(status_code=404, detail="Plan not found")
        
        if not os.path.exists(plan_images_folder):
            raise HTTPException(status_code=404, detail="Plans static folder doesn't exist")
        
        image_path = os.path.join(plan_images_folder, str(id) + ".png")
        
        if not os.path.exists(image_path):
            raise HTTPException(status_code=404, detail="Image not found")
        
        return FileResponse(image_path)
    except HTTPException as e:
        logger.error(e.detail)
        raise HTTPException(status_code=404, detail=e.detail)
    except Exception as e:
        logger.error(f"Images not found.")
        raise HTTPException(status_code=404, detail="Images not found")
