from pydantic import BaseModel, Field

# Pydantic Model for Segregation
class SegregatedInformationWithAnswers(BaseModel):
    """Segregate missing information into answered and still missing, including user-provided answers."""
    answers: list[str] = Field(
        description="A cumulative list of user-provided answers corresponding to the resolved details in the answered list."
    )
    answered: list[str] = Field(
        description="A cumulative list of details from the original missing_information that have been resolved based on user responses."
    )
    still_missing: list[str] = Field(
        description="A subset of the original missing_information list containing details that are still unresolved based on user responses."
    )

# Instructions for the Chain
SEGREGATE_INFORMATION_WITH_ANSWERS_INSTRUCTIONS = """
You are a conversational assistant tasked with maintaining and updating the segregation of a `missing_information` list based on the user's responses.

### Objective:
- Ensure `answered` and `answers` are cumulative across steps, retaining all previously resolved details while adding any newly resolved details.
- Ensure `still_missing` is the exact subset of `missing_information` that remains unresolved at this step.

### Instructions:
1. **Evaluate Previous Data:**
   - Retain the provided `answered` and `answers` from the previous step to preserve their cumulative state.
   - Use the user's latest responses to identify and add any newly resolved details to `answered` and `answers`.

2. **Segregation Process:**
   - Analyze the `missing_information` list.
   - Retain details in `answered` and `answers` that are exact subsets of `missing_information`.
   - Identify unresolved details in `missing_information` and add them to `still_missing`.

3. **Validation Rules:**
   - `answered` and `still_missing` must be non-overlapping subsets of `missing_information`.
   - `answers` must align one-to-one with `answered`.

4. **Output Requirements:**
   Provide a JSON object containing:
   - `"answers"`: A cumulative list of user-provided answers corresponding to all resolved details.
   - `"answered"`: A cumulative list of all resolved details from `missing_information`.
   - `"still_missing"`: The unresolved subset of `missing_information`.

**JSON Output:**

    "answers": [],
    "answered": [],
    "still_missing": []

"""

def get_segregate_information_with_answers_chain(llm):
    """
    Create a chain to segregate missing information into answered and still missing, including answers.

    Args:
        llm: The language model instance.

    Returns:
        A chain combining the prompt and structured output.
    """
    from langchain_core.prompts import ChatPromptTemplate

    # Define the structured output model
    structured_segregation = llm.with_structured_output(schema=SegregatedInformationWithAnswers)

    # Define the prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SEGREGATE_INFORMATION_WITH_ANSWERS_INSTRUCTIONS),
            (
                "human",
                "Conversation History:\n\n{messages}\n\nLast User Message:\n\n{question}\n\nMissing Information:\n\n{missing_information}\n\nAlready Answered from Missing Information:\n\n{answered}\n\nAnswers so far:\n\n{answers}\n\n"
            ),
        ]
    )

    # Combine the prompt with structured output
    segregation_chain = prompt | structured_segregation

    return segregation_chain
