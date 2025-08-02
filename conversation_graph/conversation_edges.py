from langchain.schema import Document
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END
from conversation_chains.main_graph import *
from tools import *
from conversation_graph import *

from langchain_openai import ChatOpenAI 
from conversation_graph.conversation_shared_resources import shared_resources_list
from conversation_graph.conversation_state import *

### Edges

def route_to_conversation_stage(state: ConversationState):
    """
    Node to determine the next stage in the outfit generation workflow.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        dict: Contains the next stage and reasoning for the decision.
    """
    print("---DETERMINE NEXT STAGE---")
    question = state["question"]
    messages = state["messages"]

    print("shared_resources_list: ", shared_resources_list)

    # Invoke the stage transition chain
    transition_result = shared_resources_list["stage_transition_chain"].invoke(
        {
            "messages": messages,
            "question": question,
        }
    )

    # Log outputs for debugging
    print("Next Stage:", transition_result.next_stage)
    print("Explanation:", transition_result.explanation)

    if transition_result.next_stage == 1:
        print("---ROUTE CONVERSATION TO DEFINE OUTFIT CONTEXT---")
        return "define outfit context"
    # elif scenario.scenario_number in [2, 3]:
    #     print("---ROUTE CONVERSATION TO GENERATE---")
    #     return "generate"
    # elif scenario.scenario_number == 4:
    #     print("---ROUTE QUESTION TO SOURCES---")
    #     source = shared_resources_list["sources_router_chain"].invoke(
    #         {
    #             "question": question, 
    #             "messages": messages
    #         }
    #     ) 
    #     if source.datasource == 'websearch':
    #         print("---ROUTE QUESTION TO WEB SEARCH---")
    #         return "websearch"
    #     elif source.datasource == 'vectorstore':
    #         print("---ROUTE QUESTION TO VECTORSTORE---")
    #     return "vectorstore"
    # elif scenario.scenario_number == 5:
    #     return "fallback"

