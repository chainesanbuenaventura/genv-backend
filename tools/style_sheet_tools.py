from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import SKLearnVectorStore
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader

from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

import numpy as np
import openai
from langchain_core.tools import tool

# Data model
class Generation(BaseModel):
    """Generation and binary score to say whether a complete outfit suggestion is asked by a user."""

    generation: str = Field(description="The conversational response to the user's request or feedback, formatted as a friendly, natural message.")
    scenario: int = Field(description="Indicates which scenario (1-6) the conversation corresponds to, based on the nature of the user's request or feedback.")
    
def get_structured_rag(llm):
    return llm.with_structured_output(schema=Generation)

# Prompt
prompt = hub.pull("rlm/rag-prompt")
# prompt.messages[0].prompt.template

# Initialize the resources once
# llm = ChatOpenAI()
loader = PyPDFLoader('../pdfs/ESTYL _ STYLE GUIDE (pdf).pdf')
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(docs)
vectorstore = InMemoryVectorStore.from_documents(documents=splits, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

# Post-processing
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

@tool
def styles_lookup(query: str) -> str:
    """Consult the company policies to check whether certain options are permitted.
    Use this before making any flight changes performing other 'write' events."""
    docs = retriever.query(query, k=2)
    retriever.invoke()
    return "\n\n".join([doc["page_content"] for doc in docs])
