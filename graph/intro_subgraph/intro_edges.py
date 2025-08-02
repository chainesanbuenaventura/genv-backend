from langchain.schema import Document
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END
from chains.main_graph import *
from tools import *
from graph import *

from langchain_openai import ChatOpenAI 
from graph.shared_resources import shared_resources_list

from graph.intro_subgraph.intro_state import *

### Edges

def is_there_specific_request(state: IntroState):
    """
    Route the conversation between checking for a specific outfit request and validating its completeness.

    Args:
        state (GraphState): The current graph state.

    Returns:
        str: The next node to call in the workflow.
    """
    question = state["question"]
    messages = state["messages"]
    print(state["question"])
    print("---DEFINE OUTFIT CONTEXT---")
    
    # Invoke the chain to determine if there is a specific request
    is_specific_request = shared_resources_list["is_there_specific_request_chain"].invoke(
        {
            "question": question,
            "messages": messages,
        }
    )
    
    if is_specific_request.is_specific_request.lower() == 'yes':
        print("---SPECIFIC OUTFIT REQUEST DETECTED---")
        
        # # Check if the specific request is complete
        # is_complete = shared_resources_list["is_outfit_context_complete_chain"].invoke(
        #     {
        #         "question": question,
        #         "messages": messages,
        #     }
        # )
        # if is_complete.is_complete.lower() == "yes":
        #     print("---REQUEST IS COMPLETE---")
        return "rewrite outfit context"
        # else:
        #     print("---REQUEST IS INCOMPLETE---")
        #     return "ask for clarity"
    else:
        print("---NO SPECIFIC REQUEST---")
        return "ask for clarity"
    
def check_additional_details_needed(state: IntroState):
    """
    Node to check if additional details are required to proceed with generating outfit recommendations.

    Args:
        state (IntroState): The current graph state.

    Returns:
        str: The next node to call based on whether additional details are needed.
    """
    question = state["question"]
    messages = state["messages"]
    outfit_context = state["outfit_context"]
    print("---CHECKING ADDITIONAL DETAILS NEEDED---")
    
    # Invoke the chain to determine if additional details are required
    additional_details_needed = shared_resources_list["check_additional_details_needed_chain"].invoke(
        {
            "question": question,
            "messages": messages,
            "outfit_context": outfit_context,
        }
    )
    
    # Log the response for debugging
    print("Additional Details Needed:", additional_details_needed.additional_details_needed)
    print("Reason:", additional_details_needed.explanation)

    if additional_details_needed.additional_details_needed.lower() == "yes":
        print("---ADDITIONAL DETAILS REQUIRED---")
        return "generate followup questions"
    else:
        print("---DETAILS SUFFICIENT---")
        return "generate response before outfit generation"

