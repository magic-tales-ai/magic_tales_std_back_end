from typing import List
from fastapi import APIRouter, status, Depends, HTTPException, Form
from models.dto.language import Language

system_router = APIRouter(prefix="/system", tags=["System"])

@system_router.get("/languages", status_code=status.HTTP_200_OK, response_model=List[Language])
async def languages():
    return [
        Language(code="CMN", name="Mandarin Chinese"),
        Language(code="SPA", name="Spanish"),
        Language(code="ENG", name="English"),
        Language(code="HIN", name="Hindi"),
        Language(code="BEN", name="Bengali"),
        Language(code="POR", name="Portuguese"),
        Language(code="RUS", name="Russian"),
        Language(code="JPN", name="Japanese"),
        Language(code="PNB", name="Western Punjabi"),
        Language(code="MAR", name="Marathi"),
        Language(code="TEL", name="Telugu"),
        Language(code="WUU", name="Wu Chinese"),
        Language(code="TUR", name="Turkish"),
        Language(code="KOR", name="Korean"),
        Language(code="FRA", name="French"),
        Language(code="DEU", name="German"),
        Language(code="VIE", name="Vietnamese"),
        Language(code="TAM", name="Tamil"),
        Language(code="YUE", name="Yue Chinese"),
        Language(code="URD", name="Urdu"),
        Language(code="ITA", name="Italian"),
        Language(code="ARA", name="Arabic"),
        Language(code="FIL", name="Filipino"),
        Language(code="POL", name="Polish"),
        Language(code="UKR", name="Ukrainian"),
        Language(code="THA", name="Thai"),
        Language(code="MAL", name="Malay"),
        Language(code="SWA", name="Swahili"),
        Language(code="NLD", name="Dutch"),
    ]