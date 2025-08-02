from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Data model for the output
class MissingInformationCheck(BaseModel):
    """Check if all missing information and follow-up questions have been addressed."""
    still_missing: list = Field(
        description="List of missing details that remain unresolved based on user responses."
    )
    answered: list = Field(
        description="List of details from 'missing_information' that have been answered by the user."
    )

# Define the structured output for the LLM
def get_missing_information_check_chain(llm):
    """
    Create a chain to check which missing information has been answered.

    Args:
        llm: The language model instance.

    Returns:
        A chain combining the prompt and structured output for this task.
    """
    structured_output = llm.with_structured_output(schema=MissingInformationCheck)

    # Prompt for the chain
    MISSING_INFORMATION_CHECK_PROMPT = """
    You are a conversational assistant tasked with verifying which missing information has been addressed and which still needs to be clarified for an outfit recommendation.

    ### Instructions:
    1. Analyze the user's chat conversation history, their latest message, and the list of missing information.
    2. Identify which details in the `missing_information` list have been addressed based on the conversation.
       - A detail is considered "answered" if the user has provided a clear response or explicitly dismissed it (e.g., "no preference" or "not important").
    3. Identify which details are still unresolved (still missing) from the `missing_information` list.
       - A detail is "still missing" if the user has ignored the question or has not provided a sufficient answer.
    4. Ensure that the "still missing" list is a subset of the provided `missing_information`.

    ### Output Format:
    Respond with a JSON object containing:
    - `"still_missing"`: A list of unresolved details from the `missing_information`.
    - `"answered"`: A list of details from the `missing_information` that have been resolved.

    ### Key Rules:
    - Do not include new information in the "still missing" list.
    - Ensure all entries in "answered" and "still missing" correspond to the initial `missing_information`.

    ### Example Input:
    **Missing Information**:
    ["color preferences", "style preferences", "weather conditions"]

    **Conversation History**:
    Assistant: "What are your color preferences?"
    User: "No preference."
    Assistant: "What are your style preferences?"
    User: "I like bohemian styles."

    **Output**:
    
        "still_missing": ["weather conditions"],
        "answered": ["color preferences", "style preferences"]
    

    ### Analyze and respond accordingly.
    """

    # Combine the prompt with the structured output
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", MISSING_INFORMATION_CHECK_PROMPT),
            (
                "human",
                """Missing Information: {missing_information}\n\nConversation History: {messages}\n\nLast User Message: {question}"""
            ),
        ]
    )

    # Return the chain
    missing_information_check_chain = prompt | structured_output
    return missing_information_check_chain
