from langgraph.graph import StateGraph
from IPython.display import Image, display
from langchain.schema import Document
from langgraph.graph import END
from langgraph.checkpoint.memory import MemorySaver
from .state import ConversationState
from .nodes import *
from .edges import *

from .intro_subgraph.intro_nodes import *
from .intro_subgraph.intro_edges import *
from .intro_subgraph.intro_state import *

from .questions_subgraph.questions_nodes import *
from .questions_subgraph.questions_edges import *
from .questions_subgraph.questions_state import *

from .outfits_subgraph.outfits_nodes import *
from .outfits_subgraph.outfits_edges import *
from .outfits_subgraph.outfits_state import *

from .outfit_layer_subgraph.outfit_layer_nodes import *
from .outfit_layer_subgraph.outfit_layer_edges import *
from .outfit_layer_subgraph.outfit_layer_state import *

def create_outfit_layer_subgraph():
    outfit_layer_workflow = StateGraph(OutfitLayerState)

    # outfit_layer_workflow.add_node("hmf", hmf)
    outfit_layer_workflow.add_node("get_style_rules_for_seed_item", get_style_rules_for_seed_item_condensed)
    outfit_layer_workflow.add_node("initialize_before_sequential_generation_of_layers", initialize_before_sequential_generation_of_layers)
    outfit_layer_workflow.add_node("generate_next_layer_item", generate_next_layer_item)
    # outfit_layer_workflow.add_node("generate_bag", generate_bag)
    # outfit_layer_workflow.add_node("generate_accessories", generate_accessories)
    # outfit_layer_workflow.add_node("finalize_layer_set", inalize_layer_set)
    outfit_layer_workflow.add_node("output_complete_outfit", output_complete_outfit)

    outfit_layer_workflow.set_entry_point("get_style_rules_for_seed_item")
    # outfit_layer_workflow.add_edge("hmf", "get_style_rules_for_seed_item")

    # Add an edge to terminate the subgraph
    outfit_layer_workflow.add_edge("get_style_rules_for_seed_item", "initialize_before_sequential_generation_of_layers")
    outfit_layer_workflow.add_edge("initialize_before_sequential_generation_of_layers", "generate_next_layer_item")
    outfit_layer_workflow.add_conditional_edges(
        "generate_next_layer_item",
        decide_to_generate_again,
        {
            "generate again": "generate_next_layer_item",
            "complete": "output_complete_outfit",
        },
    )
    # outfit_layer_workflow.add_conditional_edges(
    #     "initialize_before_sequential_generation_of_layers",
    #     decide_if_need_bag,
    #     {
    #         "needs bag": "generate_bag",
    #         "no bag needed": "finalize_layer_set",
    #     },
    # )
    # outfit_layer_workflow.add_conditional_edges(
    #     "initialize_before_sequential_generation_of_layers",
    #     decide_if_need_accessories,
    #     {
    #         "needs accessories": "generate_accessories",
    #         "no accessories needed": "finalize_layer_set",
    #     },
    # )
    # outfit_layer_workflow.add_edge("finalize_layer_set", "output_complete_outfit")
    outfit_layer_workflow.set_finish_point("output_complete_outfit")

    return outfit_layer_workflow

# def create_bulk_outfit_layer_subgraph():
#     if seed_item == "one_piece":
#         get_shoes()
#     else:
#         get_others()

def create_infinite_outfits_subgraph():

    outfits_workflow = create_outfits_subgraph()

    memory = MemorySaver()

    # Compile
    infinite_outfits_graph = outfits_workflow.compile(checkpointer=memory) #, interrupt_before=["websearch"])

    return infinite_outfits_graph

def create_outfits_subgraph():
    outfit_layer_subgraph = create_outfit_layer_subgraph().compile()

    outfits_workflow = StateGraph(GenerateOutfitsState)

    outfits_workflow.add_node("rewrite_outfit_request_context", rewrite_outfit_request_context)
    outfits_workflow.add_node("extract_weighted_colors", extract_weighted_colors)
    # outfits_workflow.add_node("extract_weighted_fabrics", extract_weighted_fabrics)
    # outfits_workflow.add_node("retrieve_subset", retrieve_subset)
    outfits_workflow.add_node("retrieve_clothing_subset", retrieve_clothing_subset)
    outfits_workflow.add_node("retrieve_shoes_subset", retrieve_shoes_subset)
    outfits_workflow.add_node("retrieve_accessories_subset", retrieve_accessories_subset)
    outfits_workflow.add_node("retrieve_bags_subset", retrieve_bags_subset)
    outfits_workflow.add_node("retrieve_jewelry_subset", retrieve_jewelry_subset)
    outfits_workflow.add_node("get_valid_seed_item_list", get_valid_seed_item_list)
    outfits_workflow.add_node("retrieve_seed_items", retrieve_seed_items)
    outfits_workflow.add_node("generate_one_outfit", outfit_layer_subgraph)
    # outfits_workflow.add_node("generate_one_outfit", generate_outfit)
    outfits_workflow.add_node("generate_outfit_cards", generate_outfit_cards)

    outfits_workflow.set_entry_point("rewrite_outfit_request_context")

    # Add an edge to terminate the subgraph
    outfits_workflow.add_edge("rewrite_outfit_request_context", "extract_weighted_colors")
    # outfits_workflow.add_edge("rewrite_outfit_request_context", "extract_weighted_fabrics")
    # outfits_workflow.add_edge("extract_weighted_colors", "retrieve_subset")
    outfits_workflow.add_edge("extract_weighted_colors", "retrieve_clothing_subset")
    outfits_workflow.add_edge("extract_weighted_colors", "retrieve_shoes_subset")
    outfits_workflow.add_edge("extract_weighted_colors", "retrieve_accessories_subset")
    outfits_workflow.add_edge("extract_weighted_colors", "retrieve_bags_subset")
    outfits_workflow.add_edge("extract_weighted_colors", "retrieve_jewelry_subset")
    # outfits_workflow.add_edge("extract_weighted_fabrics", "retrieve_subset")
    # outfits_workflow.add_edge("retrieve_subset", "retrieve_seed_items")
    outfits_workflow.add_edge("retrieve_clothing_subset", "get_valid_seed_item_list")
    outfits_workflow.add_edge("retrieve_shoes_subset", "get_valid_seed_item_list")
    outfits_workflow.add_edge("retrieve_accessories_subset", "get_valid_seed_item_list")
    outfits_workflow.add_edge("retrieve_bags_subset", "get_valid_seed_item_list")
    outfits_workflow.add_edge("retrieve_jewelry_subset", "get_valid_seed_item_list")
    outfits_workflow.add_edge("get_valid_seed_item_list", "retrieve_seed_items")
    outfits_workflow.add_conditional_edges("retrieve_seed_items", continue_to_outfits, ["generate_one_outfit"])
    outfits_workflow.add_edge("generate_one_outfit", "generate_outfit_cards")
    outfits_workflow.add_edge("generate_outfit_cards", END)

    return outfits_workflow

