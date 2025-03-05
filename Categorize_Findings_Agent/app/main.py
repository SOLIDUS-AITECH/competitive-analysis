from fastapi import FastAPI
from app.utils import (
    CategorizationRequest,
    CategorizationResponse,
    categorize_findings
)

app = FastAPI(
    title="Categorization API",
    version="1.0",
    description="API to categorize competitor findings based on search results using an LLM."
)

@app.post("/categorize", response_model=CategorizationResponse)
def categorize(request: CategorizationRequest):
    # Convert the search results (Pydantic models) to dictionaries
    search_results_dict = [result.model_dump() for result in request.search_results]
    results = categorize_findings(request.competitor, search_results_dict)
    return results
