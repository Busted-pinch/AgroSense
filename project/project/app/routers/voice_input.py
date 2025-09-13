from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.voice_service import process_voice_input

router = APIRouter()

@router.post("/voice-input")
async def voice_input(audio: UploadFile = File(...)):
    try:
        return await process_voice_input(audio)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
