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
from chains.questions_subgraph import *

from graph.questions_subgraph.questions_state import *

from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

# Initialize the resources once
# llm = ChatOpenAI()
# local_llm = 'llama3.2'
# llm = ChatOllama(model=local_llm, temperature=0)

### Edges

def first_time_to_ask(state: QuestionsState):
    """
    Edge to verify if all missing information and follow-up questions have been answered.

    Args:
        state (IntroState): The current graph state containing the conversation context.

    Returns:
        str: The next node to call in the workflow.
    """
    # Extract required inputs from the state
    missing_information = state["missing_information"]
    messages = state["messages"]
    question = state["question"]
    # outfit_context = state["outfit_context"]
    print("---ARE ALL FOLLOWUP QUESTIONS ANSWERED---")

    # Log the results for debugging
    print("Missing Information:", missing_information)
    # Determine the next node based on the result
    if len(missing_information) == 0:
        print("---FIRST TIME TO ASK QUESTIONS--")
        return "first time to ask"
    else:
        print("---REASK FOLLOWUP QUESTIONS---")
        return "reask followup questions"
    
def are_all_followup_questions_answered(state: QuestionsState):
    """
    Edge to verify if all missing information and follow-up questions have been answered.

    Args:
        state (IntroState): The current graph state containing the conversation context.

    Returns:
        str: The next node to call in the workflow.
    """
    # Extract required inputs from the state
    missing_information = state["missing_information"]
    messages = state["messages"]
    question = state["question"]
    outfit_context = state["outfit_context"]
    print("---ARE ALL FOLLOWUP QUESTIONS ANSWERED---")

    # Invoke the chain to check if all missing information is answered
    result = shared_resources_list["check_missing_information_chain"].invoke(
        {
            "missing_information": missing_information,
            "messages": messages,
            "question": question,
            "outfit_context": outfit_context,
        }
    )

    # Log the results for debugging
    print("All Answered:", result.all_answered)
    print("Reasoning:", result.reasoning)
    # Determine the next node based on the result
    if result.all_answered.lower() == "yes":
        print("---ALL QUESTIONS ANSWERED---")
        return "rewrite outfit request with additional details"
    else:
        print("---MISSING INFORMATION REMAINS---")
        return "regenerate_followup_questions"

# def are_all_followup_questions_answered(state: QuestionsState):
#     """
#     Edge to verify if all missing information and follow-up questions have been answered.

#     Args:
#         state (IntroState): The current graph state containing the conversation context.

#     Returns:
#         str: The next node to call in the workflow.
#     """
#     # Extract required inputs from the state
#     missing_information = state["missing_information"]
#     messages = state["messages"]
#     question = state["question"]
#     outfit_context = state["outfit_context"]
#     print("---ARE ALL FOLLOWUP QUESTIONS ANSWERED---")

#     # Invoke the chain to check if all missing information is answered
#     result = shared_resources_list["check_missing_information_chain"].invoke(
#         {
#             "missing_information": missing_information,
#             "messages": messages,
#             "question": question,
#             "outfit_context": outfit_context,
#         }
#     )

#     # Log the results for debugging
#     print("All Answered:", result.all_answered)
#     print("Reasoning:", result.reasoning)
#     # Determine the next node based on the result
#     if result.all_answered.lower() == "yes":
#         print("---ALL QUESTIONS ANSWERED---")
#         return "rewrite outfit request with additional details"
#     else:
#         print("---MISSING INFORMATION REMAINS---")
#         return "regenerate_followup_questions"