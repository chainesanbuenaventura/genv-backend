# # Required Imports
# from langchain_openai import ChatOpenAI
# from langchain.prompts import PromptTemplate, ChatPromptTemplate
# from langchain.tools import Tool
# from langchain_core.tools import tool
# from langchain.agents import create_react_agent, AgentExecutor
# from langchain.schema import HumanMessage
# from langchain.chains import RetrievalQAWithSourcesChain
# from langchain_community.vectorstores.neo4j_vector import Neo4jVector
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.tools.tavily_search import TavilySearchResults
# from pydantic import BaseModel, Field
# from typing import List, Dict, Union
# import asyncio
# import os
# import sys

# from .article_categorizer_chain import *

# # Add the project root directory to sys.path
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
# if project_root not in sys.path:
#     sys.path.append(project_root)

# from utils import *

# LAYERS = {
#     "base_layers": BASE_LAYERS, 
#     "one_piece_items": ONE_PIECE_ITEMS, 
#     "bottoms": BOTTOMS, 
#     "shoes": SHOES,
# }

# # Data model for next item selection
# class NextItemResult(BaseModel):
#     """Result for selecting the next best matching item."""
#     selected_item: dict = Field(description="Details of the selected item from the provided subset.")
#     explanation: str = Field(description="Explanation for why the item was selected.")

# class OutfitLayerSet:
#     def __init__(self, seed_item, outfit_request, subset, style_rules):
#         self.seed_item = seed_item
#         self.subset = subset
#         self.outfit_request = outfit_request
#         self.style_rules = style_rules

#         self.llm = ChatOpenAI(temperature=0)

#         # Instantiate the categorization chain
#         self.categorization_chain = get_categorization_chain(self.llm)

#         # Prompt Template
#         self.prompt_template = PromptTemplate(
#             template=(
#                 "You are an expert in fashion styling. Your task is to select the next best matching item for an outfit based on the provided input."
#                 "Choose the next item from the available items to add to the current selected items based on the outfit request, and use the style rules to guide your decision."
#                 "Ensure that the chosen item aligns with the overall outfit aesthetic and avoids duplications. Provide an explanation of why the chosen item was selected.\n\n"
#                 "Outfit Request: {outfit_request}\n"
#                 "Current Selected Items: {selected_items_compact}\n"
#                 "Style Rules: {style_rules}\n"
#                 "Available Items:\n{items_str}\n\n"
#                 "Rules:\n"
#                 "1. Select items that match the current selected items and that is relevant outfit request.\n"
#                 "2. Let the style rules guide you in choosing the best match to the current selected items.\n"
#                 "3. Prioritize fabric, color and style coordination.\n"
#                 "4. Follow the provided style rules if applicable.\n\n"
#                 "5. Select the next item that will make the whole look/outfit more complete or coherent\n\n"
#                 "Provide a short explanation (not more than 2 sentences) of the item choice and why it will complement the existing selected items and the outfit request context."
#             ),
#             input_variables=["outfit_request", "selected_items_compact", "style_rules", "items_str"]
#         )

#     async def generate_matching_layer_item(self, input_data: Union[str, Dict]) -> NextItemResult:
#         """
#         Build a complete, matching outfit using exact entries from the provided subset.
#         Handles both string and dictionary inputs for compatibility.
#         """
#         # Ensure input_data is a dictionary
#         if isinstance(input_data, str):
#             import json
#             input_data = json.loads(input_data)

#         # Extract inputs
#         selected_items_compact = input_data.get("selected_items_compact", "")
#         items_list = input_data.get("subset_left_to_choose_from", [])
#         outfit_request = input_data.get("outfit_request", "")
#         style_rules = input_data.get("style_rules", "")

#         # Format items list
#         items_str = "\n".join([f"{i+1}. {item['title']} by {item['brand']}" for i, item in enumerate(items_list)])