def create_questions_subgraph():
    questions_workflow = StateGraph(QuestionsState)

    questions_workflow.add_node("generate_missing_information", generate_missing_information)
    questions_workflow.add_node("segregate_missing_information", segregate_missing_information)
    questions_workflow.add_node("generate_response_with_followup", generate_response_with_followup)
    # questions_workflow.add_node("generate_followup_questions", generate_followup_questions)

    questions_workflow.set_conditional_entry_point(
        first_time_to_ask,
        {
            "first time to ask": "generate_missing_information",
            "reask followup questions": "segregate_missing_information",
        },
    )

     # Add an edge to terminate the subgraph
    questions_workflow.add_edge("generate_missing_information", "generate_response_with_followup")
    questions_workflow.add_edge("segregate_missing_information", "generate_response_with_followup")
    questions_workflow.add_edge("generate_response_with_followup", END)
    # questions_workflow.add_edge("generate_followup_questions", END)

    return questions_workflow

def create_graph():
    # intro_subgraph = create_intro_subgraph().compile()
    questions_subgraph = create_questions_subgraph().compile()
    outfits_subgraph = create_outfits_subgraph().compile()

    workflow = StateGraph(ConversationState) 

    ## Define the nodes

    workflow.add_node("define_outfit_context", define_outfit_context) # generate
    workflow.add_node("collect_all_missing_info", questions_subgraph) #collect_all_missing_info) # generate
    workflow.add_node("generate_outfits", outfits_subgraph) #generate_outfits)
    # workflow.add_node("outfit_changes", outfit_changes)
    workflow.add_node("finish_and_confirm", finish_and_confirm)
    # workflow.add_node("fallback", fallback)
    

    ## Build graph

    # Entry point
    workflow.set_conditional_entry_point(
        route_to_conversation_stage,
        {
            "define outfit context": "define_outfit_context",
            "collect all missing info": "collect_all_missing_info",
            "generate outfits": "generate_outfits",
            # "outfit changes": "outfit_changes",
            "finish and confirm": "finish_and_confirm",
            # "fallback response": "fallback",
        },
    )

    # Generate outfit edges
    workflow.add_edge("finish_and_confirm", END)
    # workflow.add_edge("regenerate_outfit", END)

    memory = MemorySaver()

    # Compile
    graph = workflow.compile(checkpointer=memory) #, interrupt_before=["websearch"])

    return graph

# def create_intro_subgraph():
#     intro_workflow = StateGraph(IntroState)

#     intro_workflow.add_node("ask_for_clarity", ask_for_clarity)
#     intro_workflow.add_node("rewrite_outfit_context", rewrite_outfit_context) 
#     intro_workflow.add_node("generate_followup_questions", generate_followup_questions)
#     intro_workflow.add_node("generate_response_before_outfit_generation", generate_response_before_outfit_generation)

#     intro_workflow.set_conditional_entry_point(
#         is_there_specific_request,
#         {
#             "rewrite outfit context": "rewrite_outfit_context",
#             "ask for clarity": "ask_for_clarity",
#         },
#     )

#     intro_workflow.add_conditional_edges(
#         "rewrite_outfit_context",
#         check_additional_details_needed,
#         {
#             "generate followup questions": "generate_followup_questions", # generation not grounded on documents, retry
#             "generate response before outfit generation": "generate_response_before_outfit_generation", # generation addresses question
#         },
#     )
    
#      # Add an edge to terminate the subgraph
#     intro_workflow.add_edge("ask_for_clarity", END)
#     intro_workflow.add_edge("generate_followup_questions", END)
#     intro_workflow.add_edge("generate_response_before_outfit_generation", END)

#     return intro_workflow

