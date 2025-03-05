from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
from app.utils import reflect_and_improve

app = FastAPI()

# Pydantic model for request validation
class StateRequest(BaseModel):
    industry: str
    specified_competitors: List[str]
    competitors: List[str]
    overview: str
    selected_competitors: List[str]
    research_results: Dict[str, List[Dict]]
    categorized_findings: Dict[str, Dict]
    base_analysis: str
    final_analysis: str
    reflection_feedback: List[str]
    reflection_iteration: int
    max_reflection_iterations: int
    next: str

@app.post("/reflect-and-improve/")
def reflect_and_improve_route(request: StateRequest):
    state = request.model_dump()
    result = reflect_and_improve(state)
    return result
