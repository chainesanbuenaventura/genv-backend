from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Data model for regenerating follow-up questions
class RegenerateFollowupQuestions(BaseModel):
    """Generate follow-up questions to address missing information."""
    followup_questions: str = Field(
        description="The follow-up questions to ask the user, covering the missing details."
    )
    explanation: str = Field(
        description="An explanation of why these follow-up questions were generated based on the missing information and context."
    )

# Define the structured output for the LLM
def get_regenerate_followup_questions_chain(llm):
    """
    Create a chain to regenerate follow-up questions based on missing details and context.

    Args:
        llm: The language model instance.

    Returns:
        A chain combining the prompt and structured output for this task.
    """
    structured_output = llm.with_structured_output(schema=RegenerateFollowupQuestions)

    # Prompt for the chain
    REGENERATE_FOLLOWUP_PROMPT = """
    You are an assistant tasked with regenerating follow-up questions for an outfit recommendation. 
    Use the missing information and conversation context to generate clear and concise questions for the user.
    Only re-ask the information that were not yet provided by the user.

    ### Guidelines:
    1. Focus on addressing the missing details to make the outfit request actionable (e.g., budget, colors, style preferences, occasion, etc.).
    2. Use the conversation history and the user's latest input to ensure the questions are relevant and logical.
    3. Generate the questions in plain text as a single response.
    4. Provide a brief explanation of why these questions are necessary.

    ### Respond in the following JSON format:
    
        "followup_questions": "<list of follow-up questions>",
        "explanation": "<reason>"
    
    ### User Profile:
    - User Name: {name}
    - User Age: {age}
    - User Gender: {gender}

    **JSON Output**:
    
        "followup_questions": "",
        "explanation": ""
    

    Analyze and respond accordingly.
    """

    # Combine the prompt with the structured output
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", REGENERATE_FOLLOWUP_PROMPT),
            (
                "human",
                """Missing Information: {missing_information}\n\nConversation History: {messages}\n\nUser Last Message: {question}\n\nOutfit Context: {outfit_context}""",
            ),
        ]
    )

    # Return the chain
    regenerate_followup_questions_chain = prompt | structured_output
    return regenerate_followup_questions_chain
