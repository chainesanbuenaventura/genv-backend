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

# Data model for accessory requirement check
class AccessoriesRequirementCheck(BaseModel):
    """Check if accessories are needed for the outfit request."""
    needs_accessories: str = Field(
        description="Binary answer: 'yes' if accessories are needed for the outfit, 'no' otherwise."
    )
    explanation: str = Field(
        description="Explanation for why accessories are or aren't needed."
    )

# Define the structured output for the LLM
def get_accessories_requirement_chain(llm):
    """
    Create a chain to determine if accessories are needed for the outfit request.

    Args:
        llm: The language model instance.

    Returns:
        A chain combining the prompt and structured output.
    """
    structured_output = llm.with_structured_output(schema=AccessoriesRequirementCheck)

    # Prompt for the chain
    ACCESSORIES_REQUIREMENT_PROMPT = """
    You are a conversational assistant helping to determine if accessories are needed for a specific outfit request.

    ### Task:
    Analyze the outfit request and decide if accessories are required based on the context and details provided. If accessories are mentioned or implied (e.g., necklace, bracelet, earrings), consider them necessary. If no such mention is made, decide that accessories are not needed.

    ### Instructions:
    1. Review the user's request and decide whether accessories are required or not.
    2. Provide:
       - `"yes"` if accessories are needed.
       - `"no"` if accessories are not needed.
    3. Provide one phrase explanation for your decision:
       - If `"yes"`, explain why accessories are needed.
       - If `"no"`, explain why accessories are not necessary. 

    ### Output Format:
    Respond with a JSON object containing:
    - `"needs_accessory"`: `"yes"` or `"no"`.
    - `"explanation"`: One phrase concise explanation of your decision.

    ### Key Rules:
    - Ensure your decision is based solely on the details provided in the outfit request.
    - Avoid making assumptions that aren't explicitly mentioned in the request.
    """

    # Combine the prompt with the structured output
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", ACCESSORIES_REQUIREMENT_PROMPT),
            (
                "human",
                """User Request Context: {outfit_request_context_subgraph}\n\nSeed Item: {seed_item}"""
            ),
        ]
    )

    # Return the chain
    accessories_requirement_chain = prompt | structured_output
    return accessories_requirement_chain
