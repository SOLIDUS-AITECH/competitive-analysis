import json
from dotenv import load_dotenv
from fastapi import HTTPException
import os
from tavily import TavilyClient

# Load environment variables
load_dotenv()
# Initialize Tavily API client
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")  # Ensure your API key is set in the environment
tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

# Search function
def search_competitor(competitor: str, max_results=3):
    print(f"🔍 Searching for {competitor} using Tavily API...")
    try:
        response = tavily_client.search(query=competitor, max_results=max_results)
        search_results = response.get("results", [])

        unique_sources = {}
        for result in search_results:
            url = result["url"]
            if url not in unique_sources:
                unique_sources[url] = {
                    "title": result["title"],
                    "content": result["content"],
                    "raw_content": result.get("raw_content", None)
                }

        formatted_results = []
        for url, details in unique_sources.items():
            formatted_results.append({
                "title": details["title"],
                "url": url,
                "summary": details["content"][:1500],
                "full_content": details["raw_content"][:3000] if details.get("raw_content") else "Content not available"
            })
        
        return formatted_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching search results: {str(e)}")
