from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Data model for Collect All Missing Info
class CollectMissingInfo(BaseModel):
    """Collect missing outfit information and generate follow-up questions."""
    followup_questions: str = Field(
        description="A single formatted string of follow-up questions to collect missing information about the outfit context."
    )
    reasoning: str = Field(
        description="Explanation of why the follow-up questions are necessary."
    )

# Define the structured output for the LLM
def get_collect_all_missing_info_chain(llm):
    """
    Create a chain to collect all missing information dynamically and output follow-up questions as a string.

    Args:
        llm: The language model instance.

    Returns:
        A chain combining the prompt and structured output for this task.
    """
    structured_output = llm.with_structured_output(schema=CollectMissingInfo)

    # Prompt for the chain
    COLLECT_MISSING_INFO_PROMPT = """
    You are a conversational assistant specializing in fashion and outfit recommendations. Your task is to dynamically identify and collect missing details required to generate a complete outfit recommendation based on the conversation history.

    ### Rules:
    1. Analyze the conversation history and identify any gaps in the user's outfit request.
    2. Dynamically generate follow-up questions based on the missing details.
    3. If the user explicitly indicates "no preference" or states a detail is not important, do not ask about it again in subsequent questions.
    4. Stop asking about all details once it is clear that no additional input is required or if the user expresses that all necessary information is provided.
    5. Format the follow-up questions as a single string, with each question separated by a newline character.
    6. Ensure the questions are natural, concise, and contextually relevant.

    ### Input:
    - Conversation History: The previous interaction history with the user.
    - User's Last Message: The most recent response from the user.

    ### Output:
    Provide a JSON response containing:
    - "followup_questions": A single string with all relevant follow-up questions, or an empty string if no questions are necessary.
    - "reasoning": An explanation of why these questions are being asked or why no questions are necessary.
    """

    # Combine the prompt with the structured output
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", COLLECT_MISSING_INFO_PROMPT),
            (
                "human",
                """Conversation History: {messages}\n\n
                User Last Message: {question}
                """,
            ),
        ]
    )

    # Return the chain
    collect_all_missing_info_chain = prompt | structured_output
    return collect_all_missing_info_chain
