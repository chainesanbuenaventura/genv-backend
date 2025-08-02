# from pydantic import BaseModel, Field
# from typing import List
# from langchain_core.prompts import ChatPromptTemplate

# class StyleRulesResponse(BaseModel):
#     """Data model for style rules retrieval."""
#     style_rules: str = Field(description="The style rules for creating an outfit around the seed item.")
#     sources: List[str] = Field(description="Sources where the style rules were retrieved from.")

# # Define the structured output for the LLM
# def get_style_rules_for_seed_item_chain(llm):
#     """
#     Create a chain to retrieve and validate style rules for the seed item.

#     Args:
#         llm: The language model instance.

#     Returns:
#         A chain combining the prompt and structured output for this task.
#     """
#     # Structured output schema
#     structured_output = llm.with_structured_output(schema=StyleRulesResponse)

#     # Prompt template
#     STYLE_RULES_PROMPT = """
#     You are a fashion assistant tasked with retrieving style rules for a seed item in the context of an outfit request.
    
#     ### Rules:
#     1. Consider the seed item and outfit request context carefully.
#     2. Retrieve style rules from internal databases or fallback to external sources if necessary.
#     3. If the rules are hallucinated or unreliable, fallback to a web search and revalidate.

#     ### Respond in the following JSON format:
    
        
#             "style_rules": "<style_rules>",
#             "sources": ["<source_1>", "<source_2>", ...]
        

#     ### Example:
#     **Seed Item**: "Red blazer, cotton, slim fit"
#     **Outfit Request**: "Business casual outfit for a presentation"

#     **Output**:
    
        
#             "style_rules": "1. Avoid pairing red blazers with bright-colored pants. 2. Opt for neutral or muted tones for a cohesive look.",
#             "sources": ["Internal database: Style Guide, Page 34"]
        

#     Analyze and respond accordingly.
#     """

#     # Combine the prompt with the structured output
#     prompt = ChatPromptTemplate.from_messages(
#         [
#             ("system", STYLE_RULES_PROMPT),
#             (
#                 "human",
#                 """Seed Item: {seed_item}\n\nOutfit Request: {outfit_request}""",
#             ),
#         ]
#     )

#     # Return the chain
#     style_rules_chain = prompt | structured_output
#     return style_rules_chain
