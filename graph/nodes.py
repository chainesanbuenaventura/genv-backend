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
from graph import *
from graph.shared_resources import shared_resources_list
from graph.state import *

from langchain_openai import ChatOpenAI 
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama

# Initialize the resources once
# llm = ChatOpenAI()
# local_llm = 'llama3.2'
# llm = ChatOllama(model=local_llm, temperature=0)

### Nodes

def fallback(state: ConversationState):
    """
    Retrieve documents from vectorstore

    Args:
        state (dict): The current graph state

    Returns:
        state (dict): New key added to state, documents, that contains retrieved documents
    """
    print("---TOPIC OUTSIDE FASHION---")

    return {
        "generation": "I'm sorry. I can only assist with fashion related questions and outfit requests.",
        "outfits": [],
    }

def define_outfit_context(state: ConversationState):
    """
    Node to nudge the user to provide an outfit context.

    Args:
        state (IntroState): The current state of the conversation.

    Returns:
        dict: Updated state with the nudge message.
    """
    # Extract conversation history and last user message from the state
    messages = state.get("messages", ["👋 Hello! I'm ESTYL AI! Can I help you with any outfit recommendations today?"])
    question = state["question"]
    model = state.get("model", "openai")
    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)

    print("---DEFINE OUTFIT CONTEXT---")
    # print(f"Conversation History: {messages}")
    # print(f"User Message: {question}")

    ask_to_define_outfit_context_chain = get_ask_to_define_outfit_context_chain(llm)

    # Invoke the "Nudge Outfit Context" chain
    nudge_response = ask_to_define_outfit_context_chain.invoke(
        {
            "conversation_history": messages,
            "user_message": question,
            "name": state["user_profile"]["first_name"] + " " + state["user_profile"]["last_name"],
            "age": state["user_profile"]["age"], 
            "gender": state["user_profile"]["gender"],
        }
    )

    # Log the generated nudge response
    # print(f"Nudge Response: {nudge_response.nudge_message}")

    messages = [
        HumanMessage(content=question),
        SystemMessage(content=nudge_response.nudge_message),
    ]
    return {
        "generation": nudge_response.nudge_message, 
        "outfits": [],
        "messages": messages,
        "missing_information": [],
        "stage": 1,
    }

def collect_all_missing_info(state: ConversationState):
    """
    Node to collect all missing information dynamically.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Updated state with generated follow-up questions.
    """
    # Extract the relevant inputs from the state
    # outfit_context = state["outfit_context"]
    # missing_information = state["missing_information"]
    messages = state["messages"]
    question = state["question"]
    model = state.get("model", "openai")
    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)
    collect_all_missing_info_chain = get_collect_all_missing_info_chain(llm)

    print("---COLLECTING ALL MISSING INFO NODE---")
    # print(f"Outfit Context: {outfit_context}")
    # print(f"Missing Information: {missing_information}")
    # print(f"Conversation History: {conversation_history}")
    # print(f"Conversation History: {messages}")
    # print(f"User Message: {question}")

    # Invoke the chain to generate follow-up questions
    response = collect_all_missing_info_chain.invoke(
        {
            # "outfit_context": outfit_context,
            # "missing_information": missing_information,
            "messages": messages,
            "question": question,
        }
    )

    # Log the response for debugging
    followup_questions = response.followup_questions
    reasoning = response.reasoning

    # print("Generated Follow-Up Questions:", followup_questions)
    # print("Reasoning for Questions:", reasoning)

    messages = [
        HumanMessage(content=question),
        SystemMessage(content=followup_questions),
    ]
    return {
        "generation":followup_questions, 
        "outfits": [],
        "messages": messages,
    }

# def generate_outfits(state: ConversationState):
#     """
#     Retrieve documents from vectorstore

#     Args:
#         state (dict): The current graph state

#     Returns:
#         state (dict): New key added to state, documents, that contains retrieved documents
#     """
#     print("---GENERATING OUTFITS---")
#     messages = state["messages"]
#     question = state["question"]
#     rewrite_outfit_context_with_additional_details_chain = get_rewrite_outfit_context_with_additional_details_chain(llm)

#     # print(f"Conversation History: {messages}")
#     # print(f"User Message: {question}")

#     # Invoke the chain to generate follow-up questions
#     response = rewrite_outfit_context_with_additional_details_chain.invoke(
#         {
#             # "outfit_context": outfit_context,
#             # "missing_information": missing_information,
#             "messages": messages,
#             "outfits": [],
#             "question": question,
#         }
#     )

#     # print("Generated Follow-Up Questions:", response.rewritten_context)

#     messages = [
#         HumanMessage(content=question),
#         SystemMessage(content="Got it! Generating outfits for you!"),
#         SystemMessage(content="Outfit COntext with Details: " + response.rewritten_context),
#     ]

#     return {
#         "generation": f"Got it! Generating outfits for you! \n\nOutfit Request: {response.rewritten_context}",
#         "outfits": [],
#         "outfit_context": response.rewritten_context,
#     }

def outfit_changes(state: ConversationState):
    """
    Node to handle outfit changes or variations based on user feedback.

    Args:
        state (ConversationState): The current graph state, including conversation history and user feedback.

    Returns:
        dict: Updated state with the feedback summary and response to the user.
    """
    # Extract the relevant inputs from the state
    messages = state["messages"]
    question = state["question"]
    model = state.get("model", "openai")
    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)
    outfit_change_chain = get_outfit_change_chain(llm)

    print("---OUTFIT CHANGE NODE---")
    # print(f"Conversation History: {messages}")
    # print(f"User Feedback: {question}")

    # Invoke the outfit change chain
    response = outfit_change_chain.invoke(
        {
            "messages": messages,
            "question": question,
            "outfit_request_context": state["outfit_request_context"],
        }
    )

    feedback_summary = response.feedback_summary
    response_to_the_user = response.response_to_the_user

    print("Feedback Summary:", feedback_summary)
    print("Response to User:", response_to_the_user)

    messages = [
        HumanMessage(content=question),
        SystemMessage(content=response_to_the_user),
    ]

    return {
        "generation": response_to_the_user,
        "outfits": [],
        "messages": messages,
    }


# Define the Finish and Confirm Node
def finish_and_confirm(state: ConversationState):
    """
    Node to finalize the conversation by summarizing the recommendation and confirming completion.

    Args:
        state (ConversationState): The current graph state, including conversation history.

    Returns:
        dict: Updated state with the summary and confirmation message.
    """
    messages = state["messages"]
    question = state["question"]
    model = state.get("model", "openai")
    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)
    finish_and_confirm_chain = get_finish_and_confirm_chain(llm)
    
    print("---FINISH AND CONFIRM NODE---")
    # print(f"Conversation History: {messages}")
    # print(f"User Feedback: {question}")

    # print("outfit_request_context: ", state["outfit_request_context"])
    # print("outfits: ", state[""])

    try:
        # Invoke the Finish and Confirm chain
        response = finish_and_confirm_chain.invoke(
            {
                "messages": messages,
                "question": question,
                # "outfit_request_context": state["outfit_request_context"],
                # "outfits": state["outfits"],
            }
        )

        # print("response ", response)

        # summary = response.summary
        confirmation_message = response.confirmation_message
    except:
        confirmation_message = "I'm sorry, I could not help you any further. Please restart conversation."

    # print("Summary:", summary)
    # print("Confirmation Message:", confirmation_message)

    messages = [
        HumanMessage(content=question),
        SystemMessage(content=confirmation_message),
    ]

    return {
        "generation": confirmation_message,
        "outfits": [],
        "messages": messages,
        "stage": 4,
    }
