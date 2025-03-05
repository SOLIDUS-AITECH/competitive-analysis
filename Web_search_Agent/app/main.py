from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from app.utils import search_competitor

# Initialize FastAPI app
app = FastAPI(title="Competitor Search API", version="1.0")

# Request model
class CompetitorSearchRequest(BaseModel):
    competitors: List[str]
    max_results: int = 3


# API endpoint to search competitors
@app.post("/search")
def search_competitors(request: CompetitorSearchRequest):
    results = {}
    for competitor in request.competitors:
        results[competitor] = search_competitor(competitor, request.max_results)
    return {"competitor_results": results}

