import operator
from typing_extensions import TypedDict
from typing import List, Annotated, Any, Dict
from langgraph.graph.message import add_messages

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

# Specific to one seed item 
class OutfitLayerState(TypedDict):
    """
    Graph state is a dictionary that contains information we want to propagate to, and modify in, each graph node.
    """

    # outfit_request_context: str

    # outfits: List[Outfit]
    # generation : str # LLM generation
    outfits: Annotated[List[Outfit], operator.add]
    bag: Outfit
    jacket: Outfit
    outfit_complete: str
    # extracted_colors: List[str]
    # seed_items: SeedItems
    # valid_seed_items: SeedItems
    # seed_item_start: int
    # past_seed_items: SeedItems
    # subset_items: SubsetItems

    # new and local to the subgraph
    # specific to one seed item
    style_rules: str
    style_rules_sources: List[List[str]]
    selected_items: list
    seed_item_layer: str
    layers_done: set
    seed_item: SeedItem
    # recopied
    outfit_request_context_subgraph: Annotated[str, "READ_ONLY"]
    subset_items_subgraph: Annotated[SubsetItems, "READ_ONLY"]


