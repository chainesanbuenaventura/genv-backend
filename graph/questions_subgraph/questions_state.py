import operator
from typing_extensions import TypedDict
from typing import List, Annotated, Any, Dict
from langgraph.graph.message import add_messages

class UserProfile(TypedDict):
    first_name: str
    last_name: str
    age: int
    gender: str

class Outfit(TypedDict):
    articles: List[str]
    generated_by: str
    
class QuestionsState(TypedDict):
    """
    Graph state is a dictionary that contains information we want to propagate to, and modify in, each graph node.
    """
    user_profile: UserProfile
    
    first_name: str
    last_name: str
    age: int
    gender: str
    
    model: str
    messages: Annotated[list, add_messages]
    question : str # User question
    generation : str # LLM generation
    stage: int # 1. Intro and outfit context
    
    # Outfit Generation
    # request_history: Annotated[list, add_messages]
    # active_request: str
    # active_request_status: str
    # outfit_context: str

    missing_information: List[str]
    outfit_request_context: str
    still_missing: List[str]
    answered: List[str]
    answers: List[str]

    outfits: List[Outfit]
