from langchain.schema import Document
from typing import Literal
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import END
from chains.main_graph import *
from chains.questions_subgraph import *
from tools import *
from graph import *

from langchain_openai import ChatOpenAI 
from chains.main_graph import *
from chains.questions_subgraph import *
from graph.shared_resources import shared_resources_list
from graph.state import *

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

# Initialize the resources once
# llm = ChatOpenAI()
# local_llm = 'llama3.2'
# llm = ChatOllama(model=local_llm, temperature=0)

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
    model = state.get("model", "openai")
    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)
    # stage = state["stage"]

    stage_transition_chain = get_stage_transition_chain(llm)
    # if "outfit_context" not in state:  
    #     state["outfit_context"] = ""

    # print("shared_resources_list: ", shared_resources_list)

    print("User: ", state.get("question"))
    print("Last Conversation: ", state.get("stage", 1))
        
    # if state.get("stage", 1) == 3:
    #     missing_information_check_chain = get_missing_information_check_chain(llm)
    #     missing_information_check_output = missing_information_check_chain.invoke(
    #         {
    #             "missing_information": state["missing_information"],
    #             "messages": messages,
    #             "question": question,
    #         }
    #     )

    #     if len(missing_information_check_output.still_missing) > 0:
    #         return "collect all missing info"
    #     else:
    #         return "generate outfits"

    try:
        # Invoke the stage transition chain
        transition_result = stage_transition_chain.invoke(
            {
                "messages": messages,
                "question": question,
                "stage": state.get("stage", 1),
            }
        )
        next_stage_number = transition_result.next_stage_number
        explanation = transition_result.explanation
    except:
        next_stage_number = 4
        explanation = "User continues to engage after outfit generation."

    # Log outputs for debugging
    print("Next Stage:", next_stage_number)
    print("Explanation:", explanation)

    # if next_stage_number == 0:
    #     print("---ROUTE CONVERSATION TO FALLBACK RESPONSE---")
    #     return "fallback response"
    if next_stage_number == 1:
        if int(state.get("stage", 1)) > 1: 
            print("---SEEMS TO JUMP BACK TO 1---")
            next_stage_number = state["stage"]
        print("---ROUTE CONVERSATION TO DEFINE OUTFIT CONTEXT---")
        return "define outfit context"
    if next_stage_number == 2:
        # do_we_need_followup_questions
        if len(state.get("missing_information", [])) == 0:
            print("---FIRST TIME TO ASK QUESTIONS---")
            # If previous stage was already asking
            
            # if state.get("stage", 2):
            #     return "generate outfits"

            # llm = ChatOpenAI()
            need_more_info_chain = get_need_more_info_chain(llm)
            need_more_info_output = need_more_info_chain.invoke(
                {
                    "messages": messages,
                    "question": question,
                    "name": state["user_profile"]["first_name"] + " " + state["user_profile"]["last_name"],
                    "age": state["user_profile"]["age"], 
                    "gender": state["user_profile"]["gender"],
                }
            )
            if need_more_info_output.need_more_info == "yes":
                print("---NEED MORE INFO---")
                return "collect all missing info"
            else:
                print("---ROUTE OUTFIT GENERATION DIRECTLY WITHOUT QUESTIONS---")
                return "generate outfits"
        else:
            if len(state["missing_information"]) == len(state.get("answered", [])):
                print("---ALL QUESTIONS ANSWERED---")
                return "generate outfits"
            print("---ROUTE CONVERSATION TO ASKING FOLLOWUP QUESTIONS UNTIL COMPLETE---")
            return "collect all missing info"
    elif next_stage_number == 3:
        print("---ROUTE CONVERSATION TO GENERATE OUTFITS---")
        return "generate outfits"
    # elif next_stage_number == 4:
    #     print("---ROUTE CONVERSATION TO OUTFIT CHANGES---")
    #     return "outfit changes"
    elif next_stage_number == 4:
        print("---ROUTE CONVERSATION TO FINISH AND CONFIRM---")
        return "finish and confirm"