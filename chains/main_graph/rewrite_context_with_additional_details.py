from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Data model for the rewritten outfit context
class RewrittenOutfitContext(BaseModel):
    """
    Model for the rewritten outfit context after gathering additional details.
    """
    rewritten_context: str = Field(
        description="The rewritten outfit context after incorporating additional details."
    )
    reasoning: str = Field(
        description="Reasoning for the updates made to the context."
    )

# Prompt for the chain
REWRITE_OUTFIT_CONTEXT_PROMPT = """
You are a fashion assistant. Your task is to rewrite the outfit context by incorporating additional details gathered from the user.

### Instructions:
1. Rewrite the original outfit context to include all relevant additional details provided by the user.
2. Ensure the rewritten context is coherent, concise, and complete.
3. If any required detail is missing, mention it in the reasoning.

### Example:

**Input:**
Original Outfit Context: "I need an outfit for a wedding."
Additional Details: "Weather": "Summer", "Style Preferences": "Formal and elegant", "Budget": "$200"

**Output:**
"rewritten_context": "I need a formal and elegant outfit for a summer wedding, with a budget of $200.",
"reasoning": "The original context mentioned a wedding. Added details about weather, style preferences, and budget to make the context complete."


"""

# Chain implementation
def get_rewrite_outfit_context_with_additional_details_chain(llm):
    """
    Create a chain to rewrite the outfit context based on additional details.

    Args:
        llm: The language model instance.

    Returns:
        A chain for rewriting the outfit context.
    """
    # Define the structured LLM output
    structured_output = llm.with_structured_output(schema=RewrittenOutfitContext)

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", REWRITE_OUTFIT_CONTEXT_PROMPT),
            ("human", "Conversation History:\n\n{messages}\n\nUser Message: {question}")
        ]
    )

    # Combine the prompt with the structured output
    return prompt | structured_output
