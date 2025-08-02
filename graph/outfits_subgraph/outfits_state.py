import operator
from typing_extensions import TypedDict
from typing import List, Annotated, Any, Dict
from langgraph.graph.message import add_messages

class UserProfile(TypedDict):
    first_name: str
    last_name: str
    age: int
    gender: str

class SeedItem(TypedDict):
    products_href: str
    image_src: str 

class SeedItems(TypedDict):
    seed_items: List[SeedItem]

class SubsetItems(TypedDict):
    subset_items: List[SeedItem]

class Outfit(TypedDict):
    subsubcategory: str
    title: str
    articles: List[str]
    image_soources: List[str]
    generated_by: str
    style_rules_used: str
    style_rules_sources: List[List]

# This will be the state of the node that we will "map" all
# seed items to in order to generate an outfit
class OutfitState(TypedDict):
    outfit: Outfit
    # subset_items: SubsetItems

class GenerateOutfitsState(TypedDict):
    """
    Graph state is a dictionary that contains information we want to propagate to, and modify in, each graph node.
    """
    user_profile: UserProfile

    first_name: str
    last_name: str
    age: int
    gender: str

    model: str
    messages: Annotated[list, add_messages]
    question : str # User question
    generation : str # LLM generation
    stage: int # 1. Intro and outfit context

    outfit_request_context: str

    # outfits: List[Outfit]
    # gotten from outfit layer subgraph
    outfits: Annotated[List[Outfit], operator.add]

    # newly added 
    # depends on outfit request
    extracted_colors: List[str] 
    extracted_fabrics: List[str] 
    valid_seed_items: SeedItems
    subset_items: SubsetItems
    clothing_subset_items: SubsetItems
    shoes_subset_items: SubsetItems
    accessories_subset_items: SubsetItems
    bags_subset_items: SubsetItems
    jewelry_subset_items: SubsetItems
    seed_items: SeedItems
    seed_item_start: int
    past_seed_items: SeedItems
    
