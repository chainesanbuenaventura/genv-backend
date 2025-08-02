from fastapi import FastAPI, HTTPException, Body
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Callable, Dict, List, Union
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from uuid import uuid4
from datetime import datetime

# make sure you have .env file saved locally with your API keys
from dotenv import load_dotenv

load_dotenv()

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import SKLearnVectorStore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.schema import AIMessage, HumanMessage, SystemMessage

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

import sys
import os
from pathlib import Path
# sys.path.append(str(Path(__file__).resolve().parent.parent))
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chains.main_graph.route_to_conversation_stage_chain import *
from chains.main_graph import *
from chains.questions_subgraph import *

from tools import *
from graph import *
from graph.shared_resources import shared_resources_list

from fastapi import FastAPI, Depends
from pydantic_settings import BaseSettings
from langchain.graphs.neo4j_graph import Neo4jGraph

import os, getpass
import pprint

def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = os.getenv(var)

# _set_env("TAVILY_API_KEY")
os.environ['TOKENIZERS_PARALLELISM'] = 'true'

_set_env("OPENAI_API_KEY")
_set_env("TAVILY_API_KEY")
# _set_env("LANGCHAIN_TRACING_V2")
# _set_env("LANGCHAIN_ENDPOINT")
# _set_env("LANGCHAIN_API_KEY") 
# _set_env("LANGCHAIN_PROJECT") 

# Settings class to handle environment variables
class Settings(BaseSettings):
    openai_api_key: str
    neo4j_url: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str

    class Config:
        env_file = ".env"  # Load environment variables from a .env file

# Dependency to provide settings
def get_settings():
    return Settings()

# Dependency to provide Neo4jGraph instance
def get_graph(settings: Settings = Depends(get_settings)):
    try:
        graph = Neo4jGraph(
            url=os.getenv('NEO4J_URI'),
            username=os.getenv('NEO4J_USERNAME'),
            password=os.getenv('NEO4J_PASSWORD')
        )
        return graph
    except Exception as e:
        print(settings.neo4j_url, settings.neo4j_username, settings.neo4j_password)
        raise HTTPException(status_code=500, detail=f"Error connecting to Neo4j: {str(e)}")

app = FastAPI()

print("Global resources initialized")
origins = ["*"]    
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    expose_headers=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class OutfitGenerationBody(BaseModel):
    key_session: str
    valid_seed_items: List[Dict]
    seed_item_start: int
    subset_items: List[Dict]

class ChatBody(BaseModel):
    new_message: str
    chat_history: list
    key_session: str
    user: dict
    stage: str
    missing_information: list
    outfit_request_context: str
    still_missing: list
    # answered: list
    # answers: list
    # model: str

# SESSION_ID = str(uuid4())

graph = build.create_graph()
# outfit_generation_graph = build.create_infinite_outfits_subgraph()
sample_body = {
    "new_message": "",
    "key_session": str(uuid4()),
    "user": 
    {
        'first_name': 'Jane',
        'last_name': 'Doe',
        "age": 27,
        "gender": "female",
    },
    "chat_history": [
      {
        "message": "Hello",
        "datetime": "2021-01-01 12:00:00",
        "sender": "user",
      },
      {
        "message": "Hi",
        "datetime": "2021-01-01 12:01:00",
        "sender": "bot",
        "outfits": []
      },
    ]
}

@app.post("/ai")
async def ai(body: ChatBody):
    if not body.new_message:
        raise HTTPException(status_code=400, detail="No chat provided.")

    # text = body.text
    ## Chat Session
    chat_history = body.chat_history
    key_session = body.key_session
    text = body.new_message
    user_profile = body.user
    # model = body.model
    model = "openai"

    ## States
    stage = body.stage if body.stage != "" else "1"  
    missing_information = body.missing_information # list = []
    outfit_request_context = body.outfit_request_context # str = ''
    still_missing = body.still_missing # list = []
    answered = [] #body.answered
    answers = [] #body.answers

    ## Outfit Generation
    seed_item_start = 0

    # Recover chat history :)
    messages = []
    for message_dict in chat_history:
        if message_dict["sender"] == "user":
            messages.append(
                HumanMessage(content=message_dict["message"]),
            )
        elif message_dict["sender"] == "bot":
            messages.append(
                SystemMessage(content=message_dict["message"]),
            )

    inputs = {
        "question": text,
        "documents": [],
        "user_profile": user_profile,
        "messages": [],
        "key_session": key_session,
        "model": model,
        # States
        "stage": stage,
        "missing_information": missing_information,
        "outfit_request_context": outfit_request_context,
        "still_missing": still_missing,
        # outfit generation
        "seed_item_start": seed_item_start,
        "answered": answered,
        "answers": answers,
    }

    config = {"configurable": {"thread_id": key_session}}
    for output in graph.stream(inputs, config):
        # print("output: ", output)
        for key, value in output.items():
            print(f"Finished running: {key}:")
    response = value["generation"]
    outfits = value.get("outfits", [])
    # states
    stage = value.get("stage", "")
    missing_information = value.get("missing_information", [])
    outfit_request_context = value.get("outfit_request_context", "")
    still_missing = value.get("still_missing", [])
    answered = value.get("answered", [])
    answers = value.get("answers", [])

    # outfit generation
    # past_seed_items = value.get("past_seed_items", [])
    subset_items = value.get("subset_items", [])
    valid_seed_items = value.get("valid_seed_items", [])
    # messages2 = value.get("messages", [])

    print("response: ", response)

    # # The dictionary `results` is returned, and FastAPI will automatically convert it into a JSON response.
    return {
        "text": response, 
        "outfits": outfits,
        # "messages2": messages2,
        # States
        "stage": stage,
        "missing_information": missing_information,
        "outfit_request_context": outfit_request_context,
        "still_missing": still_missing,
        # outfit generation
        # "past_seed_items": past_seed_items,
        "seed_item_start": 10,
        "subset_items": subset_items,
        "valid_seed_items": valid_seed_items,
        "answered": answered,
        "answers": answers,
    }

