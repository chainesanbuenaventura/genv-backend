# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import WebBaseLoader
# from langchain_community.vectorstores import SKLearnVectorStore
# from langchain.embeddings.openai import OpenAIEmbeddings
# from langchain_core.vectorstores import InMemoryVectorStore
# from langchain_openai import OpenAIEmbeddings
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_community.document_loaders import PyPDFLoader
# from langchain.schema import AIMessage, HumanMessage, SystemMessage
# from langchain.schema import Document
# from langgraph.graph import END

# from fastapi import Request

# from chains.main_graph import *
# from tools import *
# from conversation_graph import *
# from conversation_graph.conversation_shared_resources import shared_resources_list
# from conversation_graph.conversation_state import *

# from langchain_openai import ChatOpenAI 
# from langchain_mistralai import ChatMistralAI

# ### Nodes
# def check_active_request_status(state: ConversationState):
#     """
#     Check if an outfit request is already ongoing or if a new request needs to be initiated.

#     Args:
#         state (dict): The current graph state

#     Returns:
#         state (dict): Contains the status of the outfit request and updates the ongoing_request in the state if applicable.
#     """
#     print("---CHECK OUTFIT REQUEST STATUS---")
#     question = state["question"]
#     messages = state["messages"]
    
#     # Ensure 'active_request' exists in the state
#     if "active_request" not in state:
#         state["active_request"] = ""
    
#     if "active_request_status" not in state:
#         state["active_request_status"] = "none"

#     # Ensure 'missing_information' exists in the state
#     if "missing_information" not in state:
#         state["missing_information"] = []

#     # Ensure 'request_history' exists in the state
#     if "request_history" not in state:
#         state["request_history"] = []

#     # Use the chain to check if there is an ongoing outfit request
#     active_request_status = shared_resources_list["check_active_outfit_request_chain"].invoke(
#         {
#             "question": question,
#             "messages": messages,
#             "active_request": state["active_request"],
#             "active_request_status": state["active_request_status"],
#             "request_history": state["request_history"],
#             "missing_information": state["missing_information"]
#         }
#     )
    
#     # Logging for debugging purposes
#     print("new_active_request_status: ", active_request_status.new_active_request_status, "reason:", active_request_status.reason)

#     # Return updated state
#     return {
#         "active_request_status": active_request_status.new_active_request_status,
#     }