#         # Generate the prompt
#         formatted_prompt = self.prompt_template.format(
#             outfit_request=outfit_request,
#             selected_items_compact=selected_items_compact,
#             style_rules=style_rules,
#             items_str=items_str
#         )

#         # Call LLM
#         response = await self.llm.apredict([HumanMessage(content=formatted_prompt)])

#         # Parse response to identify selected items
#         selected_items = []
#         response_content = response.strip().lower()
#         for item in items_list:
#             if item['title'].lower() in response_content:
#                 selected_items.append(item)

#         return NextItemResult(
#             explanation=response.strip(),
#             selected_item=selected_items[0] if selected_items != [] else {}
#         )

#     async def get_next_layer(self, selected_items_compact, subset_left_to_choose_from):
#         # Input preparation
#         get_next_item_input = {
#             "selected_items_compact": selected_items_compact,
#             "outfit_request": self.outfit_request,
#             "style_rules": self.style_rules,
#             "subset_left_to_choose_from": subset_left_to_choose_from,
#         }

#         next_item_output = await self.generate_matching_layer_item(get_next_item_input)

#         return next_item_output.selected_item

#     async def generate_all_layer_items(self):
#         self.selected_items = [self.seed_item]
#         print("self.seed_item: ", self.seed_item)
#         print(self.seed_item["subsubcategory"])
#         self.seed_item_layer = await self.categorization_chain.apredict({
#             "item_description": self.seed_item["subsubcategory"],
#         })

#         layers_done = {self.seed_item_layer.category}

#         while len(layers_done) <= len(LAYERS):

#             if "one_piece_items" in layers_done and "bottoms" not in layers_done:
#                 layers_done.add("bottoms")
#             if "base_layers" in layers_done and "one_piece_items" not in layers_done:
#                 layers_done.add("one_piece_items")

#             print("Layers Done: ", ", ".join(layers_done))
#             # Filter all layers that are left to be added
#             possible_layers_left = [item for item in list(LAYERS.keys()) if item not in list(layers_done)]
#             print("\tPossible Layers to Choose From: ", possible_layers_left)

#             # Current selected items
#             selected_items_compact = simplify_dicts(self.selected_items)
#             subsubcategories_left_to_choose_from = [item for sublist in [LAYERS[layer] for layer in possible_layers_left] for item in sublist]
#             print("\tSubsubcategories to choose from: ", ", ".join(subsubcategories_left_to_choose_from))

#             subset_left_to_choose_from = list(filter(
#                 lambda item: item.get('subsubcategory') in subsubcategories_left_to_choose_from,
#                 self.subset,
#             ))

#             # Generate the next layer
#             next_item = await self.get_next_layer(selected_items_compact, subset_left_to_choose_from)
#             if next_item != {}:
#                 self.selected_items.append(next_item)
#                 next_layer_added = (await self.categorization_chain.apredict(
#                     {
#                         "item_description": next_item["subsubcategory"],
#                     }
#                 )).category
#                 print(f"\tAdded '{next_layer_added}' layer: ", simplify_dicts([next_item])[0]["subsubcategory"], " -- ", simplify_dicts([next_item])[0]["title"])
#                 layers_done.add(
#                     next_layer_added
#                 )
#             else:
#                 return self.selected_items

#         return self.selected_items

# Required Imports
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.tools import Tool
from langchain_core.tools import tool
from langchain.agents import create_react_agent, AgentExecutor
from langchain.schema import HumanMessage
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_community.vectorstores.neo4j_vector import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from pydantic import BaseModel, Field
from typing import List, Dict, Union

import os
import sys

from .article_categorizer_chain import *

# Add the project root directory to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils import *

LAYERS = {
    "base_layers": BASE_LAYERS, 
    "one_piece_items": ONE_PIECE_ITEMS, 
    "bottoms": BOTTOMS, 
    "shoes": SHOES,
}

