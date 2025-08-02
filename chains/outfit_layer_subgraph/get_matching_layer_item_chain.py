# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate, ChatPromptTemplate
# from langchain.tools import Tool
# from langchain_core.tools import tool
# from langchain.agents import create_react_agent, AgentExecutor
# from langchain.schema import HumanMessage
# from langchain.chains import RetrievalQAWithSourcesChain
# from langchain_community.vectorstores.neo4j_vector import Neo4jVector
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.tools.tavily_search import TavilySearchResults
# from pydantic import BaseModel, Field
# from typing import List, Dict, Union

# import os
# import sys

# from .article_categorizer_chain import *

# # Add the project root directory to sys.path
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
# if project_root not in sys.path:
#     sys.path.append(project_root)

# from utils import *

# LAYERS = {
#     "base_layers": BASE_LAYERS, 
#     "one_piece_items": ONE_PIECE_ITEMS, 
#     "bottoms": BOTTOMS, 
#     "shoes": SHOES,
# }

# # Data model for next item selection
# class NextItemResult(BaseModel):
#     """Result for selecting the next best matching item."""
#     selected_item: dict = Field(description="Details of the selected item from the provided subset.")
#     explanation: str = Field(description="Explanation for why the item was selected.")

# def generate_matching_layer_item(
#         selected_items_compact,
#         outfit_request,
#         style_rules,
#         subset_left_to_choose_from,
#     ) -> NextItemResult:
#     """
#     Build a complete, matching outfit using exact entries from the provided subset.
#     Handles both string and dictionary inputs for compatibility.
#     """
#     items_list = subset_left_to_choose_from

#     # Format items list
#     items_str = "\n".join([f"{i+1}. {item['title']} by {item['brand']}" for i, item in enumerate(items_list)])

#     prompt_template = PromptTemplate(
#         template=(
#             "You are an expert in fashion styling. Your task is to select the next best matching item for an outfit based on the provided input."
#             "Choose the next item from the available items to add to the current selected items based on the outfit request, and use the style rules to guide your decision."
#             "Ensure that the chosen item aligns with the overall outfit aesthetic and avoids duplications. Provide an explanation of why the chosen item was selected.\n\n"
#             "Outfit Request: {outfit_request}\n"
#             "Current Selected Items: {selected_items_compact}\n"
#             "Style Rules: {style_rules}\n"
#             "Available Items:\n{items_str}\n\n"
#             "Rules:\n"
#             "1. Select items that match the current selected items and that is relevant outfit request.\n"
#             "2. Let the style rules guide you in choosing the best match to the current selected items.\n"
#             "3. Prioritize fabric, color and style coordination.\n"
#             "4. Follow the provided style rules if applicable.\n\n"
#             "5. Select the next item that will make hthe whole look/outfit more complete or coherent\n\n"
#             "Provide a short explanation (not more than 2 sentences) of the item choice and why it will complement the existing selected items and the outftit request context."
#         ),
#         input_variables=["outfit_request", "selected_items_compact", "style_rules", "items_str"]
#     )

#     # Generate the prompt
#     formatted_prompt = prompt_template.format(
#         outfit_request=outfit_request,
#         selected_items_compact=selected_items_compact,
#         style_rules=style_rules,
#         items_str=items_str
#     )

#     # Call LLM
#     llm = ChatOpenAI(temperature=0)
#     response = llm.invoke([HumanMessage(content=formatted_prompt)])

#     # Parse response to identify selected items
#     selected_items = []
#     response_content = response.content.strip().lower()
#     for item in items_list:
#         if item['title'].lower() in response_content:
#             selected_items.append(item)

#     return NextItemResult(
#         explanation=response.content.strip(),
#         selected_item=selected_items[0] if selected_items != [] else {}
#     )