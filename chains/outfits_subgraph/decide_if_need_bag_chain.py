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

# Data model for bag requirement check
class BagRequirementCheck(BaseModel):
    """Check if a bag is needed for the outfit request."""
    needs_bag: str = Field(
        description="Binary answer: 'yes' if a bag is needed for the outfit, 'no' otherwise."
    )
    explanation: str = Field(
        description="Explanation for why a bag is or isn't needed."
    )

# Define the structured output for the LLM
def get_bag_requirement_chain(llm):
    """
    Create a chain to determine if a bag is needed for the outfit request.

    Args:
        llm: The language model instance.

    Returns:
        A chain combining the prompt and structured output.
    """
    structured_output = llm.with_structured_output(schema=BagRequirementCheck)

    # Prompt for the chain
    BAG_REQUIREMENT_PROMPT = """
    You are a conversational assistant helping to determine if a bag is needed for a specific outfit request.

    ### Task:
    Analyze the outfit request and decide if a bag is required based on the context and details provided. If a bag is mentioned or implied (e.g., purse, handbag, clutch), consider it necessary. If no such mention is made, decide that a bag is not needed.

    ### Instructions:
    1. Review the user's request and decide whether a bag is required or not.
    2. Provide:
       - `"yes"` if a bag is needed.
       - `"no"` if a bag is not needed.
    3. Provide one phrase explanation for your decision:
       - If `"yes"`, explain why a bag is needed 
       - If `"no"`, explain why a bag is not necessary 

    ### Output Format:
    Respond with a JSON object containing:
    - `"needs_bag"`: `"yes"` or `"no"`.
    - `"explanation"`: One phrase concise explanation of your decision.

    ### Key Rules:
    - Ensure your decision is based solely on the details provided in the outfit request.
    - Avoid making assumptions that aren't explicitly mentioned in the request.
    """

    # Combine the prompt with the structured output
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", BAG_REQUIREMENT_PROMPT),
            (
                "human",
                """User Request Context: {outfit_request_context_subgraph}\n\nSeed Item: {seed_item}"""
            ),
        ]
    )

    # Return the chain
    bag_requirement_chain = prompt | structured_output
    return bag_requirement_chain