ADDITIONAL_LAYERS = {
    "base_layers_for_layering": BASE_LAYERS, # one time
    "jackets_and_other_outerwear": JACKETS_AND_OTHER_OUTERWEAR, # one
    "coats": COATS, # one
}
OPTIONAL_LAYERS = {
    "additional_items": ADDITIONAL_ITEMS, # list ponchos
    "accessories": ACCESSORIES, #list
    "jewelry": JEWELRY, # list
    "bags": BAGS, # bags
}

ALL_ADDITIONAL_LAYERS = {
    "base_layers_for_layering": BASE_LAYERS,
    "jackets_and_other_outerwear": JACKETS_AND_OTHER_OUTERWEAR,
    "coats": COATS,
    "additional_items": ADDITIONAL_ITEMS, 
    "accessories": ACCESSORIES, 
    "jewelry": JEWELRY,
    "bags": BAGS,
}

# Data model for next item selection
class NextItemResult(BaseModel):
    """Result for selecting the next best matching item."""
    selected_item: dict = Field(description="Details of the selected item from the provided subset.")
    # explanation: str = Field(description="One phrase explanation for why the item was selected.")

class OutfitLayerSet:
    def __init__(self, seed_item, outfit_request, subset, style_rules):
        self.seed_item = seed_item
        self.subset = subset
        self.outfit_request = outfit_request
        self.style_rules = style_rules
        
        self.llm = ChatOpenAI(temperature=0)

        # Instantiate the categorization chain
        # self.categorization_chain = get_categorization_chain(self.llm)
        
        # Prompt Template
        self.prompt_template = PromptTemplate(
            template=(
                "You are an expert in fashion styling. Your task is to select the next best matching item for an outfit based on the provided input."
                "Choose the next item from the available items to add to the current selected items based on the outfit request, and use the style rules to guide your decision."
                "Ensure that the chosen item aligns with the overall outfit aesthetic and avoids duplications. Provide an explanation of why the chosen item was selected.\n\n"
                "Outfit Request: {outfit_request}\n"
                "Current Selected Items: {selected_items_compact}\n"
                "Style Rules: {style_rules}\n"
                "Available Items:\n{items_str}\n\n"
                "Rules:\n"
                "1. Select items that match the current selected items and that is relevant outfit request.\n"
                "2. Let the style rules guide you in choosing the best match to the current selected items.\n"
                "3. Prioritize fabric, color and style coordination.\n"
                "4. Follow the provided style rules if applicable.\n\n"
                "5. Select the next item that will make hthe whole look/outfit more complete or coherent\n\n"
                "Provide a one sentence explanation of the item choice and why it will complement the existing selected items and the outftit request context."
            ),
            input_variables=["outfit_request", "selected_items_compact", "style_rules", "items_str"]
        )
    
    def generate_matching_layer_item(self, input_data: Union[str, Dict]) -> NextItemResult:
        """
        Build a complete, matching outfit using exact entries from the provided subset.
        Handles both string and dictionary inputs for compatibility.
        """
        # Ensure input_data is a dictionary
        if isinstance(input_data, str):
            import json
            input_data = json.loads(input_data)

        # Extract inputs
        selected_items_compact = input_data.get("selected_items_compact", "")
        items_list = input_data.get("subset_left_to_choose_from", []) #
        outfit_request = input_data.get("outfit_request", "")
        style_rules = input_data.get("style_rules", "")

        # Format items list
        # print("\t", [item["subsubcategory"] for item in items_list])
        items_str = "\n".join([f"{i+1}. {item['title']} by {item['brand']}" for i, item in enumerate(items_list)])

        # Generate the prompt
        formatted_prompt = self.prompt_template.format(
            outfit_request=outfit_request,
            selected_items_compact=selected_items_compact,
            style_rules=style_rules,
            items_str=items_str
        )

        # Call LLM
