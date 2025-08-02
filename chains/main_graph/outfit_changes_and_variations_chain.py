from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Updated Data Model
class OutfitChange(BaseModel):
    """Handle user feedback and transitions to regenerate outfits."""
    feedback_summary: str = Field(
        description="Summary of the changes or variations requested by the user."
    )
    response_to_the_user: str = Field(
        description="A response to the user, including follow-up questions or confirmations."
    )

# Chain Implementation
def get_outfit_change_chain(llm):
    """
    Create a chain for handling outfit changes or variations dynamically.

    Args:
        llm: The language model instance.

    Returns:
        A chain that processes user feedback and transitions accordingly.
    """
    # Define the structured output format
    structured_output = llm.with_structured_output(schema=OutfitChange)

    # Define the prompt
    OUTFIT_CHANGE_PROMPT = """
    You are a fashion assistant specializing in outfit recommendations.

    Your task is to:
    1. Summarize the user’s requested changes or variations.
    2. If feedback is clear and sufficient details are provided, confirm the understanding of the user’s feedback.
    3. If feedback is unclear or additional details are required, ask follow-up questions to clarify the user’s preferences.

    ### Workflow:
    - If feedback is clear, generate a response like: "Got it! [feedback_summary]. Is this correct?"
    - If feedback is unclear or incomplete, generate follow-up questions to gather missing details.

    ### JSON Output Format:
    
        "feedback_summary": "<summary>",
        "response_to_the_user": "<response>"
    

    ### Example 1: Missing Details
    **User Feedback:** "Can you make it trendier?"
    **JSON Output:**
    
        "feedback_summary": "User requested a trendier outfit.",
        "response_to_the_user": "What trends do you have in mind? Do you have specific colors or patterns you prefer?"
    

    ### Example 2: Ready for Confirmation
    **User Feedback:** "Can you make it more formal with bold accessories?"
    **JSON Output:**
    
        "feedback_summary": "User requested a more formal outfit with bold accessories.",
        "response_to_the_user": "Got it! You want a more formal outfit with bold accessories. Is this correct?"
    
    """

    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", OUTFIT_CHANGE_PROMPT),
            ("human", "Conversation History:\n\n{messages}\n\nUser Message: {question}\n\nOutfit Context: {outfit_context}")
        ]
    )

    # Combine the prompt with structured output
    outfit_change_chain = prompt | structured_output

    return outfit_change_chain