# @app.post("/ai")
# async def ai(body: ChatBody):
#     if not body.text:
#         raise HTTPException(status_code=400, detail="No chat provided.")

#     text = body.text
#     # chat_history = body.chat_history
#     # key_session = body.key_session
#     # text = body.new_message
#     # user_profile = body.["user"]
#     user_profile = sample_body["user"]
#     key_session = sample_body["key_session"]

#     inputs = {
#         "question": text,
#         "documents": [],
#         "user_profile": user_profile,
#     }

#     config = {"configurable": {"thread_id": key_session}}
#     for output in graph.stream(inputs, config):
#         # print("output: ", output)
#         for key, value in output.items():
#             print(f"Finished running: {key}:")
#     response = value["generation"]
#     outfits = value["outfits"]

#     # # The dictionary `results` is returned, and FastAPI will automatically convert it into a JSON response.
#     return {"text": response, "outfits": outfits}

# Human In the Loop
# @app.post("/ai")
# async def ai(body: ChatBody):
#     if not body.text:
#         raise HTTPException(status_code=400, detail="No chat provided.")
    
#     config = {"configurable": {"thread_id": "12"}}

#     text = body.text

#     snapshot = shared_resources_list["chat_graph"].get_state(config)
#     print("tools: ", snapshot.next)

#     if snapshot.next == ("websearch",):
#         if text.strip().lower() == "ok":
#             # User approved the web search, resume the graph
#             events = shared_resources_list["chat_graph"].stream(None, config)
#             for event in events:
#                 if "generation" in event:
#                     return {"text": event["generation"]}
#             return {"text": "Web search completed, but no results found."}
#         else:
#             # User has not approved
#             return {
#                 "text": "Web search is pending your approval. Please respond with 'OK' to continue."
#             }
#     else:
#         inputs = {
#             "question": text,
#             "documents": [],
#         }
#         for output in shared_resources_list["chat_graph"].stream(inputs, config):
#             # print("output: ", output)
#             for key, value in output.items():
#                 print(f"Finished running: {key}:")

#         if len(shared_resources_list["chat_graph"].get_state(config).next) == 0:
#             response = value["generation"]
#             # print("Assistant: ", response.content)
#         else:
#             response = "Searching..."
#             print("Searching...")
#         # user_input = input("User: ")
#         # if user_input is None or "a":
#         #     print("Confirmed")
#         #     # `None` will append nothing new to the current state, letting it resume as if it had never been interrupted
#         #     events = graph.stream(None, config, stream_mode="values")
#         #     for event in events:
#         #         if "messages" in event:
#         #             response = event["messages"][-1]
#         #     print("Assistant: ", response.content)
#         # else: 
#         #     # should be able to correct the output of the agent but will be implemented later
#         #     pass

    

#     # # The dictionary `results` is returned, and FastAPI will automatically convert it into a JSON response.
#     return {"text": response}

# @app.post("/generate")
# async def ai(body: ChatBody):
#     if not body.text:
#         raise HTTPException(status_code=400, detail="No chat provided.")

#     text = body.text

#     inputs = {
#         "question": text,
#         "documents": [],
#     }
#     config = {"configurable": {"thread_id": "12"}}
#     for output in shared_resources_list["chat_graph"].stream(inputs, config):
#         # print("output: ", output)
#         for key, value in output.items():
#             print(f"Finished running: {key}:")
#     response = value["generation"]

#     # # The dictionary `results` is returned, and FastAPI will automatically convert it into a JSON response.
#     return {"text": response}
