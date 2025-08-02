from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import SKLearnVectorStore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.schema import Document
from langgraph.graph import END
import asyncio

from fastapi import Request

from chains.outfits_subgraph import *
from tools import *
from graph.outfit_layer_subgraph import *
from graph.outfit_layer_subgraph.outfit_layer_state import *

from utils import *

from langchain_openai import ChatOpenAI 
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama

# Initialize the resources once
# llm = ChatOpenAI()
# local_llm = 'llama3.2'
# llm = ChatOllama(model=local_llm, temperature=0)

### Nodes

def hmf(state: OutfitLayerState):
    """
    Node to extract colors from the outfit request.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the extracted colors and updated state.
    """
    # Extract relevant state variables

    print("------")

    # Initialize before sequential generation

    # Log the output for debugging
    # print("Gotten Style Rules:", style_rules_output.style_rules)
    # print("Style Rules Sources:", style_rules_output.style_rules_sources)

    # Update the state and return
    return {
        "generation": "hmf",
    }

def get_style_rules_for_seed_item(state: OutfitLayerState):
    """
    Node to extract colors from the outfit request.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the extracted colors and updated state.
    """
    # Extract relevant state variables

    print("---GET STYLE RULES FOR SEED ITEM---")

    # Extract the value for products_href
    seed_item = state["seed_item"]
    # products_href_value = seed_item["products_href"]

    # subset_products_href_list = [subset_item['products_href'] for subset_item in state["subset_items"]]

    # Generate Outfit
    # print("rules")
    seed_item_str = format_seed_item_as_string(seed_item)
    style_rules_output = asyncio.run(
        agenerate_style_rules(
            seed_item_str = seed_item_str, 
            outfit_request=state["outfit_request_context_subgraph"],
        )
    )

    # Initialize before sequential generation

    # Log the output for debugging
    # print("Gotten Style Rules:", style_rules_output.style_rules)
    # print("Style Rules Sources:", style_rules_output.style_rules_sources)

    # Update the state and return
    return {
        "style_rules": style_rules_output.style_rules,
        "style_rules_sources": style_rules_output.style_rules_sources,
    }

def get_style_rules_for_seed_item_condensed(state: OutfitLayerState):
    """
    Node to extract colors from the outfit request.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the extracted colors and updated state.
    """
    # Extract relevant state variables

    print("---GET STYLE RULES FOR SEED ITEM---")

    # Extract the value for products_href
    seed_item = state["seed_item"]
    model = state.get("model", "openai")
    outfit_request = state["outfit_request_context_subgraph"]
    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)

    # Generate Outfit
    # print("rules")
    seed_item_str = format_seed_item_as_string(seed_item)
    
    # Example usage
    query = f"""What are the style/color/fabrics rules relevant to building an outfit around the seed item? Adjust the rules to remain consistent with the outfit request. 
    User Outfit Request: '{outfit_request}' 
    Seed Item:'{seed_item_str}'"""
    style_rules_response = style_rules_lookup(query)

    style_rules = style_rules_response.get("answer", "")

    style_rules_grader_chain = get_style_rules_grader_chain(llm)

    # print(style_rules)
    if style_rules == "": 
        return {
            "style_rules": get_style_rules_from_web_search(llm, query, outfit_request, seed_item_str),
            "style_rules_sources": ["internet"],
        }
    
    style_rules_grader_chain = get_style_rules_grader_chain(llm)
    
    hallucination_grade = style_rules_grader_chain.invoke({"style_query": query, "generation": style_rules})
    # print("hallucination: ", hallucination_grade)
    
    if hallucination_grade.binary_score.lower() == "no":
        return {
            "style_rules": get_style_rules_from_web_search(llm, query, outfit_request, seed_item_str),
            "style_rules_sources": ["internet"],
        }
    
    # Initialize before sequential generation

    # Log the output for debugging
    # print("Gotten Style Rules:", style_rules_response.get("style_rules", ""))
    # print("Style Rules Sources:", style_rules_response.get("sources", []))

    # Update the state and return
    return {
        "style_rules": style_rules_response.get("style_rules", ""),
        "style_rules_sources": style_rules_response.get("sources", []),
    }

