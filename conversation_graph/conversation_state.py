import operator
from typing_extensions import TypedDict
from typing import List, Annotated, Any, Dict
from langgraph.graph.message import add_messages

class ConversationState(TypedDict):
    """
    Graph state is a dictionary that contains information we want to propagate to, and modify in, each graph node.
    """
    messages: Annotated[list, add_messages]
    question : str # User question
    generation : str # LLM generation
    stage: int # 1. Intro and outfit context
    
    # Outfit Generation
    ongoing_request: str
    request_history: Annotated[list, add_messages]
    missing_information: List[str]
    request_type: str
    active_request: str
    active_request_status: str

