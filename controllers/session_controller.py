from fastapi import APIRouter, status, Depends, HTTPException, Form
from typing import Annotated
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from db import get_session, AsyncSession
from services.session_service import (
    create_access_token,
    hash_password_async,
    verify_password,
)
from models.api.user_api import UserAPI
from models.api.register_api import RegisterAPI
from models.db.user import User
from models.db.plan import Plan
import re
import logging

from utils.log_utils import get_logger
from db import transaction_context

# Set up logging
logging.basicConfig(level=logging.INFO)
# Get a logger instance for this module
logger = get_logger(__name__)


session_router = APIRouter(prefix="/session", tags=["Session"])

# NOTE: User Input Validation: Ensure that user inputs (e.g., email, username) are validated according to your application's requirements before processing. This includes checks for proper formatting, length, and potentially malicious content to prevent injection attacks.


@session_router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    user: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: AsyncSession = Depends(get_session),
):
    """
    Asynchronously logs in a user.

    Args:
        user (str): User's email or username.
        password (str): User's password.
        session (AsyncSession): The database session for executing queries.

    Returns:
        UserAPI: User information along with an access token.
    """

    # Prepare query to find user by email or username
    if re.match(r"[^@]+@[^@]+\.[^@]+", user):
        query = select(User).where(User.email == user)
    else:
        query = select(User).where(User.username == user)

    # Execute query
    result = await session.execute(query)
    user = result.scalars().first()

    # Verify user exists and password is correct
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=404, detail="Invalid User or Password")

    # Prepare and send response
    token_data = {"user_id": user.id, "username": user.username, "email": user.email}
    access_token = create_access_token(token_data)

    response = UserAPI(
        id=user.id,
        name=user.name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        token=f"Bearer {access_token}",
    )

    return response


@session_router.post("/register", status_code=status.HTTP_200_OK)
async def register(
    name: Annotated[str, Form()],
    last_name: Annotated[str, Form()],
    email: Annotated[str, Form()],
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: AsyncSession = Depends(get_session),
):
    """
    Asynchronously registers a new user with proper transaction management.

    Args:
        email (str): The email of the user to register.
        username (str): The desired username of the new user.
        password (str): The password for the new user account.
        session (AsyncSession): Injected database session for executing asynchronous database operations.

    Returns:
        RegisterAPI: The registered user's information, including the new user ID.
    """
    try:
        logger.debug("Starting transaction...")
        async with transaction_context(session):
            result = await session.execute(select(Plan).where(Plan.name == "Free Plan"))
            free_plan = result.scalars().first()

            if not free_plan:
                logger.error("Free plan doesn't exist")
                raise HTTPException(status_code=404, detail="Free plan doesn't exist")

            hashed_password = await hash_password_async(password)

            new_user = User(
                name=name,
                last_name=last_name,
                username=username,
                email=email,
                password=hashed_password,
                plan_id=free_plan.id,
            )

            session.add(new_user)
            # The transaction will be committed at the end of the async with block
            # No need to explicitly call commit here
        logger.debug("Transaction committed.")
        await session.refresh(new_user)

        logger.info(f"Registered new user: {username}")

        return RegisterAPI(
            id=new_user.id, name=new_user.name, last_name=new_user.last_name, username=new_user.username, email=new_user.email
        )

    except Exception as e:
        logger.error(f"Failed to register user: {e}")
        await session.rollback()  # Explicit rollback in case of error
        raise HTTPException(status_code=500, detail="Failed to register user")


@session_router.post("/login-swagger", status_code=status.HTTP_200_OK)
async def login_swagger(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: AsyncSession = Depends(get_session),
):
    """
    Asynchronously logs in a user for Swagger UI.

    Args:
        username (str): User's email.
        password (str): User's plaintext password.
        session (AsyncSession): Dependency injection of an asynchronous database session.

    Returns:
        dict: A dictionary containing the "access_token" and "token_type".
    """
    try:
        logger.debug("Starting transaction...")
        async with transaction_context(session):
            query = select(User).where(User.email == username)
            result = await session.execute(query)
            user = result.scalars().first()

            # Verify user exists and password is correct
            if not user or not verify_password(password, user.password):
                raise HTTPException(status_code=404, detail="Invalid User or Password")

            # Generate an access token upon successful authentication.
            token_data = {"user_id": user.id, "email": user.email}
            access_token = create_access_token(token_data)

        # Transaction is committed here at the end of the `async with` block.
        logger.debug("Transaction committed.")

        return {"access_token": access_token, "token_type": "bearer"}
    except SQLAlchemyError as e:
        await session.rollback()  # Rollback in case of any error
        logger.error(f"Database error during login-swagger: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to login due to internal server error"
        )


@session_router.post("/recover-password", status_code=status.HTTP_200_OK)
async def recover_password(
    email: Annotated[str, Form()], session: AsyncSession = Depends(get_session)
):
    """
    Asynchronously handles the password recovery process by verifying the user's email
    and initiating the sending of a recovery email.

    Args:
        email (str): The email address to recover the password for.
        session (AsyncSession): The database session for executing queries.

    Returns:
        dict: A message indicating the outcome of the password recovery attempt.
    """
    try:
        logger.debug("Starting transaction...")
        async with transaction_context(session):
            query = select(User).where(User.email == email)
            result = await session.execute(query)
            user = result.scalars().first()

            if not user:
                raise HTTPException(status_code=404, detail="User not found")

        logger.debug("Transaction committed.")

        # TODO: The actual sending of a recovery email should be implemented here.
        # It's assumed to be an asynchronous operation.
        # E.g., await send_recovery_email(user.email)
        # This placeholder indicates success for demonstration purposes.
        # Asynchronous Email Sending: For the password recovery functionality, let's consider using a dedicated asynchronous task queue (e.g., Celery with an asyncio-compatible broker) for sending emails. This approach decouples email sending from request processing, improving scalability and fault tolerance.
        return {"status": "success", "message": "Recovery email sent."}
    except SQLAlchemyError as e:
        logger.error(f"Database error during password recovery: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to initiate password recovery due to internal server error",
        )
    except Exception as e:
        logger.error(f"Unexpected error during password recovery: {e}")
        raise HTTPException(
            status_code=500, detail=f"Failed to initiate password recovery: {str(e)}"
        )
