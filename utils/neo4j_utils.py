
from fastapi import FastAPI, Depends
from pydantic_settings import BaseSettings
from langchain.graphs.neo4j_graph import Neo4jGraph
from fastapi import FastAPI, HTTPException, Body
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain_openai import OpenAIEmbeddings

import os

def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = os.getenv(var)

_set_env("NEO4J_URI")
_set_env("NEO4J_USERNAME")
_set_env("NEO4J_PASSWORD")
_set_env("VECTOR_INDEX_NAME")
_set_env("VECTOR_SOURCE_PROPERTY") 
_set_env("VECTOR_EMBEDDING_PROPERTY") 
_set_env("VECTOR_NODE_LABEL")

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

def get_neo4j_vector_store():
    neo4j_vector_store = Neo4jVector.from_existing_graph(
        embedding=OpenAIEmbeddings(),
        url=os.getenv('NEO4J_URI'),
        username=os.getenv('NEO4J_USERNAME'),
        password=os.getenv('PASSWORD'),
        index_name=os.getenv('VECTOR_INDEX_NAME'),
        node_label=os.getenv('VECTOR_NODE_LABEL'),
        text_node_properties=[os.getenv('VECTOR_SOURCE_PROPERTY')],
        embedding_node_property=os.getenv('VECTOR_EMBEDDING_PROPERTY'),
    )

    return neo4j_vector_store

# Dependency to provide Neo4jGraph instance
def get_neo4j_graph(settings: Settings = Depends(get_settings)):
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
