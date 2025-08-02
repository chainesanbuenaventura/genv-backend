from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Data model for asking clarity about outfit context
class OutfitContextClarityCheck(BaseModel):
    """Guide the user toward providing specific outfit context."""
    has_outfit_context: str = Field(
        description="Indicates if the user has provided outfit context ('yes' or 'no')."
    )
    guidance: str = Field(
        description="Friendly guidance or follow-up questions to help the user clarify their outfit request."
    )

# LLM Structure for Asking Clarity
def get_structured_ask_for_clarity(llm):
    return llm.with_structured_output(schema=OutfitContextClarityCheck)

# Prompt Instructions for Clarity Chain
ASK_FOR_CLARITY_PROMPT = """
You are a conversational assistant specializing in fashion recommendations. Your goal is to guide the user to provide clear outfit context, even if they start with vague inputs or small talk.

### Rules:
1. Determine if the user has provided clear and actionable outfit context.
   - Outfit context includes:
     - Occasion (e.g., wedding, casual outing, birthday party)
     - Weather or season (e.g., summer, rainy, winter)
     - Style preferences (e.g., formal, trendy, casual)
2. If the context is unclear, provide friendly guidance or questions to help the user clarify their request.
3. If the context is clear, confirm with the user and prepare to suggest outfit ideas.
4. Always use friendly and conversational language.

### Respond in JSON format:

    
        "has_outfit_context": "<yes/no>",
        "guidance": "<friendly conversational response to guide the user>"
    

### Example Scenarios:
Input: "I need help with an outfit."
Output:
    
        "has_outfit_context": "no",
        "guidance": "Sure! Let’s get more specific so I can help you find the perfect outfit. What’s the occasion for this outfit? Is it for a party, a wedding, or something casual?"
    

Input: "I’m going to a summer wedding."
Output:
    
        "has_outfit_context": "yes",
        "guidance": "Great! It sounds like you have a clear idea of what you need. Let’s get started with some outfit suggestions!"
    

---

Analyze the input and respond accordingly.
"""

# Create the Ask for Clarity Chain
def get_ask_for_clarity_chain(llm):
    # LLM with structured output
    structured_clarity_check = get_structured_ask_for_clarity(llm)

    # Define the prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", ASK_FOR_CLARITY_PROMPT),
            ("human", """Conversation History:\n\n{conversation_history}\n\nUser Input: {user_message}"""),
        ]
    )

    # Combine prompt with structured output
    ask_for_clarity_chain = prompt | structured_clarity_check

    return ask_for_clarity_chain