def initialize_before_sequential_generation_of_layers(state: OutfitLayerState):
    """
    Node to extract colors from the outfit request.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the extracted colors and updated state.
    """
    # Extract relevant state variables

    print("---INITIALIZING BEFORE SEQUENTIAL GENERATION--")

    # Initialize before sequential generation

    seed_item = state["seed_item"]
    model = state.get("model", "openai")
    # if model == "llama3.2":
    #     llm = ChatOllama(model=model, temperature=0)
    # else:
    #     llm = ChatOpenAI(temperature=0)
    # llm = ChatOpenAI()

    # categorization_chain = get_categorization_chain(llm)

    selected_items = [seed_item]
    # seed_item_layer = categorization_chain.invoke({
    #     "item_description": seed_item["subsubcategory"],
    #     "title": seed_item["title"]
    # }).category
    seed_item_layer = categorize_layer(seed_item)
    # if seed_item_layer in ["base_layers_for_layering", "jackets_and_other_outerwear", "coats"]:
    #         seed_item_layer = "base_layers"

    # if seed_item_layer in ["base_layers_for_layering", "jackets_and_other_outerwear", "coats"]:
    #     seed_item_layer = "base_layers"

    layers_done = {seed_item_layer}
  
    # if "one_piece_items" in layers_done and "bottoms" not in layers_done:
    #     layers_done.add("bottoms")
    #     layers_done.add("base_layers")
    # if "base_layers" in layers_done and "one_piece_items" not in layers_done:
    #     layers_done.add("one_piece_items")
    # if "bottoms" in layers_done and "one_piece_items" not in layers_done:
    #     layers_done.add("one_piece_items")

    # Log the output for debugging
    # print("Gotten Style Rules:", style_rules_output.style_rules)
    # print("Style Rules Sources:", style_rules_output.style_rules_sources)

    # Update the state and return
    return {
        "selected_items": selected_items,
        "seed_item_layer": seed_item_layer,
        "layers_done": layers_done,
    }

def generate_next_layer_item(state: OutfitLayerState):
    """
    Node to extract colors from the outfit request.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the extracted colors and updated state.
    """
    # Extract relevant state variables
    layers_done = state["layers_done"]
    subset = state["subset_items_subgraph"]
    selected_items = state["selected_items"]
    seed_item = state["seed_item"]
    outfit_request = state["outfit_request_context_subgraph"]
    style_rules = state["style_rules"]
    model = state.get("model", "openai")
    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)

    print("---GENERATING NEXT LAYER ITEM--")

    # llm = ChatOpenAI(temperature=0)

    # Instantiate the categorization chain
    # categorization_chain = get_categorization_chain(llm)

    # print("one_piece_items in layers_done: ", "one_piece_items" in layers_done, layers_done)
    # print("base_layers in layers_done: ", "base_layers" in layers_done, layers_done)
    # print("bottoms in layers_done: ", "bottoms" in layers_done, layers_done)

    if "one_piece_items" in layers_done and "bottoms" not in layers_done:
        layers_done.add("bottoms")
        layers_done.add("base_layers")
    if "base_layers" in layers_done and "one_piece_items" not in layers_done:
        layers_done.add("one_piece_items")
    if "bottoms" in layers_done and "one_piece_items" not in layers_done:
        layers_done.add("one_piece_items")

    # print("Layers Done: ", ", ".join(layers_done))
    # Filter all layers that are left to be added
    possible_layers_left = [item for item in list(LAYERS.keys()) if item not in list(layers_done)]
    # print("\tPossible Layers to Choose From: ", possible_layers_left)

    # Current selected items
    selected_items_compact = simplify_dicts(selected_items)
    subsubcategories_left_to_choose_from = [item for sublist in [LAYERS[layer] for layer in possible_layers_left] for item in sublist]
    # print("\tSubsubcategories to choose from: ", ", ".join(subsubcategories_left_to_choose_from))

    subset_left_to_choose_from = list(filter(
        lambda item: item.get('subsubcategory') in subsubcategories_left_to_choose_from,
        subset,
    ))

    # Generate the next layer
    next_item_output = generate_matching_layer_item(
        selected_items_compact,
        outfit_request,
        style_rules,
        subset_left_to_choose_from,
    )

    next_item = next_item_output.selected_item

    if next_item != {}:
        # print("next_item: ", next_item)
        # print("subsubcategory: ", next_item["subsubcategory"])
        selected_items.append(next_item)
        # print(next_item["title"])
        # next_layer_added = categorization_chain.invoke(
        #     {
        #         "item_description": next_item["subsubcategory"],
        #         "title": next_item["title"],
        #     }
        # ).category
        next_layer_added = categorize_layer(next_item)
        # print("next_layer_added", next_layer_added)
        # print(f"\tAdded '{next_layer_added}' layer: ", simplify_dicts([next_item])[0]["subsubcategory"], " -- ", simplify_dicts([next_item])[0]["title"])
        # if next_layer_added in ["base_layers_for_layering", "jackets_and_other_outerwear", "coats"]:
        #     next_layer_added = "base_layers"
        layers_done.add(
            next_layer_added
        )
        # print("layer added: ", next_layer_added)
        # print("Seed: ", seed_item["subsubcategory"], " - ", seed_item["title"])
        # print("Selected Items: ", ", ".join([item["subsubcategory"] + " - " + item["title"] for item in selected_items]))
        # print( "Added: ", next_layer_added, " - ",  next_item["title"])
        # print("Current items: ", [item["subcategory"] for item in selected_items])
    else:
        return {
            "selected_items": selected_items,
            "layers_done": set(LAYERS.keys()),
        }


    # Log the output for debugging
    # print("Extracted Colors:", extracted_colors.colors)

    # Update the state and return
    return {
        "selected_items": selected_items,
        "layers_done": layers_done,
    }

