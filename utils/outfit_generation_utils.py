from langchain_openai import ChatOpenAI
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

import os
import sys

# from .article_categorizer_chain import *

# Add the project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils import *
from dotenv import load_dotenv

load_dotenv()

# List of all base layer items
BASE_LAYERS = [
    "Short Sleeve T-Shirts",
    "Long-Sleeve T-Shirts",
    "Polo Shirts",
    "Sleeveless T-Shirts",
    "Casual Shirts and Button-Up Shirts",
    "Formal Shirts",
    "Blouses",
    "Long-Sleeved Tops",
    "Shirts",
    "Short-Sleeve Tops",
    "Sleeveless and Tank Tops",
    "Sweaters and Pullovers",
    "Crew Neck Sweaters",
    "V-Neck Sweaters",
    "Turtlenecks",
    "Bodysuits",
    "Camisoles",
    "Hoodies", 
    "Sweatshirts",
    "Corsets and Bustier Tops",
]

# List of items that don’t need bottoms (one-piece items)
ONE_PIECE_ITEMS = [
    "Casual and Day Dresses",
    "Cocktail and Party Dresses",
    "Formal Dresses and Evening Gowns",
    "Maxi Dresses",
    "Mini and Short Dresses",
    "Full-Length Jumpsuits and Rompers",
    "Playsuits",
    "Bikinis",
    "One-Piece Swimsuits and Bathing Suits",
    "Nightgowns and Sleepshirts",
    "Lingerie and Panty Sets",
    "Robes, Robe Dresses, and Bathrobes",
    "Tracksuits and Sweat Suits",
]

# List of all bottoms
BOTTOMS = [
    "Slim Jeans",
    "Skinny Jeans",
    "Straight-Leg Jeans",
    "Tapered Jeans",
    "Relaxed and Loose-Fit Jeans",
    "Bootcut Jeans",
    "Wide-Leg Jeans",
    "Capri and Cropped Jeans",
    "Flare and Bell Bottom Jeans",
    "Full-Length Pants",
    "Skinny Pants",
    "Wide-Leg and Palazzo Pants",
    "Straight-Leg Pants",
    "Harem Pants",
    "Casual Pants",
    "Cargo Pants",
    "Leggings",
    "Casual Shorts",
    "Bermuda Shorts",
    "Knee-Length Shorts",
    "Mini Shorts",
    "Cargo Shorts",
    "Jean and Denim Shorts",
    "Formal Shorts",
    "Mini Skirts",
    "Mid-Length Skirts",
    "Knee-Length Skirts",
    "Maxi Skirts", 
    "Track Pants and Sweatpants",
    "Sweatshorts",
    "Swim Trunks and Swim Shorts",
    "Sweatpants",
    "Boardshorts"
]

# List of base layers that are not one-piece (used for layering)
BASE_LAYERS_FOR_LAYERING = [
    "Short Sleeve T-Shirts",
    "Long-Sleeve T-Shirts",
    "Polo Shirts",
    "Sleeveless T-Shirts",
    "Casual Shirts and Button-Up Shirts",
    "Formal Shirts",
    "Blouses",
    "Long-Sleeved Tops",
    "Shirts",
    "Short-Sleeve Tops",
    "Sleeveless and Tank Tops",
    "Sweaters and Pullovers",
    "Crew Neck Sweaters",
    "V-Neck Sweaters",
    "Turtlenecks",
    "Cardigans",
    "Zipped Sweaters",
    "Ponchos and Poncho Dresses",
    "Sleeveless Sweaters"
]

# Coats
COATS = [
    "Trench Coats",
    "Long Coats and Winter Coats",
    "Short Coats",
    "Parka Coats",
    "Capes",
    "Fur Coats"
]

# Jackets & Other Outerwear
JACKETS_AND_OTHER_OUTERWEAR = [
    "Casual Jackets",
    "Leather Jackets",
    "Jean and Denim Jackets",
    "Fur Jackets",
    "Padded and Down Jackets",
    "Blazers, Sport Coats, and Suit Jackets",
    "Waistcoats and Gilets"
]

# List of additional items (e.g., socks, stockings)
ADDITIONAL_ITEMS = [
    "Socks",
    "Tights and Pantyhose",
    "Stockings",
    "Cover-Ups and Kaftans",
    "Sarongs and Sarong Wraps",
]

