from fastapi import FastAPI, Header, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Annotated
from app.utils import generate_competitors

app = FastAPI(title="Competitive Analysis API Agent")

# -----------------------------
# Pydantic Models for Requests/Responses
# -----------------------------
class GenerateCompetitorsRequest(BaseModel):
    industry: str
    specified_competitors: Optional[List[str]] = None

class GenerateCompetitorsResponse(BaseModel):
    competitors: List[str]
    overview: str

# Dependency to extract API key from header.
#def get_api_key(x_api_key: str = Header(..., alias="X-API-KEY")) -> str:
#    if not x_api_key:
#        raise HTTPException(status_code=400, detail="X-API-KEY header missing")
#    return x_api_key

# -----------------------------
# API Endpoint
# -----------------------------
@app.post("/analysis/generate", response_model=GenerateCompetitorsResponse)
def api_generate_competitors(
    request: GenerateCompetitorsRequest,
    #api_key: Annotated[str, Depends(get_api_key)]
):
    """
    Generate competitors and industry overview using the provided API key (from header)
    and request body data.
    """
    result = generate_competitors(
        industry=request.industry,
        specified_competitors=request.specified_competitors
        #api_key=api_key
    )
    return GenerateCompetitorsResponse(**result)
