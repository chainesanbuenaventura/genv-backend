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

from chains.questions_subgraph import *
from tools import *
from graph.questions_subgraph import *
from graph.questions_subgraph.questions_state import *

from langchain_openai import ChatOpenAI 
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama

# Initialize the resources once
# llm = ChatOpenAI()
# local_llm = 'llama3.2'
# llm = ChatOllama(model=local_llm, temperature=0)

### Nodes

def generate_missing_information(state: QuestionsState):
    """
    Node to regenerate follow-up questions for missing details.

    Args:
        state (IntroState): The current graph state.

    Returns:
        dict: Contains the follow-up questions as 'generation' and updated state.
    """
    # outfit_context = state["outfit_context"]
    messages = state["messages"]
    question = state["question"]
    model = state.get("model", "openai")
    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)
    
    missing_information_chain = get_missing_information_chain(llm)
    # missing_information = state["missing_information"]

    print("---GENERATING MISSING INFORMATION---")

    # Invoke the chain to identify missing information
    missing_info_result = missing_information_chain.invoke(
        {
            "messages": messages,
            "question": question,
            "name": state["user_profile"]["first_name"] + " " + state["user_profile"]["last_name"],
            "age": state["user_profile"]["age"], 
            "gender": state["user_profile"]["gender"],
        }
    )

    # Log the output for debugging
    print("Outfit Request Context:", missing_info_result.outfit_request_context)
    print("Missing Information:", missing_info_result.missing_information)
    print("Explanation:", missing_info_result.explanation)

    # Update the state and return
    return {
        "missing_information": missing_info_result.missing_information,
        "still_missing": missing_info_result.missing_information,
        "outfit_request_context": missing_info_result.outfit_request_context,
    }

def segregate_missing_information(state: QuestionsState):
    """
    Node to segregate missing information into answered and still missing categories.

    Args:
        state (QuestionsState): The current graph state containing the conversation context.

    Returns:
        dict: Contains segregated information with lists of answered and still missing details.
    """
    messages = state["messages"]
    question = state["question"]
    missing_information = state["missing_information"]
    model = state.get("model", "openai")
    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)

    # Invoke the segregation chain
    segregation_chain = get_segregate_information_with_answers_chain(llm)
    segregation_result = segregation_chain.invoke(
        {
            "messages": messages,
            "question": question,
            "missing_information": missing_information,
            "answered": state.get("answered", []),
            "answers": state.get("answered", []),
        }
    )

    # Log the output for debugging
    print("Answered:", segregation_result.answered)
    print("Still Missing:", segregation_result.still_missing)
    print("Answers:", segregation_result.answers)

    # Update the state and return
    return {
        "answered": segregation_result.answered,
        "still_missing": segregation_result.still_missing,
        "answers": segregation_result.answers,
        "stage": 2, 
    }

def generate_response_with_followup(state: QuestionsState):
    """
    Node to generate a response with follow-up questions based on unresolved details.

    Args:
        state (QuestionsState): The current graph state containing unresolved details.

    Returns:
        dict: Contains the generated response and updated lists of missing information.
    """
    messages = state["messages"]
    question = state["question"]
    still_missing = state.get("still_missing", state["missing_information"])
    model = state.get("model", "openai")
    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)

    # Invoke the follow-up response chain
    followup_response_chain = get_generate_followup_response_chain(llm)
    followup_result = followup_response_chain.invoke(
        {
            "messages": messages,
            "question": question,
            "still_missing": still_missing,
        }
    )

    messages = [
        HumanMessage(content=question),
        SystemMessage(content=followup_result.response),
    ]

    # Log the output for debugging
    print("Response:", followup_result.response)

    # Update the state and return
    return {
        "generation": followup_result.response,
        "outfits": [],
        "stage": 2, 
    }