def generate_bag(state: OutfitLayerState):
    """
    Node to extract colors from the outfit request.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the extracted colors and updated state.
    """
    # Extract relevant state variables
    layers_done = state["layers_done"]
    subset = state["subset_items_subgraph"]
    selected_items = state["selected_items"]
    # seed_item = state["seed_item"]
    outfit_request = state["outfit_request_context_subgraph"]
    style_rules = state["style_rules"]

    print("---GENERATING BAG--")

    # print("Layers Done: ", ", ".join(layers_done))
    # Filter all layers that are left to be added
    possible_layers_left = ['bags']
    # print("\tPossible Layers to Choose From: ", possible_layers_left)

    # Current selected items
    selected_items_compact = simplify_dicts(selected_items)
    subsubcategories_left_to_choose_from = [item for sublist in [ALL_ADDITIONAL_LAYERS[layer] for layer in possible_layers_left] for item in sublist]
    print("subsubcategories_left_to_choose_from: ", subsubcategories_left_to_choose_from)
    # print("\tSubsubcategories to choose from: ", ", ".join(subsubcategories_left_to_choose_from))

    subset_left_to_choose_from = list(filter(
        lambda item: item.get('subsubcategory') in subsubcategories_left_to_choose_from,
        subset,
    ))

    # Generate the next layer
    next_item_output = generate_matching_layer_item(
        selected_items_compact,
        outfit_request,
        style_rules,
        subset_left_to_choose_from,
    )

    bag = next_item_output.selected_item
    print("Selected bag: ", bag)
    # Update the state and return
    return {
        "bag": bag,
    }

def generate_jacket(state: OutfitLayerState):
    """
    Node to extract colors from the outfit request.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the extracted colors and updated state.
    """
    # Extract relevant state variables
    layers_done = state["layers_done"]
    subset = state["subset_items_subgraph"]
    selected_items = state["selected_items"]
    # seed_item = state["seed_item"]
    outfit_request = state["outfit_request_context_subgraph"]
    style_rules = state["style_rules"]

    print("---GENERATING JACKET--")

    # print("Layers Done: ", ", ".join(layers_done))
    # Filter all layers that are left to be added
    possible_layers_left = ['jackets_and_other_outerwear']
    # print("\tPossible Layers to Choose From: ", possible_layers_left)

    # Current selected items
    selected_items_compact = simplify_dicts(selected_items)
    subsubcategories_left_to_choose_from = [item for sublist in [ALL_ADDITIONAL_LAYERS[layer] for layer in possible_layers_left] for item in sublist]
    print("subsubcategories_left_to_choose_from: ", subsubcategories_left_to_choose_from)
    # print("\tSubsubcategories to choose from: ", ", ".join(subsubcategories_left_to_choose_from))

    subset_left_to_choose_from = list(filter(
        lambda item: item.get('subsubcategory') in subsubcategories_left_to_choose_from,
        subset,
    ))

    # Generate the next layer
    next_item_output = generate_matching_layer_item(
        selected_items_compact,
        outfit_request,
        style_rules,
        subset_left_to_choose_from,
    )

    jacket = next_item_output.selected_item
    print("Selected Jacket: ", jacket)
    # Update the state and return
    return {
        "jacket": jacket,
    }

def generate_coat(state: OutfitLayerState):
    """
    Node to extract colors from the outfit request.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the extracted colors and updated state.
    """
    # Extract relevant state variables
    layers_done = state["layers_done"]
    subset = state["subset_items_subgraph"]
    selected_items = state["selected_items"]
    # seed_item = state["seed_item"]
    outfit_request = state["outfit_request_context_subgraph"]
    style_rules = state["style_rules"]

    print("---GENERATING COAT--")

    # print("Layers Done: ", ", ".join(layers_done))
    # Filter all layers that are left to be added
    possible_layers_left = ['coats']
    # print("\tPossible Layers to Choose From: ", possible_layers_left)

    # Current selected items
    selected_items_compact = simplify_dicts(selected_items)
    subsubcategories_left_to_choose_from = [item for sublist in [ALL_ADDITIONAL_LAYERS[layer] for layer in possible_layers_left] for item in sublist]
    print("subsubcategories_left_to_choose_from: ", subsubcategories_left_to_choose_from)
    # print("\tSubsubcategories to choose from: ", ", ".join(subsubcategories_left_to_choose_from))

    subset_left_to_choose_from = list(filter(
        lambda item: item.get('subsubcategory') in subsubcategories_left_to_choose_from,
        subset,
    ))

    # Generate the next layer
    next_item_output = generate_matching_layer_item(
        selected_items_compact,
        outfit_request,
        style_rules,
        subset_left_to_choose_from,
    )

    coat = next_item_output.selected_item
    print("Selected Coat: ", coat)
    # Update the state and return
    return {
        "coat": coat,
    }

