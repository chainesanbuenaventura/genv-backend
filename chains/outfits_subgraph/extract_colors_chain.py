from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List

import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils import *

# Data model for extracted colors
class Colors(BaseModel):
    """Extracted colors from the outfit request."""
    colors: List[str] = Field(
        ..., 
        description="Colors mentioned directly or inferred from the outfit request, such as 'red' for 'devil-themed' or 'dark' for 'black'."
    )

# Define the structured output for the LLM
def get_extract_colors_chain(llm):
    """
    Create a chain to extract colors from an outfit request.

    Args:
        llm: The language model instance.

    Returns:
        A chain combining the prompt and structured output for this task.
    """
    structured_output = llm.with_structured_output(schema=Colors)

    # Prompt for the chain
    EXTRACT_COLORS_PROMPT = f"""
    You are extracting colors from the outfit request, even if not explicitly mentioned. 
    Infer colors based on themes, descriptions, or contexts (e.g., 'devil-themed' implies 'red').
    
    ### Rules:
    1. Analyze the input outfit request to identify colors directly mentioned or inferred.
    2. Examples of inferred colors:
       - "devil-themed" implies "red."
       - "dark" implies "black."
       - "spring vibe" implies "pastel colors."
    3. Respond using the following JSON format:
    
        "colors": ["<color1>", "<color2>", ...]
    
    ### Valid Values: {VALID_COLORS}

    ### Example Analysis:
    **Request**: "I want a devil-themed outfit with bold accents."
    **Output**:
    
        "colors": ["red"]
    
    **Request**: "I need a light and airy outfit for spring."
    **Output**:
    
        "colors": ["blue", "white", "pink"]

    Analyze the input and extract relevant colors.
    """

    # Combine the prompt with the structured output
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", EXTRACT_COLORS_PROMPT),
            (
                "human",
                """Analyze the following outfit request and identify relevant colors. 
                Respond using this format: "colors": ["color1", "color2", ...].\n\nRequest: {question}"""
            ),
        ]
    )

    # Return the chain
    extract_colors_chain = prompt | structured_output
    return extract_colors_chain