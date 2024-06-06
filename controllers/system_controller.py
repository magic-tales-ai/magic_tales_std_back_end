from typing import List
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from magic_tales_models.models.language import Language
from models.dto.language import Language as LanguageDTO
from db import get_session, AsyncSession
from sqlalchemy.future import select # Use future select for compatibility with async
from sqlalchemy import asc
import logging
from utils.log_utils import get_logger

# Set up logging
logging.basicConfig(level=logging.INFO)
# Get a logger instance for this module
logger = get_logger(__name__)

system_router = APIRouter(prefix="/system", tags=["System"])

@system_router.get("/languages", status_code=status.HTTP_200_OK, response_model=List[LanguageDTO])
async def languages(session: AsyncSession = Depends(get_session)):
    """_summary_
    Asynchronously retrieves all languages from the database.

    Args:
        session (AsyncSession): The database session used to execute queries.

    Returns:
        List[Language]: A list of Language objects representing all languages found in the database.

    Raises:
        HTTPException: An exception is raised if there is an issue accessing the database or if no languages are found.
    """
    try:
        result = await session.execute(select(Language).order_by(asc(Language.name)))
        languages = result.scalars().all()
        if not languages:
            # If no languages are found, log the event and raise a 404 HTTPException
            logger.info("No languages found in the database.")
            raise HTTPException(status_code=404, detail="No languages found")
            
        return languages
    except SQLAlchemyError as e:
        # Log the specific database error and raise a 500 HTTPException
        logger.error(f"Database error while fetching languages: {e}")
        raise HTTPException(status_code=500, detail="Database error occurred")