# Accessories, jewelry, and bags
ACCESSORIES = [
    "Belts",
    "Hats",
    "Scarves and Mufflers",
    "Gloves",
    "Face Masks",
    "Sunglasses",
    "Headbands and Hair Accessories",
    "Ties",
    "Umbrellas"
]

JEWELRY = [
    "Necklaces",
    "Bracelets",
    "Rings",
    "Earrings and Ear Cuffs",
    "Brooches"
]

BAGS = [
    "Tote Bags",
    "Shoulder Bags",
    "Crossbody Bags",
    "Clutches and Evening Bags",
    "Satchel Bags and Purses",
    "Top-Handle Bags",
    "Hobo Bags and Purses",
    "Duffel Bags and Weekend Bags",
    "Messenger Bags",
    "Backpacks",
    "Belt Bags",
    "Briefcases and Work Bags",
    "Bucket Bags and Bucket Purses",
    "Makeup Bags and Cosmetic Cases",
    "Luggage",
    "Pouches and Wristlets"
]

# List of all shoes
SHOES = [
    # Sneakers
    "High-Top Sneakers",
    "Low-Top Sneakers",
    
    # Heels
    "Stilettos and High Heels",
    "Pump Shoes",
    "Platform Heels",
    "Mule Shoes",
    "Sandal Heels",
    "Wedge Shoes and Pumps",
    
    # Boots
    "Ankle Boots",
    "Knee-High Boots",
    "Mid-Calf Boots",
    "Over-the-Knee Boots",
    "Casual Boots",
    "Wedge Boots",
    "Heel and High Heel Boots",
    "Wellington and Rain Boots",
    "Chukka Boots and Desert Boots",
    "Formal and Smart Boots",
    
    # Flats
    "Ballet Flats and Ballerina Shoes",
    "Espadrille Shoes and Sandals",
    "Loafers and Moccasins",
    "Flat Sandals",
    
    # Sandals & Slides
    "Leather Sandals",
    "Flip-Flops",
    
    # Slip-On Shoes
    "Loafers",
    "Monk Shoes",
    "Boat and Deck Shoes",
    "Espadrilles",
    "Slippers"
]

def categorize_layer(article):
    if not article["subsubcategory"]:
        if article["category"] == "Bags":
            return "bags"
        if article["category"] == "Accessories":
            return "accessories"
        if article["category"] in "Jewelry":
            return "jewelry"
    if article["subsubcategory"] in BASE_LAYERS or article["subcategory"] in ["T-Shirts", "Shirts", "Knitwear", "Tops"]:
        return "base_layers"
    if article["subsubcategory"] in ONE_PIECE_ITEMS or article["subcategory"] in ["Suits", "Dresses", "Jumpsuits & Rompers"]:
        return "one_piece_items"
    if article["subsubcategory"] in BOTTOMS or article["subcategory"] in ["Jeans", "Pants", "Shorts", "Skirts"]:
        return "bottoms"
    if article["subsubcategory"] in COATS or article["subcategory"] == "Coats":
        return "coats"
    if article["subsubcategory"] in JACKETS_AND_OTHER_OUTERWEAR or article["subcategory"] == "Jackets":
        return "jackets_and_other_outerwear"
    if article["subsubcategory"] in ADDITIONAL_ITEMS or article["subcategory"] in ["Hosiery"]:
        return "additional_items"
    if article["subsubcategory"] in SHOES or article["category"] == "Shoes":
        return "shoes"
    return "undefined"

# Data model for next item selection
class NextItemResult(BaseModel):
    """Result for selecting the next best matching item."""
    selected_item: dict = Field(description="Details of the selected item from the provided subset.")
    # explanation: str = Field(description="One phrase explanation for why the item was selected.")