#         llm = ChatOpenAI(temperature=0)
        response = self.llm.invoke([HumanMessage(content=formatted_prompt)])

        # Parse response to identify selected items
        selected_items = []
        response_content = response.content.strip().lower()
        for item in items_list:
            if item['title'].lower() in response_content:
                selected_items.append(item)

        return NextItemResult(
            explanation=response.content.strip(),
            selected_item=selected_items[0] if selected_items != [] else {}
        )

    def get_next_layer(self, selected_items_compact, subset_left_to_choose_from):
        # Input preparation
        get_next_item_input = {
            "selected_items_compact": selected_items_compact,
            "outfit_request": self.outfit_request,
            "style_rules": self.style_rules,
            "subset_left_to_choose_from": subset_left_to_choose_from,
        }

        next_item_output = self.generate_matching_layer_item(get_next_item_input)

        return next_item_output.selected_item
    
    # from one seed item
    def generate_all_layer_items(self):
        self.selected_items = [self.seed_item]
        # print("seed item:", self.seed_item["subsubcategory"])
        # self.seed_item_layer = self.categorization_chain.invoke({
        #     "item_description": self.seed_item["subsubcategory"],
        #     "title": self.seed_item["title"],
        # })
        self.seed_item_layer = categorize_layer(self.seed_item)

        layers_done = {self.seed_item_layer.category}

        while len(layers_done) <= len(LAYERS):    
            if "one_piece_items" in layers_done and "bottoms" not in layers_done:
                layers_done.add("bottoms")
                layers_done.add("base_layers")
            if "base_layers" in layers_done and "one_piece_items" not in layers_done:
                layers_done.add("one_piece_items")
            if "bottoms" in layers_done and "one_piece_items" not in layers_done:
                layers_done.add("one_piece_items")

            # print("\tLayers Done: ", ", ".join(layers_done))
            # Filter all layers that are left to be added
            possible_layers_left = [item for item in list(LAYERS.keys()) if item not in list(layers_done)]
            # print("\tPossible Layers to Choose From: ", possible_layers_left)

            # Current selected items
            selected_items_compact = simplify_dicts(self.selected_items)
            subsubcategories_left_to_choose_from = [item for sublist in [LAYERS[layer] for layer in possible_layers_left] for item in sublist]
            # print("\tSubsubcategories to choose from: ", ", ".join(subsubcategories_left_to_choose_from))

            subset_left_to_choose_from = list(filter(
                lambda item: item.get('subsubcategory') in subsubcategories_left_to_choose_from,
                self.subset,
            ))
            # print("\tSubset: ", [item["subsubcategory"] for item in self.subset])
            # print("\tSubset left to choose from: ", [item["subsubcategory"] for item in subset_left_to_choose_from])

            # Generate the next layer
            # next_item = self.get_next_layer(selected_items_compact, subset_left_to_choose_from)
            next_item_output = self.generate_matching_layer_item(
                {
                    "selected_items_compact": selected_items_compact,
                    "outfit_request": self.outfit_request,
                    "style_rules": self.style_rules,
                    "subset_left_to_choose_from": subset_left_to_choose_from,
                }
            )

            next_item = next_item_output.selected_item

            # print("\tNext Item Selected: ", next_item)
            if next_item != {}:
                # print("next_item: ", next_item)
                # print("subsubcategory: ", next_item["subsubcategory"])
                self.selected_items.append(next_item)
                # next_layer_added = self.categorization_chain.invoke(
                #     {
                #         "item_description": next_item["subsubcategory"],
                #         "title": next_item["title"],
                #     }
                # ).category
                next_layer_added = categorize_layer(next_item)
                # print(f"\tAdded '{next_layer_added}' layer: ", simplify_dicts([next_item])[0]["subsubcategory"], " -- ", simplify_dicts([next_item])[0]["title"])
                layers_done.add(
                    next_layer_added
                )
                # print("Seed: ", self.seed_item["subsubcategory"], " - ", self.seed_item["title"])
                # print("Selected Items: ", ", ".join([item["subsubcategory"] + " - " + item["title"] for item in self.selected_items]))
                # print( "Added: ", next_layer_added, " - ",  next_item["title"])
            else:
                return self.selected_items
            
        return self.selected_items

