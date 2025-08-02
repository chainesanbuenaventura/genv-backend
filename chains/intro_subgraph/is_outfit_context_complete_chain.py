from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Data model for completeness check
class OutfitRequestCompletenessCheck(BaseModel):
    """Check if the specific outfit request idea is complete."""
    is_complete: str = Field(description="Indicates whether the specific outfit request is complete ('yes' or 'no').")
    missing_details: list = Field(description="List of any missing details required to complete the outfit request.")

# LLM Structure for Completeness Check
def get_structured_completeness_check(llm):
    return llm.with_structured_output(schema=OutfitRequestCompletenessCheck)

# Prompt Instructions
COMPLETENESS_PROMPT = """
You are a conversational assistant specializing in fashion recommendations. Your task is to analyze the user's input and determine if the specific outfit request idea is complete.

### Rules:
1. An outfit request is considered complete if it provides all the necessary details for generating an outfit, such as:
   - Occasion (e.g., wedding, casual day)
   - Weather or season (e.g., summer, rainy)
   - Style preferences (e.g., formal, trendy)
   - Budget (optional but helpful)
2. If any details are missing, identify and list them.
3. Respond with 'yes' if all necessary details are provided, and 'no' otherwise.
4. Include a list of missing details if the request is incomplete.

### Respond in the following JSON format:

    "is_complete": "<yes/no>",
    "missing_details": ["<detail_1>", "<detail_2>", ...]


### Example Analysis:
Input: "I need an outfit for a wedding."
Output: 
    "is_complete": "no",
    "missing_details": ["weather/season", "style preferences"]


Input: "I need a formal outfit for a summer wedding."
Output: 
    "is_complete": "yes",
    "missing_details": []


---

Analyze the input and respond accordingly.
"""

# Create the Completeness Check Chain
def get_is_outfit_context_complete_chain(llm):
    # LLM with structured output
    structured_completeness_check = get_structured_completeness_check(llm)

    # Define the prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system", 
                COMPLETENESS_PROMPT
            ),
            (
                "human", 
                """Conversation History:\n\n{messages}\n\nUser Input: {question}"""
            ),
        ]
    )

    # Combine prompt with structured output
    is_outfit_context_complete_chain = prompt | structured_completeness_check

    return is_outfit_context_complete_chain
