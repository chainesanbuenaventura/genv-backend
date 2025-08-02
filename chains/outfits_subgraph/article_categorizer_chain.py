from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field

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
    "Camisoles"
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
    "Robes, Robe Dresses, and Bathrobes"
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
    "Maxi Skirts"
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
    "Stockings"
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

# Data model
class CategorizationResult(BaseModel):
    """Categorization result for an input item."""
    category: str = Field(description="The category or layer the item belongs to, e.g., 'base_layers,' 'bottoms,' etc.")

def get_structured_categorizer(llm):
    """
    Configure an LLM for structured output.
    """
    return llm.with_structured_output(schema=CategorizationResult)

def get_categorization_chain(llm):
    """
    Create a chain for categorizing items into predefined layers.

    Args:
        llm: The language model instance.

    Returns:
        A categorization chain that outputs the category.
    """
    structured_categorizer = get_structured_categorizer(llm)
    
    base_layers = ", ".join(BASE_LAYERS)
    one_piece_items = ", ".join(ONE_PIECE_ITEMS),
    bottoms = ", ".join(BOTTOMS),
    jackets_and_other_outerwear = ", ".join(JACKETS_AND_OTHER_OUTERWEAR)
    coats = ", ".join(COATS),
    shoes = ", ".join(SHOES)
    additional_items = ", ".join(ADDITIONAL_ITEMS),
    accessories = ", ".join(ACCESSORIES),
    jewelry = ", ".join(JEWELRY),
    bags = ", ".join(BAGS)

    # Prompt
    system_message = f"""
    You are an expert in fashion categorization. Your task is to categorize the input item into one of the predefined fashion layers 
    based on its subsubcategory and title. The layers are:
    - base_layers (e.g. {base_layers})
    - one_piece_items (e.g. {one_piece_items})
    - bottoms (e.g. {bottoms})
    - coats (e.g. {coats})
    - shoes (e.g. {shoes})
    - jackets_and_other_outerwear (e.g. {jackets_and_other_outerwear})
    - additional_items (e.g. {additional_items})
    - accessories (e.g. {accessories})
    - jewelry (e.g. {jewelry})
    - bags (e.g. {bags})

    Provide only the category the item belongs to. If there is no exact match, provide the closes category it belongs to.
    """

    categorization_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_message),
            ("human", "Title: {title}\n\nSubsubcategory: {item_description}\n\nDetermine the most suitable layer for the item.\n\n")
        ]
    )

    # Combine prompt with structured output
    categorization_chain = categorization_prompt | structured_categorizer

    return categorization_chain