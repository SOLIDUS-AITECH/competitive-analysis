from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from app.utils import finalize_summary

app = FastAPI(
    title="Final Summary",
    version="1.0",
    description="API to summarize competitive analysis"
)

class SummaryRequest(BaseModel):
    industry: str
    overview: Optional[str] = None
    findings: Dict[str, dict]
    sources: List[str] = []

@app.post("/finalize_summary")
async def get_summary(request: SummaryRequest):
    try:
        summary = finalize_summary(
            industry=request.industry,
            overview=request.overview,
            findings=request.findings,
            sources=request.sources
        )
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
