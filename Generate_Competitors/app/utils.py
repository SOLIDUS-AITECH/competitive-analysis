import os
import json
import re
from fastapi import HTTPException
from dotenv import load_dotenv
from langchain_sambanova import ChatSambaNovaCloud
from typing import List, Optional

# Load environment variables from the .env file
load_dotenv()


SAMBANOVA_API_KEY = os.getenv("SAMBANOVA_API_KEY")
MODEL = "Meta-Llama-3.3-70B-Instruct"
MAX_TOKENS = 2000
TEMPERATURE = 0.7
TOP_P = 0.01

if not MODEL:
    raise Exception("Missing required environment variable: MODEL")

def generate_competitors(
    industry: str,
    specified_competitors: Optional[List[str]] = None,
    api_key: Optional[str] = None
) -> dict:
    """
    Generate a list of key competitors and an industry overview using the ChatSambaNovaCloud LLM.
    
    If an API key is provided (via header), it will be used to instantiate the model.
    If specified_competitors is provided, the prompt instructs the model to use only those.
    """
    # Use provided API key or fall back to default from environment.
    if api_key is None:
        api_key = SAMBANOVA_API_KEY
    if not api_key:
        raise Exception("API key not provided either via header or environment variable.")

    # Set the API key in the environment for the ChatSambaNovaCloud integration.
    os.environ["SAMBANOVA_API_KEY"] = api_key

    # Instantiate the ChatSambaNovaCloud model
    llm = ChatSambaNovaCloud(
        model=MODEL,
        max_tokens=int(MAX_TOKENS),
        temperature=float(TEMPERATURE),
        top_p=float(TOP_P)
    )

    if specified_competitors:
        # Instruct the model to consider only the provided competitor names.
        prompt = f"""
        Identify key players in the {industry} domain.
        For the list of competitors, consider only these companies: {', '.join(specified_competitors)}.
        DO NOT generate any competitor names other than those provided.
        Provide a brief industry overview for the {industry} domain.
        Return ONLY valid JSON in the following format without any additional text:
        {{
          "competitors": {specified_competitors},
          "overview": "High-level industry description"
        }}
        """
    else:
        prompt = f"""
        Identify key players in the {industry} domain.
        Provide a list of top competitors and a brief industry overview.
        Return ONLY valid JSON in the following format without any additional text:
        {{
          "competitors": ["competitor1", "competitor2", ...],
          "overview": "High-level industry description"
        }}
        """

    # Build messages as expected by the SambaNova integration.
    messages = [
        ("system", "You are a competitive analysis assistant."),
        ("human", prompt)
    ]

    response = llm.invoke(messages)
    response_text = response.content.strip()

    # Attempt to parse the response as JSON.
    try:
        response_json = json.loads(response_text)
    except json.JSONDecodeError:
        # Try to extract a JSON substring from the response using regex.
        match = re.search(r"\{.*\}", response_text, re.DOTALL)
        if match:
            try:
                response_json = json.loads(match.group(0))
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error decoding JSON after extraction. Raw output: {response_text}"
                )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Error decoding response from SambaNova LLM. Ensure the format is valid JSON. Raw output: {response_text}"
            )

    competitors = response_json.get("competitors", [])
    overview = response_json.get("overview", "")
    return {"competitors": competitors, "overview": overview}
