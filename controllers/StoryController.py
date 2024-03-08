from fastapi import APIRouter, status, Depends, HTTPException
from db import get_session
from sqlalchemy.orm import Session
from sqlalchemy import select
from services.SessionService import check_token
from models.db.Profile import Profile
from models.db.Story import Story
from models.api.StoryAPI import StoryAPI

story_router = APIRouter(prefix='/story', tags=['Story'])

@story_router.get("/", status_code=status.HTTP_200_OK)
def get(session: Session = Depends(get_session), token_data: dict = Depends(check_token)):
    profiles_ids = session.execute(select(Profile.id).where(Profile.user_id == token_data.get('user_id'))).scalars().all()
    return session.execute(select(Story).filter(Story.profile_id.in_(profiles_ids))).scalars().all()

@story_router.get("/{id}", status_code=status.HTTP_200_OK)
def get_by_id(id, session: Session = Depends(get_session), token_data: dict = Depends(check_token)):
    return session.get(Story, id)

@story_router.post("/", status_code=status.HTTP_200_OK)
def post(data: StoryAPI, session: Session = Depends(get_session), token_data: dict = Depends(check_token)):
    instance = Story(
        profile_id = data.profile_id,
        title = data.title,
        synopsis = data.synopsis,
        last_successful_step = data.last_successful_step
    )
    
    session.add(instance)
    session.commit()
    
    data.id = instance.id
    
    return data

@story_router.delete("/{id}", status_code=status.HTTP_200_OK)
async def delete(id: int, session: Session = Depends(get_session), token_data: dict = Depends(check_token)):
    story = session.query(Story).filter(Story.id == id).first()
    
    if not story:
        raise HTTPException(status_code=404, detail="Story not found")
    
    # TODO: check if the story belongs to the user
    
    session.delete(story)
    session.commit()
    
    return {"message": "Story deleted successfully"}