# Required Imports
from langchain.chat_models import ChatOpenAI
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
import asyncio
import sys
import os

# Add the project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.append(project_root)
    
# Add the `chains` directory to sys.path
chains_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../chains'))
if chains_path not in sys.path:
    sys.path.append(chains_path)

from tools import *
from chains.outfits_subgraph import *
from chains.outfits_subgraph.style_rules_chain import arun_parallel_style_chains
from chains.outfits_subgraph.generate_layer_items_chain import *

# Wrap Tools
generate_outfit_tool = Tool(
    name="generate_matching_outfit",
    func=generate_matching_outfit,
    description="Generates a complete outfit based on a seed item, available items, and optional style rules."
)

style_rules_tool = Tool(
    name="style_rules_lookup",
    func=style_rules_lookup,
    description="Retrieves fashion style rules based on a query. If unavailable, it searches the internet for answers."
)

tools = [generate_outfit_tool, style_rules_tool]

# Adjust Agent Prompt
agent_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a professional AI fashion stylist assistant. Automatically retrieve style rules relevant to the user's outfit request and use them to generate an outfit.\n\n"
                "Your steps:\n"
                "1. Retrieve style rules internally using the outfit request and seed item.\n"
                "2. Use the retrieved style rules to generate an outfit.\n\n"
                "Your responses must follow this strict format:\n"
                "Action: <tool_name>\n"
                "Action Input: <input_dict>\n"
                "If unsure, clarify your intention instead of producing invalid output."),
    ("human", "{input}"),
    ("system", "Available tools: {tools}\nTool names: {tool_names}\nScratchpad: {agent_scratchpad}")
])

class GenerateOutfitOutput(BaseModel):
#     outfit_description: str = Field(..., description="Detailed description of the complete outfit.")
    selected_items: List[Dict] = Field(..., description="Exact entries from the subset used to complete the outfit.")

class StyleRules(BaseModel):
    """
    Represents a collection of style rules and their sources.
    """
    style_rules: str  # A list of style rules
    style_rules_sources: List[List[str]]  # A list of corresponding sources for the rules

def generate_complete_outfit(
        seed_item, 
        outfit_request, 
        subset, 
        style_rules
    ) -> GenerateOutfitOutput:
    """
    Build a complete, matching outfit using exact entries from the provided subset.
    Handles both string and dictionary inputs for compatibility.
    """
    outfit_layer_set = OutfitLayerSet(
        seed_item,
        outfit_request,
        subset,
        style_rules
    )
    selected_items = outfit_layer_set.generate_all_layer_items()
#     selected_items = outfit_layer_set.selected_items
    
    return GenerateOutfitOutput(
#         outfit_description=response.content.strip(),
        selected_items=selected_items
    )

async def agenerate_style_rules(
        seed_item_str: str, 
        outfit_request: str,
        model: str = "openai",
    ) -> StyleRules:
    """
    Combines style rules retrieval and outfit generation, with the style query being internally generated.
    Args:
        seed_item: Description of the seed item for the outfit.
        subset: List of available items for the outfit.
        outfit_request: User's request describing the outfit theme or style.
    Returns:
        A dictionary with the outfit description, selected items, and style rules used.
    """
    # Step 1: Internally Generate Style Query
    # Define the queries
    color_style_query = f"""What are the color rules relevant to building an outfit around the seed item? Adjust the rules to remain consistent with the outfit request. 
    User Outfit Request: '{outfit_request}' 
    Seed Item:'{seed_item_str}'"""

    fabric_style_query = f"""What are the fabric rules relevant to building an outfit around the seed item? Adjust the rules to remain consistent with the outfit request. 
    User Outfit Request: '{outfit_request}' 
    Seed Item:'{seed_item_str}'"""

    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)

    # Execute the async function in Jupyter with `await`
    style_rules = ""
    style_rules_response = await arun_parallel_style_chains(llm, [color_style_query, fabric_style_query], outfit_request, seed_item_str)
    style_rules_sources = []
    for i, style_rule_response in enumerate(style_rules_response):
        answer = style_rule_response["answer"]
        style_rules += f"Style Rule {i+1}: {answer}\n"
        style_rules_sources.append(style_rule_response["sources"])

    return StyleRules(
        style_rules=style_rules, 
        style_rules_sources=style_rules_sources,
    )

def generate_outfit_with_internal_style_rules_sequential(
        subset: List[Dict], 
        outfit_request: str,
        seed_item: dict,
        style_rules_output: StyleRules,
    ) -> dict:
    """
    Combines style rules retrieval and outfit generation, with the style query being internally generated.
    Args:
        seed_item: Description of the seed item for the outfit.
        subset: List of available items for the outfit.
        outfit_request: User's request describing the outfit theme or style.
    Returns:
        A dictionary with the outfit description, selected items, and style rules used.
    """
    # outfit_output = generate_matching_outfit(outfit_input)
    outfit_output = generate_complete_outfit(
        seed_item=seed_item, 
        outfit_request=outfit_request, 
        subset=subset, 
        style_rules=style_rules_output.style_rules,
    )

    # Combine Results
    return {
#         "outfit_description": outfit_output.outfit_description,
        "selected_items": outfit_output.selected_items,
        "style_rules_used": style_rules_output.style_rules,
        "style_rules_sources": style_rules_output.style_rules_sources,
    }

