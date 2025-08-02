from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Data model for rewritten outfit request context
class OutfitRequestContext(BaseModel):
    """Rewritten outfit request context based on conversation history and previous context."""
    outfit_request_context: str = Field(
        description="A single concise sentence summarizing the user's outfit request based on the old context and answered questions."
    )

# Define the structured output for the LLM
def get_rewrite_outfit_request_context_chain(llm):
    """
    Create a chain to rewrite the outfit request context based on the previous context, conversation history, and latest message.

    Args:
        llm: The language model instance.

    Returns:
        A chain combining the prompt and structured output for rewriting the outfit request context.
    """
    structured_output = llm.with_structured_output(schema=OutfitRequestContext)

    # Prompt for the chain
    REWRITE_CONTEXT_PROMPT = """
    You are a conversational assistant tasked with updating the user's outfit request context.

    ### Task:
    Analyze the previous outfit request context, the conversation history, and the user's latest message to rewrite the outfit request context based on answered questions.

    ### Instructions:
    1. Start with the old outfit request context if it is provided.
    2. Update or refine the context using the conversation history and the latest user message, considering only the details explicitly answered by the user from the follow up questions asked to the user.
    3. Rewrite the outfit request context into a single, concise sentence that accurately reflects the provided and additional information, if there are.
    4. Avoid redundancy, vague terms, or speculative details. Ensure the context is clear and actionable.

    ### Output Format:
    Respond with a JSON object containing:
    - `"outfit_request_context"`: A single concise sentence summarizing the user's updated outfit request.

    ### Example Input:
    **Previous Context:**
    "An outfit for a wedding."
    
    **Conversation History:**
    Assistant: "What is the occasion for the outfit?"
    User: "A wedding."
    Assistant: "Do you have any color preferences?"
    User: "Pastel colors."
    Assistant: "What style do you prefer?"
    User: "Something elegant."

    **Latest Message:**
    "It will be an evening event."

    **JSON Output:**
    
        "outfit_request_context": "An elegant outfit in pastel colors for an evening wedding."
    

    ### Key Rules:
    - Include relevant updates from the conversation history and user message.
    - Ensure the summary is actionable and relevant to the user's input.
    - Keep it to one concise sentence.
    """

    # Combine the prompt with the structured output
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", REWRITE_CONTEXT_PROMPT),
            (
                "human",
                """Previous Outfit Request Context: {outfit_request_context}\n\nConversation History: {messages}\n\nLatest User Message: {question}"""
            ),
        ]
    )

    # Return the chain
    rewrite_outfit_request_context_chain = prompt | structured_output
    return rewrite_outfit_request_context_chain
