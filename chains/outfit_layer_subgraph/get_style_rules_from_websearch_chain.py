# import os
# from langchain_community.tools.tavily_search import TavilySearchResults

# def _set_env(var: str):
#     if not os.environ.get(var):
#         os.environ[var] = os.getenv(var)
        
# from tools import * 

# def get_style_rules_from_web_search(llm, style_rules_query, outfit_request, seed_item_str):
#     primary_assistant_prompt = ChatPromptTemplate.from_messages(
#         [
#             (
#                 style_rules_query
#             ),
#         ]
#     )

#     tools = [
#         TavilySearchResults(max_results=3),
#     ]
#     part_1_assistant_runnable = primary_assistant_prompt | llm.bind_tools(tools)
    
#     result = part_1_assistant_runnable.invoke({
#         "outfit_request": outfit_request, 
#         "seed_item_str": seed_item_str,
#     })
    
#     return result.content