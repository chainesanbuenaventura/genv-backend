from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Data model for Follow-Up Questions
class FollowUpQuestions(BaseModel):
    """Generate follow-up questions for missing details."""
    followup_questions: str = Field(
        description="A general response based on the user's last message, including follow-up questions for unresolved details presented naturally."
    )
    still_missing: list[str] = Field(
        description="A subset of the original missing_information list containing details that are still unresolved based on user responses."
    )
    answered: list[str] = Field(
        description="List of details from the original missing_information that have been resolved based on user responses."
    )

# LLM Structure for Follow-Up Questions
def get_structured_followup_questions(llm):
    """
    Set up LLM with structured output for Follow-Up Questions.
    """
    return llm.with_structured_output(schema=FollowUpQuestions)

# Prompt Instructions for Follow-Up Questions
FOLLOWUP_QUESTIONS_INSTRUCTIONS = """
You are a conversational assistant tasked with generating a natural, conversational response to the user's latest message. 
If there are unresolved details in the outfit request, include them in the response seamlessly.

### Objective:
Generate a conversational response based on the user's last message and seamlessly integrate follow-up questions for unresolved details from the `missing_information` list.

### Instructions:
1. **Review Inputs:**
   - Analyze the user's chat conversation history, their latest message, and the `missing_information` list.
   - Based on these, segregate `missing_information` list into two sub list:
       - "answered": Details explicitly resolved or dismissed by the user (e.g., "no preference").
       - "still_missing": Details that remain unresolved or insufficiently addressed.

2. **Formulate a Response:**
   - Begin with a general response addressing the user's latest message.
   - If there are unresolved details in `still_missing`, include follow-up questions naturally within the flow of the response.
   - Acknowledge previous interactions when appropriate (e.g., "Thanks for sharing this! Could you also clarify...").

3. **Output Requirements:**
   Respond with a JSON object containing:
   - `"response"`: A natural, conversational response based on the user's last message and unresolved details.
   - `"answered"`: List of resolved details (subset of `missing_information`).
   - `"still_missing"`: List of unresolved details (subset of `missing_information`).

4. **Special Handling:**
   - If all details are resolved, provide a response that acknowledges completeness (e.g., "Thanks for sharing all the details! I can now proceed with your outfit suggestion.").
   - Avoid introducing unrelated topics or repeating resolved questions.
   - Ensure the follow-up questions flow naturally and do not confuse the user.

**JSON Output:**

    "response": "",
    "answered": [],
    "still_missing": []

"""

# Chain Implementation
def get_generate_followup_questions_chain(llm):
    """
    Create a chain to generate follow-up questions for missing details.

    Args:
        llm: The language model instance.

    Returns:
        A chain combining the prompt and structured output.
    """
    # Define the structured LLM output
    structured_followup_questions = get_structured_followup_questions(llm)

    # Define the prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", FOLLOWUP_QUESTIONS_INSTRUCTIONS),
            (
                "human",
                "Conversation History:\n\n{messages}\n\nLast User Message:\n\n{question}\n\nOutfit Request Context:\n\n{outfit_request_context}\n\nMissing Information:\n\n{missing_information}\n\n"
            )
        ]
    )

    # Combine the prompt with structured output
    followup_questions_chain = prompt | structured_followup_questions

    return followup_questions_chain
