from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from app.utils import default_metrics


app = FastAPI(
    title="Metrics Comparison Agent",
    version="1.0",
    description=(
        "Provides user-selected metrics for company comparison based on industry. "
        "If no metrics are provided, returns an empty list."
    )
)

class MetricsRequest(BaseModel):
    industry: str
    selected_metrics: Optional[List[str]] = []  # User may specify which metrics they want

@app.post("/compare-metrics")
async def compare_metrics(request: MetricsRequest):
    if not request.selected_metrics:
        # Return empty if nothing specified
        return {
            "industry": request.industry,
            "selected_metrics": []
        }
    
    # Otherwise, for each provided metric category, expand it using default_metrics.
    expanded_metrics = []
    for metric in request.selected_metrics:
        # If the provided metric is a recognized category, expand it.
        if metric in default_metrics:
            expanded_metrics.extend(default_metrics[metric])
        else:
            # If it's not recognized, add it as is (or you could choose to ignore or error).
            expanded_metrics.append(metric)
            
    return {
        "industry": request.industry,
        "selected_metrics": expanded_metrics
    }