async def agenerate_outfit_with_internal_style_rules(
        seed_item_str: str, subset: List[Dict], outfit_request: str,
        model: str = "openai"
    ) -> dict:
    """
    Combines style rules retrieval and outfit generation, with the style query being internally generated.
    Args:
        seed_item: Description of the seed item for the outfit.
        subset: List of available items for the outfit.
        outfit_request: User's request describing the outfit theme or style.
    Returns:
        A dictionary with the outfit description, selected items, and style rules used.
    """
    # Step 1: Internally Generate Style Query
    # Define the queries
    color_style_query = f"""What are the color rules relevant to building an outfit around the seed item? Adjust the rules to remain consistent with the outfit request. 
    User Outfit Request: '{outfit_request}' 
    Seed Item:'{seed_item_str}'"""

    fabric_style_query = f"""What are the fabric rules relevant to building an outfit around the seed item? Adjust the rules to remain consistent with the outfit request. 
    User Outfit Request: '{outfit_request}' 
    Seed Item:'{seed_item_str}'"""

    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)

    # Execute the async function in Jupyter with `await`
    style_rules = ""
    style_rules_response = await arun_parallel_style_chains(llm, [color_style_query, fabric_style_query], outfit_request, seed_item_str)
    style_rules_sources = []
    for i, style_rule_response in enumerate(style_rules_response):
        answer = style_rule_response["answer"]
        style_rules += f"Style Rule {i+1}: {answer}\n"
        style_rules_sources.append(style_rule_response["sources"])
    
    # print("Style rules: ", style_rules)

    # Step 3: Generate Outfit Using Retrieved Style Rules
    outfit_input = {
        "seed_item_str": seed_item_str,
        "subset": subset,
        "outfit_request": outfit_request,
        "style_rules": style_rules,
    }

    outfit_output = generate_matching_outfit(outfit_input)

    # Combine Results
    return {
        # "outfit_description": outfit_output.outfit_description,
        "selected_items": outfit_output.selected_items,
        "style_rules_used": style_rules,
        "style_rules_sources": style_rules_sources,
    }

async def agenerate_outfit_with_internal_style_rules_extended(
        seed_item_str: str, subset: List[Dict], outfit_request: str, seed_item,
        model: str = "openai"
    ) -> dict:
    """
    Combines style rules retrieval and outfit generation, with the style query being internally generated.
    Args:
        seed_item: Description of the seed item for the outfit.
        subset: List of available items for the outfit.
        outfit_request: User's request describing the outfit theme or style.
    Returns:
        A dictionary with the outfit description, selected items, and style rules used.
    """
    # Step 1: Internally Generate Style Query
    # Step 1: Internally Generate Style Query
    # Define the queries
    color_style_query = f"""What are the color rules relevant to building an outfit around the seed item? Adjust the rules to remain consistent with the outfit request. 
    User Outfit Request: '{outfit_request}' 
    Seed Item:'{seed_item_str}'"""

    fabric_style_query = f"""What are the fabric rules relevant to building an outfit around the seed item? Adjust the rules to remain consistent with the outfit request. 
    User Outfit Request: '{outfit_request}' 
    Seed Item:'{seed_item_str}'"""

    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)

    # Execute the async function in Jupyter with `await`
    style_rules = ""
    style_rules_response = await arun_parallel_style_chains(llm, [color_style_query, fabric_style_query], outfit_request, seed_item_str)
    style_rules_sources = []
    for i, style_rule_response in enumerate(style_rules_response):
        answer = style_rule_response["answer"]
        style_rules += f"Style Rule {i+1}: {answer}\n"
        style_rules_sources.append(style_rule_response["sources"])
    
    # print("Style rules: ", style_rules)

    # Step 3: Generate Outfit Using Retrieved Style Rules
    outfit_output = generate_complete_outfit(seed_item, outfit_request, subset, style_rules)

    # Combine Results
    return {
#         "outfit_description": outfit_output.outfit_description,
        "selected_items": outfit_output.selected_items,
        "style_rules_used": style_rules,
        "style_rules_sources": style_rules_sources,
    }

def generate_outfit_with_internal_style_rules(seed_item: str, subset: List[Dict], outfit_request: str) -> dict:
    """
    Combines style rules retrieval and outfit generation, with the style query being internally generated.
    Args:
        seed_item: Description of the seed item for the outfit.
        subset: List of available items for the outfit.
        outfit_request: User's request describing the outfit theme or style.
    Returns:
        A dictionary with the outfit description, selected items, and style rules used.
    """
    # Step 1: Internally Generate Style Query
    style_query = f"""What are the style rules relevant to building an outfit around this seed item below but remaining relevant to the current outfit request? 
    User Outfit Request: '{outfit_request}' 
    Seed Item:'{seed_item}'
    """

    # Step 2: Retrieve Style Rules (Internally)
    style_rules_response = style_rules_lookup({"query": style_query})
    style_rules = style_rules_response.get("answer", "No specific style rules found.")
    
    # print("Style rules: ", style_rules)

    # Step 3: Generate Outfit Using Retrieved Style Rules
    outfit_input = {
        "seed_item_str": seed_item,
        "subset": subset,
        "outfit_request": outfit_request,
        "style_rules": style_rules,
    }

    outfit_output = generate_matching_outfit(outfit_input)

    # Combine Results
    return {
        "outfit_description": outfit_output.outfit_description,
        "selected_items": outfit_output.selected_items,
        "style_rules_used": style_rules,
        "style_rules_sources": style_rules_response.get("sources", []),
    }

# Create Agent
# llm = ChatOpenAI(model="gpt-4o", temperature=0)
# agent = create_react_agent(llm=llm, tools=tools, prompt=agent_prompt)

# agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True, max_iterations=5)