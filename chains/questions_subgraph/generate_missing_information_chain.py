from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

# Data model for Missing Information
class MissingInformation(BaseModel):
    """Identify additional missing information to enrich recommendations."""
    outfit_request_context: str = Field(
        description="A detailed description of the user's outfit request context, such as the occasion, purpose, or specific requirements for the outfit."
    )
    missing_information: list = Field(
        description="List of detailed descriptions of additional information needed to enrich and personalize the outfit recommendation. Each item must be a full sentence explaining what is needed."
    )
    explanation: str = Field(
        description="A comprehensive explanation of why the additional details are necessary to create a personalized and thoughtful outfit recommendation."
    )

# LLM Structure for Missing Information
def get_structured_missing_information(llm):
    """
    Set up LLM with structured output for Missing Information.
    """
    return llm.with_structured_output(schema=MissingInformation)

# Prompt Instructions for Missing Information
MISSING_INFORMATION_INSTRUCTIONS = """
You are a conversational assistant helping a fashion stylist identify missing information to improve outfit recommendations.

### Task:
Analyze the user's chat conversation history, their latest message, and any already-provided details. Identify key information still missing to make the recommendation more personalized and relevant.

### Guidelines:
1. **Summarize Context:**
   - Provide a clear one-sentence summary of the user's outfit request. Avoid redundancy and ensure the context aligns with the user's inputs.

2. **List Missing or Additional Information Needed:**
   - Use concise, specific phrases to describe additional details that can truly enrich the user's outfit request.
   - Only include information that is essential or genuinely missing. 
   - Avoid asking unnecessary questions (e.g., do not ask about color preferences if the outfit request explicitly or implicitly provides this information or it is obvious from the outfit request context, do not ask about the weather conditions if the user said it is for summer)
   - Limit the list to **1-2 actionable missing details.**
   - Ensure each entry is a single, descriptive phrase rather than full sentences or vague terms.
   - Do not provide examples or options of possible answers that the user can provide. Ensure the output is clean and avoids suggesting possible answers.

3. **Explain Importance:**
   - Provide a concise explanation of why these missing details are necessary to enhance the recommendations.

4. **Avoid Repetition:**
   - Exclude any details the user has already provided.
   - Do not list as missing information anything related to the user profile (e.g. name, age, gender), since they are already provided below.

### User Profile:
    - User Name: {name}
    - User Age: {age}
    - User Gender: {gender}

### Output Format:
Respond with a JSON object in the following format:
- `"outfit_request_context"`: A clear one-sentence summary of the user's outfit request.
- `"missing_information"`: A list of concise phrases describing the missing details.
- `"explanation"`: A short explanation of why the missing details are important.

### Key Rules:
- Avoid repetitive or irrelevant or obvious questions.
- Keep the output concise and focused on actionable details.
- Ensure the explanation directly relates to the missing information.
- Do not give users possible answers to choose from.
"""

# Chain Implementation
def get_missing_information_chain(llm):
    """
    Create a chain to identify missing information for an outfit request.

    Args:
        llm: The language model instance.

    Returns:
        A chain combining the prompt and structured output.
    """
    # Define the structured LLM output
    structured_missing_information = get_structured_missing_information(llm)

    # Define the prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", MISSING_INFORMATION_INSTRUCTIONS),
            ("human", "Conversation History:\n\n{messages}\n\nLast User Message:\n\n{question}\n\n")
        ]
    )

    # Combine the prompt with structured output
    missing_information_chain = prompt | structured_missing_information

    return missing_information_chain
