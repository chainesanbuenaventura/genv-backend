from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Data model for minimum necessary details
class MinimumDetailsCheck(BaseModel):
    """Check if the minimum necessary details are provided and generate follow-up questions if not."""
    missing_information: list = Field(description="A list of minimum necessary details missing to generate outfit recommendations.")
    followup_questions: str = Field(description="A single sentence with all follow-up questions for the missing details.")

# LLM Structure for Minimum Necessary Details Check
def get_minimum_details_chain(llm):
    """
    Creates a chain to check if the minimum necessary details are provided and generate follow-up questions.
    """
    structured_minimum_details_check = llm.with_structured_output(schema=MinimumDetailsCheck)

    # Define the prompt template
    MINIMUM_DETAILS_PROMPT = """
    You are a fashion recommendation assistant specializing in creating outfits using items from e-commerce websites.
    Your task is to check if the user has provided the **minimum necessary details** for generating personalized outfit recommendations and to request any essential missing information.

    ### Rules:
    1. The **minimum necessary details** can include but are not limited to:
       - **Occasion**: The event or purpose (e.g., casual, formal, party, gym).
       - **Style Preferences**: The user's aesthetic or style choices (e.g., trendy, minimalistic, vintage).
       - **Weather or Season**: Relevant climate information (e.g., summer, rainy, winter).
       - **Budget** (optional): If budget constraints are mentioned, consider them, but this is not always required.
       - **Other Context-Dependent Information**: Any other details necessary to ensure the outfit recommendation is appropriate and actionable.
    2. The minimum necessary details depend on the context of the request.
       - For instance, if the request is "How to dress like a banana?" budget or weather may not be relevant.
       - If the request is "Formal outfit for a summer wedding," you may still need details about style preferences or budget.
    3. Generate a list of missing information and a single follow-up question to ask the user.

    ### Respond in the following JSON format:
        "missing_information": ["<detail_1>", "<detail_2>", ...],
        "followup_questions": "<single sentence with all follow-up questions>"

    ### Example Input and Output:
    Input: "I need a formal outfit for a wedding."
    Output:
        "missing_information": ["weather/season", "style preferences"],
        "followup_questions": "Can you let me know the weather and your style preferences for this wedding outfit?"

    Input: "I need something casual for summer."
    Output:
        "missing_information": ["style preferences", "occasion"],
        "followup_questions": "Can you tell me your style preferences and the occasion for this casual summer outfit?"

    Input: "I want an outfit for the gym."
    Output:
        "missing_information": ["weather/season", "style preferences"],
        "followup_questions": "Can you let me know the weather conditions and your style preferences for this gym outfit?"

    ### Note:
    - Always tailor the missing details to the user's context.
    - Ensure the follow-up question is concise and conversational.

    Analyze the input and respond accordingly.
    """

    # Combine the prompt with structured output
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system", 
                MINIMUM_DETAILS_PROMPT
            ),
            (
                "human", 
                """Outfit Context: {outfit_context}"""
            ),
        ]
    )

    return prompt | structured_minimum_details_check
