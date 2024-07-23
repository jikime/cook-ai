from pydantic import BaseModel

class AnalysisRequest(BaseModel):
    context: str
    question: str

class AnalysisResult(BaseModel):
    contents: str
