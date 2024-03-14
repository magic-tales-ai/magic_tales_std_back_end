from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession  # Import AsyncSession
from sqlalchemy.future import select  # Use future select for compatibility with async
from db import get_session 
from models.db.Plan import Plan

plan_router = APIRouter(prefix='/plan', tags=['Plan'])

@plan_router.get("/", status_code=status.HTTP_200_OK)
async def get(session: AsyncSession = Depends(get_session)):
    """
    Asynchronously retrieves all plans from the database.

    Args:
        session (AsyncSession, optional): The database session used to execute queries. 
            Defaults to Depends(get_session), which is a dependency that provides an async session.

    Returns:
        List[Plan]: A list of Plan objects representing all plans found in the database.
    
    Raises:
        HTTPException: An exception is raised if there is a database access issue, encapsulating the error within an HTTP response.
    """
    try:
        # Execute the query asynchronously
        result = await session.execute(select(Plan))
        plans = result.scalars().all()
        return plans
    except Exception as e:
        # Log the exception here (e.g., using logging library)
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching plans: {e}")
