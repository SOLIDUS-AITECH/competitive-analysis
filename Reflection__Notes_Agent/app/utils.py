import os
import json
from typing import Dict, List
from dotenv import load_dotenv
from langchain_sambanova import ChatSambaNovaCloud

# Load environment variables
load_dotenv()
SAMBANOVA_API_KEY = os.getenv("SAMBANOVA_API_KEY")
MODEL = "Meta-Llama-3.3-70B-Instruct"
MAX_TOKENS = 2000
TEMPERATURE = 0.7
TOP_P = 0.01

# Initialize SambaNova Client
llm = ChatSambaNovaCloud(
    model=MODEL,
    max_tokens=int(MAX_TOKENS),
    temperature=float(TEMPERATURE),
    top_p=float(TOP_P)
)

# Reflection Prompt Template
reflection_prompt_template = """
Review the following competitive analysis:
{analysis}

Previous feedback:
{previous_feedback}

Consider:
- Depth of competitor analysis
- Missing key capabilities
- Clarity of market positioning
- Evidence and sources
- Actionable insights

Return JSON with:
{{
  "critique": ["List of critiques"],
  "suggestions": ["List of improvement suggestions"]
}}
"""

def reflect_and_improve(state: Dict) -> Dict:
    if not state.get("base_analysis"):
        return {"reflection_feedback": []}
    
    base_analysis = state["base_analysis"]
    previous_feedback = state.get("reflection_feedback", [])
    
    reflection_prompt = reflection_prompt_template.format(
        analysis=base_analysis,
        previous_feedback="\n".join(previous_feedback) if previous_feedback else "None"
    )
    
    messages = [("system", "You are a competitive analysis assistant."), ("human", reflection_prompt)]
    response = llm.invoke(messages)
    response_text = response.content.strip()
    
    try:
        feedback_json = json.loads(response_text)
    except json.JSONDecodeError:
        feedback_json = {"critique": [], "suggestions": []}
    
    feedback = feedback_json.get("critique", []) + feedback_json.get("suggestions", [])
    new_feedback = [fb for fb in feedback if fb not in previous_feedback]
    
    updated_feedback = previous_feedback + new_feedback
    
    # Return only the reflection feedback (notes)
    return {"reflection_feedback": updated_feedback}
