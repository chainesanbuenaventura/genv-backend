# Required Imports
from langchain.chat_models import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.tools import Tool
from langchain_core.tools import tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain.schema import HumanMessage
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel, Field
from typing import List, Dict, Union

import sys
import os

# Add the project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils import *

# ============================================
# 1. Input and Output Schemas
# ============================================

class GenerateOutfitInput(BaseModel):
    seed_item_str: str = Field(..., description="Description of the seed item.")
    subset: List[Dict] = Field(..., description="List of available items to build the outfit.")
    outfit_request: str = Field(..., description="User request describing the outfit theme or style.")
    style_rules: str = Field(..., description="Optional style rules to follow.")

class GenerateOutfitOutput(BaseModel):
    outfit_description: str = Field(..., description="Detailed description of the complete outfit.")
    selected_items: List[Dict] = Field(..., description="Exact entries from the subset used to complete the outfit.")

# ============================================
# 2. Tool 1: Generate Matching Outfit
# ============================================

def generate_complete_outfit(input_data: Union[str, Dict]) -> GenerateOutfitOutput:
    """
    Build a complete, matching outfit using exact entries from the provided subset.
    Handles both string and dictionary inputs for compatibility.
    """
    # Ensure input_data is a dictionary
    if isinstance(input_data, str):
        import json
        input_data = json.loads(input_data)

    # Extract inputs
    seed_item_str = input_data.get("seed_item_str", "")
    items_list = input_data.get("subset", [])
    outfit_request = input_data.get("outfit_request", "")
    style_rules = input_data.get("style_rules", "")
    model = input_data.get("model", "openai")

    # Format items list
    items_str = "\n".join([f"{i+1}. {item['title']} by {item['brand']}" for i, item in enumerate(items_list)])

    # Prompt Template
    prompt_template = PromptTemplate(
        template=(
            "You are a professional fashion stylist tasked with creating a complete outfit.\n\n"
            "Outfit Request: {outfit_request}\n"
            "Seed Item: {seed_item_str}\n"
            "Style Rules: {style_rules}\n"
            "Available Items:\n{subset}\n\n"
            "Rules:\n"
            "1. Select items that match the seed item and outfit request.\n"
            "2. Do not include duplicate categories (e.g., two pants or shoes).\n"
            "3. Prioritize fabric, color and style coordination.\n"
            "4. Follow the provided style rules if applicable.\n\n"
            "Provide a detailed outfit description and list the selected items."
        ),
        input_variables=["outfit_request", "seed_item_str", "style_rules", "subset"]
    )

    # Generate the prompt
    formatted_prompt = prompt_template.format(
        outfit_request=outfit_request,
        seed_item_str=seed_item_str,
        style_rules=style_rules,
        subset=items_str
    )

    # Call LLM
    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)
    response = llm.invoke([HumanMessage(content=formatted_prompt)])
    response = llm.invoke([HumanMessage(content=formatted_prompt)])

    # Parse response to identify selected items
    selected_items = []
    response_content = response.content.strip().lower()
    for item in items_list:
        if item['title'].lower() in response_content:
            selected_items.append(item)

    return GenerateOutfitOutput(
        outfit_description=response.content.strip(),
        selected_items=selected_items
    )

def generate_matching_outfit(input_data: Union[str, Dict]) -> GenerateOutfitOutput:
    """
    Build a complete, matching outfit using exact entries from the provided subset.
    Handles both string and dictionary inputs for compatibility.
    """
    # Ensure input_data is a dictionary
    if isinstance(input_data, str):
        import json
        input_data = json.loads(input_data)

    # Extract inputs
    seed_item_str = input_data.get("seed_item_str", "")
    items_list = input_data.get("subset", [])
    outfit_request = input_data.get("outfit_request", "")
    style_rules = input_data.get("style_rules", "")
    model = input_data.get("model", "openai")

    # Format items list
    items_str = "\n".join([f"{i+1}. {item['title']} by {item['brand']}" for i, item in enumerate(items_list)])

    # Prompt Template
    prompt_template = PromptTemplate(
        template=(
            "You are a professional fashion stylist tasked with creating a complete outfit.\n\n"
            "Outfit Request: {outfit_request}\n"
            "Seed Item: {seed_item_str}\n"
            "Style Rules: {style_rules}\n"
            "Available Items:\n{subset}\n\n"
            "Rules:\n"
            "1. Select items that match the seed item and outfit request.\n"
            "2. Do not include duplicate categories (e.g., two pants or shoes).\n"
            "3. Prioritize fabric, color and style coordination.\n"
            "4. Follow the provided style rules if applicable.\n\n"
            "Provide a detailed outfit description and list the selected items."
        ),
        input_variables=["outfit_request", "seed_item_str", "style_rules", "subset"]
    )

    # Generate the prompt
    formatted_prompt = prompt_template.format(
        outfit_request=outfit_request,
        seed_item_str=seed_item_str,
        style_rules=style_rules,
        subset=items_str
    )

    # Call LLM
    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)
    response = llm.invoke([HumanMessage(content=formatted_prompt)])

    # Parse response to identify selected items
    selected_items = []
    response_content = response.content.strip().lower()
    for item in items_list:
        if item['title'].lower() in response_content:
            selected_items.append(item)

    return GenerateOutfitOutput(
        outfit_description=response.content.strip(),
        selected_items=selected_items
    )

# ============================================
# 3. Tool 2: Style Rules Lookup
# ============================================

def style_rules_lookup(input_data: Union[str, Dict]) -> dict:
    """Retrieve fashion style rules from a Neo4j vector database or fallback to an internet search."""
    # Ensure input_data is a dictionary
    if isinstance(input_data, str):
        input_data = {"query": input_data}
    query = input_data.get("query", "")

    # Neo4j Vector Store
    neo4j_vector_store = get_neo4j_vector_store()

    retriever = neo4j_vector_store.as_retriever()
    chain = RetrievalQAWithSourcesChain.from_chain_type(
        ChatOpenAI(temperature=0),
        chain_type="stuff",
        retriever=retriever
    )

    response = chain.invoke({"question": query})
#     print("response: ", response)
    if response["sources"] == "":
        # Fallback to internet search if no answer found in the database
        tavily_tool = TavilySearchResults(max_results=3)
        search_response = tavily_tool.run(query)
        return {"answer": search_response, "sources": ["Internet search"]}

    return {
        "answer": response["answer"],
        "sources": response.get("sources", "").split("\n")
    }