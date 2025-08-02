from pydantic import BaseModel, Field, ValidationError
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
  

# Data model for Stage Transition
class StageTransition(BaseModel):
    """Determine the next stage in the outfit generation workflow."""
    next_stage_number: int = Field(description="The stage number (1-5) of the next stage in the workflow.")
    explanation: str = Field(description="Reason for transitioning to or staying in the next stage.")


# LLM Structure for Stage Transition
def get_structured_stage_transition(llm):
    """
    Set up LLM with structured output for the Stage Transition task.
    """
    return llm.with_structured_output(schema=StageTransition)

# 4. **Allow Outfit Changes or Variations**: Respond to feedback and iterate on the outfit recommendations. If the user gives positive feedback or does not request modifications, proceed to Stage 5.
# 5. **Finish and Confirm**: Summarize the final recommendation and confirm the conversation is complete.

# Prompt Instructions for the Stage Transition
STAGE_TRANSITION_INSTRUCTIONS = """
You are a conversational assistant helping a fashion stylist determine the next stage in an outfit recommendation workflow.

### Stages:
1. **Introduction and Ask Outfit Context**: Start the conversation by introducing yourself as a fashion assistant specializing in outfit recommendations. Ask the user for the context of the outfit they need (e.g., occasion, season/weather, preferences, etc). If the user brings up a non-fashion topic, politely inform them you can only assist with outfit recommendations and re-direct them if they have any outfit needs.
2. **Collect Additional Information**: Once there is already an outfit request context (e.g., occasion, season/weather, preferences, etc), identify additional information that will help improve the context and collect them from the user until all the identified missing information are provided by the user.
3. **Generate Outfit Recommendations**: Generate outfit recommendations based on the collected details. 
4. **Handle User Feedback and further engagement*: Handle user feedback or further engagement.

### Rules:
- Always return a JSON object with:
  - `"next_stage_number"`: An integer (1-4) indicating the next stage.
  - `"explanation"`: A string explaining the reason for selecting this stage.
- If the last stage number is 3 or 4, always set the next stage to 4.
- If the last stage number is 4 and the user continues engaging, stay in stage 4.
- Never omit these fields, even if the input is ambiguous. Always output a "next_stage_number" and an "explanation".
  Sample JSON Output:
      "next_stage_number": 1,
      "explanation": "The outfit request conversation is just initiating and has been no outfit request yet. Starting with defining the outfit context."
"""

# Chain Implementation
def get_stage_transition_chain(llm):
    """
    Create a chain to determine the next stage in the outfit recommendation workflow.

    Args:
        llm: The language model instance.

    Returns:
        A chain combining the prompt and structured output.
    """
    # Define the structured LLM output
    structured_stage_transition = get_structured_stage_transition(llm)

    # Define the prompt template
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", STAGE_TRANSITION_INSTRUCTIONS),
            ("human", "Conversation History:\n\n {messages} \n\n Last User Message: {question}\n\n Last Conversation Stage Number: {stage}\n\n"),
        ]
    )

    print("get_stage_transition_chain")

    # Combine the prompt with structured output
    stage_transition_chain = prompt | structured_stage_transition

    return stage_transition_chain
