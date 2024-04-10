from typing import List
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.future import select  # Use future select for compatibility with async
from db import get_session, AsyncSession
from models.db.plan import Plan
from models.dto.plan import Plan as PlanDTO
import logging

from utils.log_utils import get_logger

# Set up logging
logging.basicConfig(level=logging.INFO)
# Get a logger instance for this module
logger = get_logger(__name__)


plan_router = APIRouter(prefix="/plan", tags=["Plan"])


@plan_router.get("/", status_code=status.HTTP_200_OK, response_model=List[PlanDTO])
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
