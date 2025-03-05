from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.utils import orchestrate_analysis

app = FastAPI(
    title="Competitor Analysis Orchestrator",
    version="1.1",
    description="Orchestrates agents to generate competitors, perform web search, categorize findings, and finalize the summary."
)

class OrchestrationRequest(BaseModel):
    industry: str
    specified_competitors: Optional[List[str]] = []  # Optional list to seed competitor generation

@app.post("/orchestrate")
async def orchestrate(request: OrchestrationRequest):
    try:
        result = await orchestrate_analysis(request.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
