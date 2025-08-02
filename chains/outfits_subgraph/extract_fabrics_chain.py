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

# Data model for extracted fabrics
class Fabrics(BaseModel):
    """Extracted fabrics from the outfit request."""
    fabrics: List[str] = Field(
        ..., 
        description="Fabrics mentioned directly or inferred from the outfit request, such as 'silk' for 'luxurious' or 'cotton' for 'casual'."
    )

# Define the structured output for the LLM
def get_extract_fabrics_chain(llm):
    """
    Create a chain to extract fabrics from an outfit request.

    Args:
        llm: The language model instance.

    Returns:
        A chain combining the prompt and structured output for this task.
    """
    structured_output = llm.with_structured_output(schema=Fabrics)

    # Prompt for the chain
    EXTRACT_FABRICS_PROMPT = f"""
    You are extracting fabrics from the outfit request, even if not explicitly mentioned. 
    Infer fabrics based on themes, descriptions, or contexts (e.g., 'luxurious' implies 'silk').
    
    ### Rules:
    1. Analyze the input outfit request to identify fabrics directly mentioned or inferred.
    2. Examples of inferred fabrics:
       - "luxurious" implies "silk."
       - "casual" implies "cotton."
       - "warm and cozy" implies "wool."
    3. Respond using the following JSON format:
    
        "fabrics": ["<fabric1>", "<fabric2>", ...]
    
    ### Valid Values: {VALID_FABRICS}

    ### Example Analysis:
    **Request**: "I want a luxurious outfit for a formal dinner."
    **Output**:
    
        "fabrics": ["silk"]
    
    **Request**: "I need a casual and breathable outfit for summer."
    **Output**:
    
        "fabrics": ["cotton", "linen"]

    Analyze the input and extract relevant fabrics.
    """

    # Combine the prompt with the structured output
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", EXTRACT_FABRICS_PROMPT),
            (
                "human",
                """Analyze the following outfit request and identify relevant fabrics. 
                Respond using this format: \"fabrics\": [\"fabric1\", \"fabric2\", ...].\n\nRequest: {question}"""
            ),
        ]
    )

    # Return the chain
    extract_fabrics_chain = prompt | structured_output
    return extract_fabrics_chain
