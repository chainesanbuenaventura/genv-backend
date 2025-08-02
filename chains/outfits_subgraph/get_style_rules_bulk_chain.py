import asyncio
# from langchain_openai import ChatOpenAI
import os

def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = os.getenv(var)
        
from tools import *
from chains.outfits_subgraph import *
from chains.outfits_subgraph.style_rules_grader_chain import *
from chains.outfits_subgraph.get_style_rules_from_websearch_chain import *

# llm = ChatOpenAI()

# Define the chain function
async def astyle_rules_chain(llm, query, outfit_request, seed_item_str):
    """
    Run the style rules lookup chain with a given query.
    """
    style_rules_response = await asyncio.to_thread(style_rules_lookup, {"query": query})
#     print(style_rules_response)
    style_rules = style_rules_response.get("answer", "")
    style_rules_grader_chain = get_style_rules_grader_chain(llm)
    # print(style_rules)
    if style_rules == "": 
        return {"answer": get_style_rules_from_web_search(llm, query, outfit_request, seed_item_str), "sources": ["internet"]}
    
    hallucination_grade = style_rules_grader_chain.invoke({"style_query": query, "generation": style_rules})
    # print("hallucination: ", hallucination_grade)
    
    if hallucination_grade.binary_score.lower() == "no":
        answer = get_style_rules_from_web_search(llm, query, outfit_request, seed_item_str)
        # print("answer: ", answer)
        return {"answer": answer, "sources": ["internet"]}
    
    return {"answer": style_rules, "sources": style_rules_response.get("sources", [])}


# Run the chains in parallel
async def arun_parallel_style_chains(llm, style_queries, outfit_request, seed_item_str):
    """
    Run both chains in parallel and return the results.
    """
    tasks = []
    for style_query in style_queries:
        tasks.append(astyle_rules_chain(llm, style_query, outfit_request, seed_item_str))
    results = await asyncio.gather(*tasks)
    return results

# def get_color_style_rules_bulk(llm, seed_items, outfit_request):
#     color_style_query = f"""What are the color rules relevant to building an outfit around the seed item? Adjust the rules to remain consistent with the outfit request. 
#     User Outfit Request: '{outfit_request}' 
#     Seed Item:'{seed_item_str}'"""

#     # fabric_style_query = f"""What are the fabric rules relevant to building an outfit around the seed item? Adjust the rules to remain consistent with the outfit request. 
#     # User Outfit Request: '{outfit_request}' 
#     # Seed Item:'{seed_item_str}'"""

#     # Execute the async function in Jupyter with `await`
#     style_rules = ""
#     style_rules_response = await arun_parallel_style_chains(llm, [color_style_query, fabric_style_query], outfit_request, seed_item_str)
#     style_rules_sources = []
#     for i, style_rule_response in enumerate(style_rules_response):
#         answer = style_rule_response["answer"]
#         style_rules += f"Style Rule {i+1}: {answer}\n"
#         style_rules_sources.append(style_rule_response["sources"])

#     # print("Style rules: ", style_rules)

#     # Combine Results
#     return {
#     #         "outfit_description": outfit_output.outfit_description,
#         "selected_items": outfit_output.selected_items,
#         "style_rules_used": style_rules,
#         "style_rules_sources": style_rules_sources,
#     }