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

class ConversationState(TypedDict):
    """
    Graph state is a dictionary that contains information we want to propagate to, and modify in, each graph node.
    """
    user_profile: UserProfile
    
    model: str
    messages: Annotated[list, add_messages]
    question : str # User question
    generation : str # LLM generation
    stage: int # 1. Intro and outfit context

    missing_information: List[str]
    outfit_request_context: str
    still_missing: List[str]
    answered: List[str]
    answers: List[str]

    # outfits: List[Outfit]
    outfits: Annotated[List[Outfit], operator.add]
    # extracted_colors: List[str]
    # seed_items: SeedItems
    # valid_seed_items: SeedItems
    seed_item_start: int
    # past_seed_items: SeedItems
    # subset_items: SubsetItems

    # sequential generation
    # style_rules: str
    # style_rules_sources: List[List[str]]
    # selected_items: list
    # layers_done: list
    # seed_item: SeedItem

