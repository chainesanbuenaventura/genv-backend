from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Data model for rewriting outfit context
class OutfitContextRewriter(BaseModel):
    """Rewrites the user's outfit context to improve clarity and structure."""
    outfit_context: str = Field(description="The refined version of the outfit context, rewritten for clarity and completeness.")

# LLM Structure for Rewriting Outfit Context
def get_structured_outfit_context_rewriter(llm):
    return llm.with_structured_output(schema=OutfitContextRewriter)

# Prompt Instructions
REWRITE_CONTEXT_PROMPT = """
You are a conversational assistant specializing in fashion advice. Your task is to take the user's 
outfit request and rewrite it to make it more concise, clear, and actionable.

### Guidelines:
1. Retain the original meaning and intent of the outfit request.
2. Rewrite the context to improve structure and clarity.
3. Ensure the rewritten context focuses on actionable details (e.g., occasion, weather, style preferences).
4. Avoid introducing new details or assumptions not present in the original request.

### Respond with the rewritten outfit context as plain text. Do not include additional commentary.
"""

# Create the Outfit Context Rewriter Chain
def get_rewrite_outfit_context_chain(llm):
    # LLM with structured output
    structured_outfit_context_rewriter = get_structured_outfit_context_rewriter(llm)

    # Define the prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system", 
                REWRITE_CONTEXT_PROMPT
            ),
            (
                "human", 
                """User Input:\n\n{question}\n\nConversation History:\n\n{messages}"""
            ),
        ]
    )

    # Combine prompt with structured output
    outfit_context_rewriter_chain = prompt | structured_outfit_context_rewriter

    return outfit_context_rewriter_chain
