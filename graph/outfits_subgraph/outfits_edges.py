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
 
from chains.outfits_subgraph import *
from tools import *
from graph.outfits_subgraph import *
from graph.outfits_subgraph.outfits_state import *

from utils import *

from langchain_openai import ChatOpenAI 
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama
from langgraph.types import Send

from .outfits_nodes import *

### Edges

def continue_to_outfits(state: GenerateOutfitsState):
    print("---GENERATE OUTFIT FOR EACH SEED---")
    # print("State Keys:", state.keys())
    return [
        Send(
            "generate_one_outfit", 
            {
                "seed_item": seed_item,
                "subset_items_subgraph": state["subset_items"],
                "outfit_request_context_subgraph": state["outfit_request_context"],  # Propagate this explicitly
            }
        )
        for seed_item in state["seed_items"]
    ]

# def continue_to_outfits(state: GenerateOutfitsState):
#     # Return a list of `Send` objects
#     # Each `Send` object consists of the name of a node in the graph
#     # as well as the state to send to that node
#     return [
#         Send("generate_outfit", {"seed_item": seed_item, "subset_items": state["subset_items"], "outfit_request_context": state["outfit_request_context"]})
#         for seed_item in state["seed_items"]
#     ]