# # Optimized
# # Data model for next item selection
# class NextItemResult(BaseModel):
#     """Result for selecting the next best matching item."""
#     selected_item: dict = Field(description="Details of the selected item from the provided subset.")
#     # explanation: str = Field(description="One phrase explanation for why the item was selected.")

# class OutfitLayerSet:
#     def __init__(self, seed_item, outfit_request, subset, style_rules):
#         self.seed_item = seed_item
#         self.subset = subset
#         self.outfit_request = outfit_request
#         self.style_rules = style_rules
        
#         self.llm = ChatOpenAI(temperature=0)

#         # Instantiate the categorization chain
#         self.categorization_chain = get_categorization_chain(self.llm)
        
#         # # Prompt Template
#         # self.prompt_template = PromptTemplate(
#         #     template=(
#         #         "You are an expert in fashion styling. Your task is to select the next best matching item for an outfit based on the provided input."
#         #         "Choose the next item from the available items to add to the current selected items based on the outfit request, and use the style rules to guide your decision."
#         #         "Ensure that the chosen item aligns with the overall outfit aesthetic and avoids duplications. Provide an explanation of why the chosen item was selected.\n\n"
#         #         "Outfit Request: {outfit_request}\n"
#         #         "Current Selected Items: {selected_items_compact}\n"
#         #         "Style Rules: {style_rules}\n"
#         #         "Available Items:\n{items_str}\n\n"
#         #         "Rules:\n"
#         #         "1. Select items that match the current selected items and that is relevant outfit request.\n"
#         #         "2. Let the style rules guide you in choosing the best match to the current selected items.\n"
#         #         "3. Prioritize fabric, color and style coordination.\n"
#         #         "4. Follow the provided style rules if applicable.\n\n"
#         #         "5. Select the next item that will make hthe whole look/outfit more complete or coherent\n\n"
#         #     ),
#         #     input_variables=["outfit_request", "selected_items_compact", "style_rules", "items_str"]
#         # )
#         self.generate_layer_item_instructions = """
#             You are an expert in fashion styling. Your task is to select the next best matching item for an outfit based on the provided input.
#             Choose the next item from the available items to add to the current selected items based on the outfit request, and use the style rules to guide your decision.
#             Ensure that the chosen item aligns with the overall outfit aesthetic and avoids duplications. Provide an explanation of why the chosen item was selected.\n\n
#             Outfit Request: {outfit_request}\n
#             Current Selected Items: {selected_items_compact}\n
#             Style Rules: {style_rules}\n
#             Available Items:\n{items_str}\n\n
#             Rules:\n
#             1. Select items that match the current selected items and that is relevant outfit request.\n
#             2. Let the style rules guide you in choosing the best match to the current selected items.\n
#             3. Prioritize fabric, color and style coordination.\n
#             4. Follow the provided style rules if applicable.\n\n
#             5. Select the next item that will make hthe whole look/outfit more complete or coherent\n\n
#         """

#         # Define the structured LLM output
#         self.structured_matching_layer_item = self.get_structured_matching_layer_item()

#         # Define the prompt template
#         self.prompt = ChatPromptTemplate.from_messages(
#             [
#                 ("system", self.generate_layer_item_instructions),
#             ]
#         )

#         # Combine the prompt with structured output
#         self.structured_matching_layer_item_chain = self.prompt | self.structured_matching_layer_item

#     # LLM Structure for Follow-Up Questions
#     def get_structured_matching_layer_item(self):
#         """
#         Set up LLM with structured output for Follow-Up Questions.
#         """
#         return self.llm.with_structured_output(schema=NextItemResult)

#     def generate_matching_layer_item(
#             self,
#             selected_items_compact,
#             outfit_request,
#             style_rules,
#             subset_left_to_choose_from,
#     ):
#         """
#         Build a complete, matching outfit using exact entries from the provided subset.
#         Handles both string and dictionary inputs for compatibility.
#         """
#         # # Format items list
#         # # print("\t", [item["subsubcategory"] for item in items_list])
#         items_str = "\n".join([f"{i+1}. {item['title']} by {item['brand']}" for i, item in enumerate(subset_left_to_choose_from)])

