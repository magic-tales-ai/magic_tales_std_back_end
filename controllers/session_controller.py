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
from services.email_service import send_email
from services.image_service import get_image_as_byte_64
from services.user_service import check_validation_code
from models.api.user_api import UserAPI
from models.api.register_api import RegisterAPI
from models.db.user import User
from models.db.plan import Plan
import re
import logging
import random

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
        raise HTTPException(status_code=401, detail="Invalid User or Password")
    
    # Verify if user is active
    if not user.active:
        raise HTTPException(status_code=401, detail="User is not active")

    # Prepare and send response
    token_data = {"user_id": user.id, "username": user.username, "email": user.email}
    access_token = create_access_token(token_data)

    response = UserAPI(
        id=user.id,
        name=user.name,
        last_name=user.last_name,
        username=user.username,
        email=user.email,
        image=get_image_as_byte_64("/users", user.id),
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
            
            user = (await session.execute(select(User).where(User.username == username))).scalar_one_or_none()
            if user:
                logger.error("The username already exists")
                raise HTTPException(status_code=422, detail="The username already exists")

            user = (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
            if user:
                logger.error("The email already exists")
                raise HTTPException(status_code=422, detail="The email already exists")

            hashed_password = await hash_password_async(password)
            validation_code = random.randint(100000, 999999) # Generate validation_code

            new_user = User(
                name=name,
                last_name=last_name,
                username=username,
                email=email,
                password=hashed_password,
                validation_code=validation_code,
                plan_id=free_plan.id,
            )
            
            # Send validation_code email
            await send_email(new_user.email, "Magic Tales - Validate email", f"The validation code is: {new_user.validation_code}")

            session.add(new_user)
            # The transaction will be committed at the end of the async with block
            # No need to explicitly call commit here
        logger.debug("Transaction committed.")
        await session.refresh(new_user)

        logger.info(f"Registered new user: {username}")

        return RegisterAPI(
            id=new_user.id, name=new_user.name, last_name=new_user.last_name, username=new_user.username, email=new_user.email
        )

    except SQLAlchemyError as e:
        logger.error(f"Failed to register user: {e}")
        raise HTTPException(status_code=500, detail="Failed to register user")
    
@session_router.post("/register-validate", status_code=status.HTTP_200_OK)
async def register_validation(
    email: Annotated[str, Form()],
    validation_code: Annotated[int, Form()],
    session: AsyncSession = Depends(get_session),
):
    """
    Validate user's register code

    Args:
        email (Annotated[str, Form): The email of the user to validate.
        validation_code (Annotated[int, Form): The validation code of the user.
        session (AsyncSession): Injected database session for executing asynchronous database operations.

    Returns:
        bool: True if the email was validate successfully.
    """
    try:
        logger.debug("Starting transaction...")
        async with transaction_context(session):
            user = (await session.execute(select (User).where(User.email==email))).scalar_one_or_none()
            
            if not user:
                logger.error(f"User {email} not found")
                raise HTTPException(status_code=404, detail="User not found")
            
            if not check_validation_code(validation_code, user.validation_code):
                raise HTTPException(status_code=422, detail="Validation code is not valid")
            
            user.active = 1
            user.validation_code = None
            # Transaction will be automatically committed here
        logger.debug("Transaction committed.")
        return True
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Failed to validate user email: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate email")


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
            
            user.validation_code = random.randint(100000, 999999) # Generate validation_code
            await send_email(user.email, "Magic Tales - Password recovery", f"The validation code is: {user.validation_code}")

        logger.debug("Transaction committed.")

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

@session_router.post("/recover-password-validate", status_code=status.HTTP_200_OK)
async def recover_password_validation(
    email: Annotated[str, Form()],
    new_password: Annotated[str, Form()],
    repeated_new_password: Annotated[str, Form()],
    validation_code: Annotated[int, Form()],
    session: AsyncSession = Depends(get_session),
):
    """
    Validate user's register code

    Args:
        email (Annotated[str, Form): The email of the user to validate.
        new_password (str): The new user password
        repeated_new_password (str): The repeated new user password for validation
        validation_code (Annotated[int, Form): The validation code of the user.
        session (AsyncSession): Injected database session for executing asynchronous database operations.

    Returns:
        bool: True if the email was validate successfully.
    """
    try:
        logger.debug("Starting transaction...")
        async with transaction_context(session):
            user = (await session.execute(select (User).where(User.email==email))).scalar_one_or_none()
            
            if not user:
                logger.error(f"User {email} not found")
                raise HTTPException(status_code=404, detail="User not found")
            
            if not check_validation_code(validation_code, user.validation_code):
                raise HTTPException(status_code=422, detail="Validation code is not valid")
            
            if new_password != repeated_new_password:
                logger.error(f"The new_password '{new_password}' and repeated_new_password '{repeated_new_password}' aren't the same")
                raise HTTPException(status_code=422, detail="The new password and repeated new password must be the same")
            
            user.password = await hash_password_async(new_password)
            user.validation_code = None
            # Transaction will be automatically committed here
        logger.debug("Transaction committed.")
        return True
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Failed to validate user email: {e}")
        raise HTTPException(status_code=500, detail="Failed to validate email")