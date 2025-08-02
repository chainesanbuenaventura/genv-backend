from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Data model for specific outfit request
class SpecificRequestCheck(BaseModel):
    """Check if there is a specific outfit request in the conversation."""
    is_specific_request: str = Field(description="Indicates whether the user provided a specific outfit request ('yes' or 'no').")
    reasoning: str = Field(description="Explanation of why the input was or was not considered a specific outfit request.")

# LLM Structure for Specific Request Check
def get_structured_request_check(llm):
    return llm.with_structured_output(schema=SpecificRequestCheck)

# Prompt Instructions
SPECIFIC_REQUEST_PROMPT = """
You are a conversational assistant specializing in fashion recommendations. Your task is to analyze the user's input and determine if they have provided a specific outfit request.

### Rules:
1. A specific outfit request contains detailed information, such as the occasion, preferences, or specific style elements.
2. If the input is vague or general, it is not a specific request.
3. Respond with 'yes' if the input contains a specific outfit request, and 'no' otherwise.
4. Include reasoning for the decision.

### Respond in the following JSON format:

    "is_specific_request": "<yes/no>",
    "reasoning": "<reason>"


### Example Analysis:
Input: "I need an outfit for a wedding."
Output: 
    "is_specific_request": "yes",
    "reasoning": "The user mentioned an occasion (wedding) which is sufficient to consider it a specific request."


Input: "I need something nice to wear."
Output: 
    "is_specific_request": "no",
    "reasoning": "The input is too vague and does not specify an occasion, preferences, or style elements."


---

Analyze the input and respond accordingly.
"""

# Create the Specific Request Check Chain
def get_is_specific_request_chain(llm):
    # LLM with structured output
    structured_request_check = get_structured_request_check(llm)

    # Define the prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system", 
                SPECIFIC_REQUEST_PROMPT
            ),
            (
                "human", 
                """Conversation History:\n\n{messages}\n\nUser Input: {question}"""
            ),
        ]
    )

    # Combine prompt with structured output
    specific_request_chain = prompt | structured_request_check

    return specific_request_chain
