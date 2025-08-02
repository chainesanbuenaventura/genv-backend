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

# from conversation_chains.main_graph import *
# from tools import *
# from conversation_graph import *
# from conversation_graph.conversation_shared_resources import shared_resources_list
# from conversation_graph.conversation_state import *

# from langchain_openai import ChatOpenAI 
# from langchain_mistralai import ChatMistralAI

# ### Nodes
# def generate_outfits(state: ConversationState):
#     """
#     Retrieve documents from vectorstore

#     Args:
#         state (dict): The current graph state

#     Returns:
#         state (dict): New key added to state, documents, that contains retrieved documents
#     """
#     print("---GENERATE OUTFITS---")

#     return {
#         "generation": "Got it! Generating outfits for you."
#     }

