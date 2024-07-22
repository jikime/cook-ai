from fastapi import APIRouter, HTTPException
from models import AnalysisRequest, AnalysisResult
from services import analyze_text

router = APIRouter()

@router.post("/analyze", response_model=AnalysisResult)
async def analyze(request: AnalysisRequest):
    try:
        result = await analyze_text(request.context, request.question)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))