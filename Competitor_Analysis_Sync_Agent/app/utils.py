import httpx
import json
from typing import Dict, List

# Agent Endpoints from the Solidus platform
GENERATE_COMPETITORS_URL = "https://serverless.on-demand.io/apps/generatecompetitorsapi/analysis/generate"
WEBSEARCH_URL = "https://serverless.on-demand.io/apps/websearchapi/search"
CATEGORIZE_FINDINGS_URL = "https://serverless.on-demand.io/apps/categorizefindingsapi/categorize"
FINAL_SUMMARY_URL = "https://serverless.on-demand.io/apps/finalizesummaryapi/finalize_summary"
REFLECTION_AGENT_URL = "https://serverless.on-demand.io/apps/reflectionagentapi/reflect-and-improve"


# Helper function to call an agent's endpoint
async def call_agent(url: str, payload: dict) -> dict:
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            print(f"Calling: {url} with payload: {json.dumps(payload, indent=2)}")  # Debugging
            response = await client.post(url, json=payload)
            print(f"Response [{response.status_code}]: {response.text}")  # Debugging
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            print(f"Error calling {url}: {e.response.status_code}")
            print("Response content:", e.response.text)
            raise


# Step 1: Generate Competitors (Only if not specified)
async def call_generate_competitors(input_data: dict) -> dict:
    return await call_agent(GENERATE_COMPETITORS_URL, input_data)

# Step 2: Websearch for a competitor
async def call_websearch_agent(competitor: str) -> List[dict]:
    payload = {"competitors": [competitor], "max_results": 3}
    result = await call_agent(WEBSEARCH_URL, payload)
    if "competitor_results" in result:
        return result["competitor_results"].get(competitor, [])
    return result.get("results", [])

# Step 3: Categorize Findings for a competitor
async def call_categorize_findings(competitor: str, search_results: List[dict]) -> dict:
    # Include "title", "summary", and "url" for each search result
    filtered_results = [
        {
            "title": res.get("title", ""),
            "summary": res.get("summary", ""),
            "url": res.get("url", "")
        }
        for res in search_results
    ]
    payload = {"competitor": competitor, "search_results": filtered_results}
    return await call_agent(CATEGORIZE_FINDINGS_URL, payload)

# Step 4: Finalize Summary
async def call_final_summary(industry: str, overview: str, findings: dict, sources: List[str]) -> dict:
    payload = {"industry": industry, "overview": overview, "findings": findings, "sources": sources}
    return await call_agent(FINAL_SUMMARY_URL, payload)

async def call_reflection_agent(state: dict) -> dict:
    return await call_agent(REFLECTION_AGENT_URL, state)


# Orchestrator: Executes each agent in sequence and stops at final summary
async def orchestrate_analysis(input_data: dict) -> dict:
    industry = input_data["industry"]
    specified_competitors = input_data.get("specified_competitors", [])

    if specified_competitors:
        competitors = specified_competitors
        overview = f"Analysis of specified competitors in {industry} industry."
    else:
        gen_payload = {"industry": industry}
        gen_result = await call_generate_competitors(gen_payload)
        competitors = gen_result.get("competitors", [])
        overview = gen_result.get("overview", "")

    research_results = {comp: await call_websearch_agent(comp) for comp in competitors}
    
    categorized_findings = {
        comp: await call_categorize_findings(comp, research_results.get(comp, []))
        for comp in competitors
    }

    sources = [
        res.get("url") for comp_results in research_results.values() for res in comp_results if res.get("url")
    ]
    
    final_summary_result = await call_final_summary(industry, overview, categorized_findings, sources)
    final_summary = final_summary_result.get("summary", "No analysis provided.")

    # Initial analysis state before reflection
    analysis_state = {
        "industry": industry,
        "specified_competitors": specified_competitors,
        "competitors": competitors,
        "overview": overview,
        "selected_competitors": competitors,  # Assuming all are selected
        "research_results": research_results,
        "categorized_findings": categorized_findings,
        "base_analysis": final_summary,
        "final_analysis": final_summary,
        "reflection_feedback": [],
        "reflection_iteration": 0,
        "max_reflection_iterations": 3,
        "next": "reflection"
    }

    # Reflection Iteration
    for i in range(analysis_state["max_reflection_iterations"]):
        reflection_result = await call_reflection_agent(analysis_state)
        feedback = reflection_result.get("reflection_feedback", [])
        
        if not feedback or feedback == analysis_state["reflection_feedback"]:
            break  # Stop iterating if no new feedback

        analysis_state["reflection_feedback"] = feedback
        analysis_state["reflection_iteration"] += 1

    return {
        "final_summary": analysis_state["final_analysis"],
        "sources": sources,
        "reflection_feedback": analysis_state["reflection_feedback"]
    }
