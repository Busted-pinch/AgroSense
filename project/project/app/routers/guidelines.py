from fastapi import APIRouter
from models.schemas import GuidelineOutput
from app.services.guidelines_service import get_guidelines

router = APIRouter(prefix="/api/v1/guidelines", tags=["Guidelines"])

@router.get("/recommendations", response_model=GuidelineOutput)
def get_recs():
    recs = get_guidelines()
    return {"recommendations": recs}