def generate_accessories(state: OutfitLayerState):
    """
    Node to extract colors from the outfit request.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the extracted colors and updated state.
    """
    # Extract relevant state variables
    layers_done = state["layers_done"]
    subset = state["subset_items_subgraph"]
    selected_items = state["selected_items"]
    # seed_item = state["seed_item"]
    outfit_request = state["outfit_request_context_subgraph"]
    style_rules = state["style_rules"]

    print("---GENERATING ACCESSORIES--")

    # print("Layers Done: ", ", ".join(layers_done))
    # Filter all layers that are left to be added
    possible_layers_left = ['accessories']
    # print("\tPossible Layers to Choose From: ", possible_layers_left)

    # Current selected items
    selected_items_compact = simplify_dicts(selected_items)
    subsubcategories_left_to_choose_from = [item for sublist in [ALL_ADDITIONAL_LAYERS[layer] for layer in possible_layers_left] for item in sublist]
    print("subsubcategories_left_to_choose_from: ", subsubcategories_left_to_choose_from)
    # print("\tSubsubcategories to choose from: ", ", ".join(subsubcategories_left_to_choose_from))

    subset_left_to_choose_from = list(filter(
        lambda item: item.get('subsubcategory') in subsubcategories_left_to_choose_from,
        subset,
    ))

    # Generate the next layer
    next_item_output = generate_matching_layer_item(
        selected_items_compact,
        outfit_request,
        style_rules,
        subset_left_to_choose_from,
    )

    accessories = next_item_output.selected_item
    print("Selected accessories: ", accessories)
    # Update the state and return
    return {
        "coat": accessories,
    }

def finalize_layer_set(state: OutfitLayerState):
    """
    Node to extract colors from the outfit request.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the extracted colors and updated state.
    """
    # Extract relevant state variables
    print("---FINALIZING LAYER SET--")
    # selected_items = state["selected_items"] 
    # # if state["bag"]:
    # #     print("Adding bag")
    # #     selected_items += state["bag"]

    # outfit = {
    #     "subsubcategory": [result["subsubcategory"] for result in selected_items if "subsubcategory" in result],
    #     "title": [result["title"] for result in selected_items if "title" in result],
    #     "image_sources": [result["product_image_src"][0] for result in selected_items if "product_image_src" in result],
    #     "articles": [result["products_href"] for result in selected_items if "products_href" in result],
    #     "generated_by": "ai",
    #     # "outfit_description": results["outfit_description"],
    #     "style_rules_used": state["style_rules"],
    #     "style_rules_sources": state["style_rules_sources"],
    # }

    # Update the state and return
    return {
        "outfit_complete": True,
    }

def output_complete_outfit(state: OutfitLayerState):
    """
    Node to extract colors from the outfit request.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the extracted colors and updated state.
    """
    # Extract relevant state variables
    print("---OUTFIT COMPLETE--")
    selected_items = state["selected_items"] 
    base_outfit = simplify_dicts(selected_items)
    outfit_request_context_subgraph = state.get("outfit_request_context_subgraph", "")
    subset_items_subgraph = state["subset_items_subgraph"]
    style_rules = state["style_rules"]

    outfit_extra_layer_set = OutfitExtraLayerSet(base_outfit, outfit_request_context_subgraph, subset_items_subgraph, style_rules)

    output = outfit_extra_layer_set.generate_all_extra_layer_items()
    # print("additional layers: ", output)

    selected_items.extend(
        filter_by_subset(
            subset_items_subgraph, 
            output.additional_items + output.accessories + output.jewelry + output.bags
        )
    )

    # try:
    #     print("Adding bag")
    #     selected_items += state["bag"]
    # except:
    #     pass

    outfit = {
        "subsubcategory": [result["subsubcategory"] for result in selected_items if "subsubcategory" in result],
        "title": [result["title"] for result in selected_items if "title" in result],
        "image_sources": [result["product_image_src"][0] for result in selected_items if "product_image_src" in result],
        "articles": [result["products_href"] for result in selected_items if "products_href" in result],
        "generated_by": "ai",
        # "outfit_description": results["outfit_description"],
        "style_rules_used": state["style_rules"],
        "style_rules_sources": state["style_rules_sources"],
    }

    # Update the state and return
    return {
        "outfits": [outfit]
    }
