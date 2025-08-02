from pydantic import BaseModel, Field

class FollowUpQuestionsResponse(BaseModel):
    """Generate a conversational response with follow-up questions for unresolved details."""
    response: str = Field(
        description="A conversational response based on the user's latest message, including follow-up questions for unresolved details."
    )

FOLLOWUP_QUESTIONS_RESPONSE_INSTRUCTIONS = """
You are a conversational assistant tasked with generating a natural, conversational response to the user's latest message.

### Objective:
Generate a conversational response based on the user's last message and seamlessly integrate follow-up questions for unresolved details from the `still_missing` list.

### Instructions:
1. **Review Inputs:**
   - Analyze the user's chat conversation history and their latest message.
   - Use the `still_missing` list to generate follow-up questions naturally within the response.

2. **Formulate a Response:**
   - Begin with a general acknowledgment or response addressing the user's latest message.
   - If there are unresolved details in `still_missing`, include follow-up questions naturally within the flow of the response.
   - Acknowledge previous interactions when appropriate (e.g., "Thanks for sharing this! Could you also clarify...").

3. **Output Requirements:**
   Provide the results as a JSON object containing:
   - `"response"`: A natural, conversational response based on the user's last message and unresolved details.

4. **Special Handling:**
   - If all details are resolved (`still_missing` is empty), provide a response acknowledging completeness (e.g., "Thanks for sharing all the details! I can now proceed with your outfit suggestion.").
   - Avoid introducing unrelated topics or repeating resolved questions.
   - Ensure the follow-up questions flow naturally and do not confuse the user.

**JSON Output:**

    "response": "",

"""

def get_generate_followup_response_chain(llm):
    """
    Create a chain to generate a response with follow-up questions based on unresolved details.

    Args:
        llm: The language model instance.

    Returns:
        A chain combining the prompt and structured output.
    """
    from langchain_core.prompts import ChatPromptTemplate

    # Define the structured output model
    structured_followup_response = llm.with_structured_output(schema=FollowUpQuestionsResponse)

    # Define the prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", FOLLOWUP_QUESTIONS_RESPONSE_INSTRUCTIONS),
            (
                "human",
                "Conversation History:\n\n{messages}\n\nLast User Message:\n\n{question}\n\nStill Missing Information:\n\n{still_missing}\n\n"
            ),
        ]
    )

    # Combine the prompt with structured output
    followup_response_chain = prompt | structured_followup_response

    return followup_response_chain
