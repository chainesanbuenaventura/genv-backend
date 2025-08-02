from langgraph.graph import StateGraph
from IPython.display import Image, display
from langchain.schema import Document
from langgraph.graph import END
from langgraph.checkpoint.memory import MemorySaver
from .conversation_state import ConversationState
from .conversation_nodes import *
from .conversation_edges import *

# from .outfit_request_subgraph.state import *
from .intro_subgraph.intro_nodes import *
from .intro_subgraph.intro_edges import *

def create_intro_subgraph():
    intro_workflow = StateGraph(IntroState)

    intro_workflow.add_node("ask_for_clarity", ask_for_clarity)
    intro_workflow.add_node("rewrite_outfit_context", rewrite_outfit_context) # generate

    intro_workflow.set_conditional_entry_point(
        is_there_specific_request,
        {
            "ask more clarity": "ask_more_clarity",
            "rewrite outfit context": "rewrite_outfit_context",
        },
    )
    
    # Add an edge to terminate the subgraph
    intro_workflow.add_edge("ask_more_clarity", END)
    # intro_workflow.set_termination("rewrite_outfit_request")
    

    return intro_workflow

def create_graph():
    define_outfit_context = create_intro_subgraph().compile()
    # ask_followup_questions = create_questions_subgraph().compile()
    # iterate_generation = create_iterate_subgraph().compile()

    conversation_workflow = StateGraph(ConversationState)

    conversation_workflow.add_node("define_outfit_context", define_outfit_context)
    # conversation_workflow.add_node("ask_followup_questions", ask_followup_questions) # generate
    # conversation_workflow.add_node("iterate_generation", iterate_generation) 

    # conversation_workflow.add_node("generate_outfits", generate_outfits)

    conversation_workflow.set_conditional_entry_point(
        route_to_conversation_stage,
        {
            "define outfit context": "define_outfit_context",
            # "ask followup questions": "ask_followup_questions",
            # "iterate generation": "iterate_generation",
        },
    )

    conversation_workflow.add_edge("define_outfit_context", END)
    # conversation_workflow.add_edge("generate_outfits", END)

    memory = MemorySaver()

    # Compile
    graph = conversation_workflow.compile(checkpointer=memory) #, interrupt_before=["websearch"])

    return graph

