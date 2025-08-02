from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Data model for nudging outfit context
class NudgeOutfitContextResponse(BaseModel):
    """Response for nudging the user to provide an outfit context."""
    nudge_message: str = Field(
        description="Message to nudge the user to provide an outfit context or clarify their request."
    )

# Define the structured output for the LLM
def get_ask_to_define_outfit_context_chain(llm):
    """
    Create a chain to nudge the user to define the outfit context.

    Args:
        llm: The language model instance.

    Returns:
        A chain combining the prompt and structured output for this task.
    """
    structured_output = llm.with_structured_output(schema=NudgeOutfitContextResponse)

    # Prompt for the chain
    NUDGE_OUTFIT_CONTEXT_PROMPT = """
    You are a conversational assistant helping users with fashion and outfit recommendations. 
    Assume that an introduction was already made. Do not make another greeting. Assume continuity of conversation.
    Your task is to politely and engagingly nudge the user toward providing an outfit context.
    Make sure to not greet them more than once if it has already been done in the conversation history. You can always address by their name or engage them given the information about their user profile.

    ### Rules:
    1. If the user has not provided an outfit context yet, ask them an engaging and conversational question to encourage them to share the context.
       Examples of context include:
       - Occasion (e.g., wedding, party, work, casual outing)
       - Season or weather (e.g., summer, rainy, winter)
       - Style preferences (e.g., casual, formal, trendy)
    2. If the user is vague or chit-chatting, guide them naturally toward making a specific outfit request.
       Examples:
       - "What’s the occasion for the outfit you’re looking for? A wedding, a casual day out, or something else?"
       - "Let’s start with something simple—are you shopping for something formal or casual?"
    3. Keep your response natural, friendly, and engaging. Avoid pressuring the user.
    4. Your output must be one single conversational response.
    5. Personalize your response using the user's name, age, and gender.

    ### User Profile:
    - User Name: {name}
    - User Age: {age}
    - User Gender: {gender}

    ### Respond in the following JSON format:
    
        "nudge_message": "<message>"
    

    ### Example Analysis:
    **Conversation History**:
    Assistant: "How can I help you with your outfit today?"
    User: "I don’t know, just looking for ideas."

    **Output**:
    
        "nudge_message": "Got it! Let’s narrow it down. Are you looking for an outfit for a specific occasion, like a party or a casual day out?"

    **Conversation History**:
    Assistant: "What can I help you with today?"
    User: "I hate suits."

    **Output**:
    
        "nudge_message": "Noted! How about we find something stylish and comfortable instead? What’s the occasion?"
    

    Analyze the input and respond with a friendly, helpful nudge.
    """

    # Combine the prompt with the structured output
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", NUDGE_OUTFIT_CONTEXT_PROMPT),
            (
                "human",
                """Conversation History: {conversation_history}\n\nUser Last Message: {user_message}"""
            ),
        ]
    )

    # Return the chain
    ask_to_define_outfit_context_chain = prompt | structured_output
    return ask_to_define_outfit_context_chain
