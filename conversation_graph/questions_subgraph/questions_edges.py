# from langchain.schema import Document
# from typing import Literal
# from pydantic import BaseModel, Field
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.messages import HumanMessage, SystemMessage
# from langgraph.graph import END
# from chains.main_graph import *
# from tools import *
# from graph import *

# from langchain_openai import ChatOpenAI 
# from graph.shared_resources import shared_resources_list
# from graph.state import *

# ### Edges

# def route_scenario(state: GraphState):
#     """
#     Route question to web search or RAG 

#     Args:
#         state (dict): The current graph state

#     Returns:
#         str: Next node to call
#     """
#     question = state["question"]
#     messages = state["messages"]
#     print(state["question"])
#     print("---ROUTE QUESTION---")
#     scenario = shared_resources_list["scenario_router_chain"].invoke(
#         {
#             "question": question, 
#             "messages": messages
#         }
#     )
#     if scenario.scenario_number == 1:
#         print("---ROUTE CONVERSATION TO OUTFIT REQUEST---")
#         return "outfit request"
#     elif scenario.scenario_number in [2, 3]:
#         print("---ROUTE CONVERSATION TO GENERATE---")
#         return "generate"
#     elif scenario.scenario_number == 4:
#         print("---ROUTE QUESTION TO SOURCES---")
#         source = shared_resources_list["sources_router_chain"].invoke(
#             {
#                 "question": question, 
#                 "messages": messages
#             }
#         ) 
#         if source.datasource == 'websearch':
#             print("---ROUTE QUESTION TO WEB SEARCH---")
#             return "websearch"
#         elif source.datasource == 'vectorstore':
#             print("---ROUTE QUESTION TO VECTORSTORE---")
#         return "vectorstore"
#     elif scenario.scenario_number == 5:
#         return "fallback"

