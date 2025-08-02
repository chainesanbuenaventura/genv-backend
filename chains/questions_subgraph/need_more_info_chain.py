from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Data model for binary check
class NeedMoreInfoCheck(BaseModel):
    """Check if more information needs to be asked."""
    need_more_info: str = Field(
        description="Binary answer: 'yes' if more information is needed to enrich the outfit request, 'no' otherwise."
    )
    explanation: str = Field(
        description="Explanation for why more information is or isn't needed."
    )

# Define the structured output for the LLM
def get_need_more_info_chain(llm):
    """
    Create a chain to determine if more information is needed in the first interaction.

    Args:
        llm: The language model instance.

    Returns:
        A chain combining the prompt and structured output.
    """
    structured_output = llm.with_structured_output(schema=NeedMoreInfoCheck)

    # Prompt for the chain
    NEED_MORE_INFO_PROMPT = """
    You are a conversational assistant helping a fashion stylist determine if more information is needed to enrich an outfit request during the first interaction with the user.

    ### Task:
    Analyze the user's initial message and the conversation context. Decide if the provided details are sufficient to generate an outfit recommendation or if additional questions should be asked to gather more information.

    ### Instructions:
    1. Review the conversation history and last user message and provide a one sentence summarizing the outfit request context.
    2. Decide whether the user provided enough information to proceed with generating an outfit or if further clarification or enrichment is required.
    3. Consider cases where some outfit requests (e.g., a casual outfit for a weekend) do not require extensive additional details, but others (e.g., a formal event in winter) might benefit from clarification.
    4. Provide:
       - `"yes"` if additional information is needed to enrich the request.
       - `"no"` if the request is complete and actionable.
    5. Provide a brief explanation for your decision:
       - If `"yes"`, explain what type of information could enrich the request.
       - If `"no"`, explain why the details are sufficient.
    6. The user profile is provided (e.g. name, age, gender), hence, consider them as non-missing information.

    ### User Profile:
    - User Name: {name}
    - User Age: {age}
    - User Gender: {gender}

    ### Output Format:
    Respond with a JSON object containing:
    - `"need_more_info"`: `"yes"` or `"no"`.
    - `"explanation"`: A concise explanation of your decision.

    ### Key Rules:
    - Ensure your decision is based solely on the initial user message and concersation histor.
    - Avoid asking unnecessary questions if the message already provides actionable details.
    """

    # Combine the prompt with the structured output
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", NEED_MORE_INFO_PROMPT),
            (
                "human",
                """User Message: {question}\n\nConversation History: {messages}"""
            ),
        ]
    )

    # Return the chain
    need_more_info_chain = prompt | structured_output
    return need_more_info_chain
