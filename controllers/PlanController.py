from fastapi import APIRouter, status, Depends
from db import get_session
from sqlalchemy.orm import Session
from sqlalchemy import select
from services.SessionService import check_token
from models.db.Plan import Plan

plan_router = APIRouter(prefix='/plan', tags=['Plan'])

@plan_router.get("/", status_code=status.HTTP_200_OK)
def get(session: Session = Depends(get_session)):
    plans = session.execute(select(Plan)).scalars().all()

    return plans