import os
import json
import re
from typing import List, Dict, Optional
from dotenv import load_dotenv
from fastapi import HTTPException
from langchain_sambanova import ChatSambaNovaCloud
from pydantic import BaseModel

# Load environment variables
load_dotenv()
SAMBANOVA_API_KEY = os.getenv("SAMBANOVA_API_KEY")
MODEL = "Meta-Llama-3.3-70B-Instruct"
MAX_TOKENS = 2000
TEMPERATURE = 0.7
TOP_P = 0.01

if not MODEL:
    raise Exception("Missing required environment variable: MODEL")

# Initialize SambaNova client
llm = ChatSambaNovaCloud(
    model=MODEL,
    max_tokens=int(MAX_TOKENS),
    temperature=float(TEMPERATURE),
    top_p=float(TOP_P)
)

# Prompt template for competitor analysis
categorization_prompt_template = """
Analyze {competitor} based on these search results:
{searchResults}

Key Analysis Points:
- Core capabilities and technologies
- Unique technological approaches and innovations
- Unique selling points and target market segments
- Recent innovations, strengths, and weaknesses
- Company's capabilities and overall market positioning
- Key products/services offered
- Potential challenges and market hurdles
- Business strategies and future vision

Provide concise, actionable insights about the competitor.

Return JSON with:
{{
  "key_insights": ["Detailed insights for each competitor"],
  "unique_capabilities": ["Standout features and strengths"],
  "unique_selling_points": ["Unique selling points and target market segments"],
  "recent_innovations": ["Recent innovations, strengths, and weaknesses"],
  "market_positioning": ["Overall market positioning, capabilities and differentiators"],
  "challenges": ["Challenges faced in the market"],
  "future_vision": ["Business strategies and plans for growth"]
}}
"""

def categorize_findings(competitor: str, search_results: List[Dict]) -> Dict:
    if not search_results:
        print(f"⚠️ No research results available for {competitor}")
        return {
            "key_insights": [],
            "unique_capabilities": [],
            "unique_selling_points": [],
            "recent_innovations": [],
            "market_positioning": [],
            "challenges": [],
            "future_vision": []
        }
    
    search_results_text = "\n".join([f"{res['title']}: {res['summary']}" for res in search_results])
    prompt = categorization_prompt_template.format(competitor=competitor, searchResults=search_results_text)
    
    messages = [("system", "You are a competitive analysis assistant."), ("human", prompt)]
    response = llm.invoke(messages)
    response_text = response.content.strip()
    
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                raise HTTPException(status_code=500, detail=f"Error decoding JSON after extraction. Raw output: {response_text}")
        else:
            raise HTTPException(status_code=500, detail=f"Error decoding response from SambaNova LLM. Raw output: {response_text}")

# Pydantic models for requests and responses
class SearchResult(BaseModel):
    title: str
    summary: str

class CategorizationRequest(BaseModel):
    competitor: str
    search_results: List[SearchResult]

class CategorizationResponse(BaseModel):
    key_insights: List[str]
    unique_capabilities: List[str]
    unique_selling_points: List[str]
    recent_innovations: List[str]
    market_positioning: List[str]
    challenges: List[str]
    future_vision: List[str]
