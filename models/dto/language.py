from pydantic import BaseModel

class Language(BaseModel):
    id: int
    code: str
    name: str