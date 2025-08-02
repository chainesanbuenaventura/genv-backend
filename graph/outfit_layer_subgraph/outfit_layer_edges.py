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

from .outfit_layer_nodes import *
from .outfit_layer_edges import *
from .outfit_layer_state import *

### Edges

def decide_to_generate_again(state: OutfitLayerState):
    """
    Node to determine the next stage in the outfit generation workflow.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        dict: Contains the next stage and reasoning for the decision.
    """
    print("---DECIDE TO GENERATE AGAIN---")
    layers_done = state["layers_done"]

    # print("Check generate again node: ", layers_done)

    if not set(LAYERS.keys()).issubset(layers_done):    
        print("---GENERATE NEXT LAYER ITEM---")
        return "generate again"
    else:
        print("---LAYER SET COMPLETE---")
        # print(layers_done, LAYERS.keys())
        return "complete"
    
def decide_if_need_bag(state: OutfitLayerState):
    """
    Node to determine the next stage in the outfit generation workflow.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        dict: Contains the next stage and reasoning for the decision.
    """
    print("---DECIDE IF NEED BAG---")
    model = state.get("model", "openai")
    outfit_request_context_subgraph = state.get("outfit_request_context_subgraph", "")
    seed_item = state.get("seed_item", "")

    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)

    bag_requirement_chain = get_bag_requirement_chain(llm)

    # Invoke the stage transition chain
    result = bag_requirement_chain.invoke(
        {
            "outfit_request_context_subgraph": outfit_request_context_subgraph,
            "seed_item": seed_item,
        }
    )

    print("Needs Bag: ", result.needs_bag)
    print("Explanation: ", result.explanation)

    if result.needs_bag.lower() == "yes":    
        print("---GENERATE BAG---")
        return "needs bag"
    else:
        print("---NO BAG NEEDED---")
        # print(layers_done, LAYERS.keys())
        return "no bag needed"

def decide_if_need_accessories(state: OutfitLayerState):
    """
    Node to determine the next stage in the outfit generation workflow.

    Args:
        state (ConversationState): The current state of the conversation.

    Returns:
        dict: Contains the next stage and reasoning for the decision.
    """
    print("---DECIDE IF NEED BAG---")
    model = state.get("model", "openai")
    outfit_request_context_subgraph = state.get("outfit_request_context_subgraph", "")
    seed_item = state.get("seed_item", "")

    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)

    accessories_requirement_chain = get_accessories_requirement_chain(llm)

    # Invoke the stage transition chain
    result = accessories_requirement_chain.invoke(
        {
            "outfit_request_context_subgraph": outfit_request_context_subgraph,
            "seed_item": seed_item,
        }
    )

    print("Needs Bag: ", result.needs_accessories)
    print("Explanation: ", result.explanation)

    if result.needs_accessories.lower() == "yes":    
        print("---GENERATE ACCESSORIES---")
        return "needs accessories"
    else:
        print("---NO ACCESSORIES NEEDED---")
        # print(layers_done, LAYERS.keys())
        return "no accessories needed"