#         result = self.structured_matching_layer_item_chain.invoke(
#             {
#                 "outfit_request": outfit_request, 
#                 "selected_items_compact": selected_items_compact, 
#                 "style_rules": style_rules, 
#                 "items_str": items_str,
#             }
#         )

#         return result.selected_item
    
#     # from one seed item
#     def generate_all_layer_items(self):
#         self.selected_items = [self.seed_item]
#         # print("seed item:", self.seed_item["subsubcategory"])
#         self.seed_item_layer = self.categorization_chain.invoke({
#             "item_description": self.seed_item["subsubcategory"],
#             "title": self.seed_item["title"],
#         })

#         layers_done = {self.seed_item_layer.category}

#         while len(layers_done) < len(LAYERS):    
#             if "one_piece_items" in layers_done and "bottoms" not in layers_done:
#                 layers_done.add("bottoms")
#                 layers_done.add("base_layers")
#             if "base_layers" in layers_done and "one_piece_items" not in layers_done:
#                 layers_done.add("one_piece_items")
#             if "bottoms" in layers_done and "one_piece_items" not in layers_done:
#                 layers_done.add("one_piece_items")

#             # print("\tLayers Done: ", ", ".join(layers_done))
#             # Filter all layers that are left to be added
#             possible_layers_left = [item for item in list(LAYERS.keys()) if item not in list(layers_done)]
#             # print("\tPossible Layers to Choose From: ", possible_layers_left)

#             # Current selected items
#             selected_items_compact = simplify_dicts(self.selected_items)
#             subsubcategories_left_to_choose_from = [item for sublist in [LAYERS[layer] for layer in possible_layers_left] for item in sublist]
#             # print("\tSubsubcategories to choose from: ", ", ".join(subsubcategories_left_to_choose_from))

#             subset_left_to_choose_from = list(filter(
#                 lambda item: item.get('subsubcategory') in subsubcategories_left_to_choose_from,
#                 self.subset,
#             ))
#             # print("\tSubset: ", [item["subsubcategory"] for item in self.subset])
#             # print("\tSubset left to choose from: ", [item["subsubcategory"] for item in subset_left_to_choose_from])

#             # Generate the next layer
#             # next_item = self.get_next_layer(selected_items_compact, subset_left_to_choose_from)
#             next_item_output = self.generate_matching_layer_item(
#                 selected_items_compact=selected_items_compact,
#                 outfit_request=self.outfit_request,
#                 style_rules=self.style_rules,
#                 subset_left_to_choose_from=subset_left_to_choose_from,
#             )

#             next_item = next_item_output.selected_item

#             # print("\tNext Item Selected: ", next_item)
#             if next_item != {}:
#                 # print("next_item: ", next_item)
#                 # print("subsubcategory: ", next_item["subsubcategory"])
#                 self.selected_items.append(next_item)
#                 next_layer_added = self.categorization_chain.invoke(
#                     {
#                         "item_description": next_item["subsubcategory"],
#                         "title": next_item["title"],
#                     }
#                 ).category
#                 # print(f"\tAdded '{next_layer_added}' layer: ", simplify_dicts([next_item])[0]["subsubcategory"], " -- ", simplify_dicts([next_item])[0]["title"])
#                 layers_done.add(
#                     next_layer_added
#                 )
#                 # print("Seed: ", self.seed_item["subsubcategory"], " - ", self.seed_item["title"])
#                 # print("Selected Items: ", ", ".join([item["subsubcategory"] + " - " + item["title"] for item in self.selected_items]))
#                 # print( "Added: ", next_layer_added, " - ",  next_item["title"])
#             else:
#                 return self.selected_items
            
#         return self.selected_items