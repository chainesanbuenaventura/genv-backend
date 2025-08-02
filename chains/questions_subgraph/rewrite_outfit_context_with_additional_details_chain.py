# from pydantic import BaseModel, Field
# from langchain_core.prompts import ChatPromptTemplate

# # Data model for rewriting outfit context with additional details
# class RewrittenOutfitContextWithDetails(BaseModel):
#     """Rewrites the user's outfit context with additional details and conversation context."""
#     rewritten_context: str = Field(
#         description="The updated outfit context, incorporating additional details, conversation history, and user input."
#     )

# # Define the structured output for the LLM
# def get_rewrite_outfit_context_with_additional_details_chain(llm):
#     """
#     Create a chain to rewrite the outfit context with additional details, conversation history, and user input.

#     Args:
#         llm: The language model instance.

#     Returns:
#         A chain combining the prompt and structured output for this task.
#     """
#     structured_output = llm.with_structured_output(schema=RewrittenOutfitContextWithDetails)

#     # Prompt for the chain
#     REWRITE_CONTEXT_PROMPT = """
#     You are an assistant specializing in fashion advice. Your task is to rewrite the user's outfit context,
#     incorporating additional details, missing information, and conversation context to create a clearer and more actionable request.

#     ### Guidelines:
#     1. Retain the original meaning and intent of the user's outfit request.
#     2. Incorporate the additional details provided (e.g., budget, colors, weather) and use the conversation history to ensure completeness.
#     3. Include any relevant missing information if explicitly mentioned by the user.
#     4. Ensure the rewritten context is concise, clear, and actionable.
#     5. Avoid adding new details or assumptions that are not present in the input.

#     ### Respond with the rewritten outfit context as plain text. Do not include additional commentary.

#     ### Example:
#     **Original Context**:
#     "I need an outfit for a wedding."
#     **Conversation History**:
#     Assistant: "What is your budget for the wedding outfit?"
#     User: "My budget is $200."
#     Assistant: "Do you have any color preferences?"
#     User: "Pastel shades."
#     **Missing Information**:
#     - "Season: Summer"

#     **Rewritten Context**:
#     "A $200 summer wedding outfit in pastel shades."

#     **Original Context**:
#     "I need a casual outfit."
#     **Conversation History**:
#     Assistant: "What is the occasion?"
#     User: "Beach outing."
#     Assistant: "What is your budget?"
#     User: "$100."
#     **Missing Information**:
#     - "Style: Trendy"

#     **Rewritten Context**:
#     "A $100 trendy casual outfit for a beach outing."

#     ### Respond with:
#     <rewritten_context>
#     """

#     # Combine the prompt with the structured output
#     prompt = ChatPromptTemplate.from_messages(
#         [
#             ("system", REWRITE_CONTEXT_PROMPT),
#             (
#                 "human",
#                 """Conversation History: {messages}\n\nUser Last Message: {question}""",
#             ),
#         ]
#     )

#     # Return the chain
#     rewrite_outfit_context_chain = prompt | structured_output
#     return rewrite_outfit_context_chain