def generate_matching_layer_item(
        selected_items_compact,
        outfit_request,
        style_rules,
        subset_left_to_choose_from,
        model="openai"
    ) -> NextItemResult:
    """
    Build a complete, matching outfit using exact entries from the provided subset.
    Handles both string and dictionary inputs for compatibility.
    """
    prompt_template = PromptTemplate(
        template=(
            "You are an expert in fashion styling. Your task is to select the next best matching item for an outfit based on the provided input."
            "Choose the next item from the available items to add to the current selected items based on the outfit request, and use the style rules to guide your decision."
            "Ensure that the chosen item aligns with the overall outfit aesthetic and avoids duplications. Provide an explanation of why the chosen item was selected.\n\n"
            "Outfit Request: {outfit_request}\n"
            "Current Selected Items: {selected_items_compact}\n"
            "Style Rules: {style_rules}\n"
            "Available Items:\n{items_str}\n\n"
            "Rules:\n"
            "1. Select items that match the current selected items and that is relevant outfit request.\n"
            "2. Let the style rules guide you in choosing the best match to the current selected items.\n"
            "3. Prioritize fabric, color and style coordination.\n"
            "4. Follow the provided style rules if applicable.\n\n"
            "5. Select the next item that will make hthe whole look/outfit more complete or coherent\n\n"
            "Provide a one sentence explanation of the item choice and why it will complement the existing selected items and the outftit request context."
        ),
        input_variables=["outfit_request", "selected_items_compact", "style_rules", "items_str"]
    ) 

    # Format items list
    # print("\t", [item["subsubcategory"] for item in items_list])
    items_str = "\n".join([f"{i+1}. {item['title']} by {item['brand']}" for i, item in enumerate(subset_left_to_choose_from)])

    # Generate the prompt
    formatted_prompt = prompt_template.format(
        outfit_request=outfit_request,
        selected_items_compact=selected_items_compact,
        style_rules=style_rules,
        items_str=items_str
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
    for item in subset_left_to_choose_from:
        if item['title'].lower() in response_content:
            selected_items.append(item)

    return NextItemResult(
        explanation=response.content.strip(),
        selected_item=selected_items[0] if selected_items != [] else {}
    )

def retrieve_category_subset(state, category, percentage, k=500):
    limit = int(percentage * k)

    kg = get_neo4j_graph()

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_ENDPOINT = os.getenv('OPENAI_ENDPOINT')

    print("question: ", state.get("outfit_request_context", ""))
    print(state["extracted_colors"])

    subset = kg.query(f"""
        WITH genai.vector.encode(
            $question, 
            "OpenAI", 
            {{ token: $openAiApiKey, endpoint: $openAiEndpoint }}
        ) AS question_embedding

        CALL db.index.vector.queryNodes(
            'captions', 
            3000,  // Retrieve a large number of nodes initially
            question_embedding
        ) YIELD node AS a, score

        WITH a, score / 1.0 AS normalized_similarity_score
                                
        // Convert colors_composition array to a single string for fuzzy matching
        WITH a, normalized_similarity_score, apoc.text.join(a.colors_composition, " ") AS colors_string

        // Perform fuzzy matching for colors
        WITH a, colors_string, normalized_similarity_score,
            size([color IN $colors WHERE apoc.text.fuzzyMatch(colors_string, color)]) AS fuzzy_color_match_count

        // Assign a binary score based on fuzzy matches
        WITH a, normalized_similarity_score,
            CASE WHEN fuzzy_color_match_count > 0 THEN 1 ELSE 0 END AS color_match_score
        
        WHERE a.gender_category = $gender_category
            AND a.category = $category  // Restrict to the current category
                                
        // Combine vector similarity and keyword relevance, normalized
        WITH a, 
            (normalized_similarity_score * 0.7) + 
            (color_match_score * 0.3) AS combined_score

        // WITH a, 
        //     (normalized_similarity_score * 0.5) AS combined_score

        // SET a:SubsetNode

        RETURN a.products_href AS products_href, 
            a.product_image_src AS product_image_src, 
            a.brand AS brand, 
            a.title AS title, 
            a.image_caption AS image_caption, 
            a.gender_category AS gender_category, 
            a.colors_composition AS colors_composition, 
            a.fabric_composition AS fabric_composition, 
            a.category AS category, 
            a.subcategory as subcategory, 
            a.subsubcategory AS subsubcategory, 
            combined_score
        ORDER BY combined_score DESC
        LIMIT $limit
    """, 
    params=
        {
            "openAiApiKey": OPENAI_API_KEY,
            "openAiEndpoint": OPENAI_ENDPOINT,
            "question": state.get("outfit_request_context", ""),
            "colors": state["extracted_colors"],
            "gender_category": 'Men' if state["user_profile"]["gender"].lower() == 'male' else 'Women',
            "category": category,
            "limit": limit
        }
    )

    print(f"Adding {limit} {category}")
    # print("subset_subsubcategories: ", set([item["category"] for item in category_subset]))
    print("Number of newly added: ", len(subset))

    # print("gender: ", 'Men' if state["user_profile"]["gender"].lower() == 'male' else 'Women')

    return subset

