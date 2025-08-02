from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import SKLearnVectorStore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import AIMessage, HumanMessage, SystemMessage
from langchain.schema import Document
from langgraph.graph import END

from fastapi import Request

from chains.main_graph import *
from tools import *
from graph.intro_subgraph import *
from graph.intro_subgraph.intro_state import *

from langchain_openai import ChatOpenAI 
from langchain_mistralai import ChatMistralAI

### Nodes
def ask_for_clarity(state: IntroState):
    """
    Node to guide the user toward providing specific outfit context.

    Args:
        state (dict): The current state of the conversation.

    Returns:
        dict: Updated state with clarity check results and guidance for the user.
    """
    print("---ASK FOR CLARITY NODE---")
    
    question = state["question"]
    messages = state["messages"]

    if "outfit_context" not in state:
        state["outfit_context"] = ""

    # Invoke the clarity chain
    clarity_response = shared_resources_list["ask_for_clarity_chain"].invoke(
        {
            "conversation_history": messages,
            "user_message": question,
        }
    )

    # Logging for debugging purposes
    print("Clarity Response:", clarity_response)

    # Update the state
    state["has_outfit_context"] = clarity_response.has_outfit_context
    state["guidance"] = clarity_response.guidance

    # Return the updated state
    return {
        "generation": clarity_response.guidance,
    }

def rewrite_outfit_context(state: IntroState):
    """
    Rewrite the user's outfit request to make it more concise, clear, and actionable.

    Args:
        state (dict): The current state of the conversation, including the user's question and messages.

    Returns:
        dict: Contains the rewritten outfit context.
    """
    print("---REWRITE OUTFIT CONTEXT---")
    question = state["question"]
    messages = state["messages"]
    
    # Ensure 'rewritten_context' exists in the state
    if "outfit_context" not in state:
        state["outfit_context"] = ""

    # Use the chain to rewrite the outfit request
    rewritten_context = shared_resources_list["rewrite_outfit_context_chain"].invoke(
        {
            "question": question,
            "messages": messages,
        }
    )

    # Logging for debugging purposes
    print("rewritten_context:", rewritten_context.outfit_context)

    # Return updated state with the rewritten context
    return {
        "outfit_context": rewritten_context.outfit_context,
        "generation": rewritten_context.outfit_context,
    }

def generate_followup_questions(state: IntroState):
    """
    Node to check if minimum necessary details are provided for generating outfit recommendations.

    Args:
        state (IntroState): The current graph state.

    Returns:
        dict: The updated state with generation and missing information.
    """
    outfit_context = state["outfit_context"]
    print("---CHECKING MINIMUM NECESSARY DETAILS---")

    # Invoke the chain to determine missing details
    response = shared_resources_list["minimum_details_chain"].invoke(
        {
            "outfit_context": outfit_context,
        }
    )

    # Log the response for debugging
    print("Missing Information:", response.missing_information)
    print("Follow-Up Questions:", response.followup_questions)

    return {
        "missing_information": response.missing_information,
        "generation": response.followup_questions,
    }

def generate_response_before_outfit_generation(state: IntroState):
    """
    Retrieve documents from vectorstore

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---TOPIC OUTSIDE FASHION---")
    outfit_context = state["outfit_context"]

    return {
        "generation": f"Got it! Please wait while I generate outfits for you! [{outfit_context}]"
    }

