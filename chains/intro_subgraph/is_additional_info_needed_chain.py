from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Data model for Dynamic Additional Details Check
class DynamicAdditionalDetailsCheck(BaseModel):
    """Check if additional details are needed based on the dynamic nature of the outfit request."""
    additional_details_needed: str = Field(description="Indicates whether additional details are needed ('yes' or 'no').")
    explanation: str = Field(description="Explanation of why additional details are or are not needed.")

# LLM Structure for Dynamic Additional Details Check
def get_structured_dynamic_details_check(llm):
    return llm.with_structured_output(schema=DynamicAdditionalDetailsCheck)

# Prompt Instructions
DYNAMIC_DETAILS_PROMPT = """
You are a conversational assistant specializing in fashion recommendations. Your task is to evaluate whether additional details are needed to generate an outfit recommendation dynamically, based on the user's input and detected outfit context.

### Rules:
1. Consider whether the outfit context is specific enough to generate an outfit recommendation without further clarification.
   - If additional details would significantly improve the recommendation (e.g., weather, budget, preferences), respond with "yes."
   - If the input is already sufficient for generating an outfit (e.g., highly specific or self-explanatory like "look like a banana"), respond with "no."
2. Provide reasoning for your decision in plain language.

### Respond in the following JSON format:

    "additional_details_needed": "<yes/no>",
    "explanation": "<reason>"


### Example Analysis:
Input: "I need an outfit for a wedding."
Output: 

    "additional_details_needed": "yes",
    "explanation": "The input lacks details like style preferences or weather, which are important for creating a suitable recommendation."


Input: "I want to look like a banana."
Output: 

    "additional_details_needed": "no",
    "explanation": "The input is specific enough and does not require additional details to generate an outfit suggestion."


Input: "I need a formal outfit for a summer wedding."
Output: 

    "additional_details_needed": "no",
    "explanation": "The input provides all necessary details for generating a formal outfit for a summer wedding."


---

Analyze the input and respond accordingly.
"""

# Create the Chain
def get_check_additional_details_needed_chain(llm):
    # LLM with structured output
    structured_dynamic_details_check = get_structured_dynamic_details_check(llm)

    # Define the prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system", 
                DYNAMIC_DETAILS_PROMPT
            ),
            (
                "human", 
                """User Input: {question}\n\nOutfit Context Detected: {outfit_context}\n\nConversation History: {messages}"""
            ),
        ]
    )

    # Combine the prompt with structured output
    check_additional_details_needed_chain = prompt | structured_dynamic_details_check

    return check_additional_details_needed_chain