def generate_followup_questions(state: QuestionsState):
    """
    Node to regenerate follow-up questions for missing details.

    Args:
        state (IntroState): The current graph state.

    Returns:
        dict: Contains the follow-up questions as 'generation' and updated state.
    """
    # outfit_context = state["outfit_context"]
    messages = state["messages"]
    question = state["question"]
    missing_information = state["missing_information"]
    outfit_request_context = state["outfit_request_context"]
    model = state.get("model", "openai")
    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)
        
    generate_followup_questions_chain = get_generate_followup_questions_chain(llm)

    print("---GENERATING FOLLOW-UP QUESTIONS---")

    # Invoke the chain to regenerate follow-up questions
    followup_result = generate_followup_questions_chain.invoke(
        {
            # "outfit_context": outfit_context,
            "messages": messages,
            "question": question,
            "missing_information": missing_information,
            "outfit_request_context": outfit_request_context,
            "name": state["user_profile"]["first_name"] + " " + state["user_profile"]["last_name"],
            "age": state["user_profile"]["age"], 
            "gender": state["user_profile"]["gender"],
        }
    )
 
    messages = [
        HumanMessage(content=question),
        SystemMessage(content=followup_result.followup_questions),
    ]

    # Log the output for debugging
    print("Follow-up Questions:", followup_result.followup_questions)
    print("Still Missing Information:", followup_result.still_missing)
    print("Answered Questions:", followup_result.answered)

    # Update the state and return
    return {
        "generation": followup_result.followup_questions,
        "outfits": [],
        "still_missing": followup_result.still_missing,
        "answered": followup_result.answered,
        "messages": messages,
        "stage": 2, 
    }

def rewrite_outfit_context_with_additional_details(state: QuestionsState):
    """
    Node to rewrite the outfit context with additional details and conversation context.

    Args:
        state (IntroState): The current graph state.

    Returns:
        dict: The rewritten outfit context and updated state.
    """
    outfit_context = state["outfit_context"]
    messages = state["messages"]
    question = state["question"]
    missing_information = state["missing_information"]
    rewrite_outfit_context_with_additional_details_chain = get_rewrite_outfit_context_with_additional_details_chain(llm)

    print("---REWRITING OUTFIT CONTEXT WITH ADDITIONAL DETAILS---")

    # Invoke the chain to rewrite the outfit context
    rewritten_context_result = rewrite_outfit_context_with_additional_details_chain.invoke(
        {
            "outfit_context": outfit_context,
            "messages": messages,
            "question": question,
            "missing_information": missing_information,
        }
    )

    # Log the output for debugging
    print("Rewritten Context:", rewritten_context_result.rewritten_context)

    # Update the state and return
    return {
        "outfit_context": rewritten_context_result.rewritten_context,
    }

def regenerate_followup_questions(state: QuestionsState):
    """
    Node to regenerate follow-up questions for missing details.

    Args:
        state (IntroState): The current graph state.

    Returns:
        dict: Contains the follow-up questions as 'generation' and updated state.
    """
    outfit_context = state["outfit_context"]
    messages = state["messages"]
    question = state["question"]
    missing_information = state["missing_information"]
    regenerate_followup_questions_chain = get_regenerate_followup_questions_chain(llm)

    print("---REGENERATING FOLLOW-UP QUESTIONS---")

    # Invoke the chain to regenerate follow-up questions
    followup_result = regenerate_followup_questions_chain.invoke(
        {
            "outfit_context": outfit_context,
            "messages": messages,
            "question": question,
            "missing_information": missing_information,
        }
    )

    # Log the output for debugging
    print("Follow-up Questions:", followup_result.followup_questions)
    print("Explanation:", followup_result.explanation)

    # Update the state and return
    return {
        "generation": followup_result.followup_questions,
        "outfits": [],
    }

def generate_response_before_outfit_generation(state: QuestionsState):
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
        "generation": f"Got it! Please wait while I generate outfits for you! [{outfit_context}]",
        "outfits": [],
    }