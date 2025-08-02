from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from itertools import chain

from utils import * 
from .generate_layer_items_chain import *

# Pydantic Model for Layered Output
class LayeredOutfitOutput(BaseModel):
    base_layers_for_layering: Optional[List[Dict]] = Field([], description="Selected base layer items.")
    jackets_and_other_outerwear: Optional[List[Dict]] = Field([], description="Selected jacket or outerwear items.")
    coats: Optional[List[Dict]] = Field([], description="Selected coat items.")
    additional_items: Optional[List[Dict]] = Field([], description="List of additional items.")
    accessories: Optional[List[Dict]] = Field([], description="List of accessories.")
    jewelry: Optional[List[Dict]] = Field([], description="List of jewelry items.")
    bags: Optional[List[Dict]] = Field([], description="Selected bag item.")

class OutfitExtraLayerSet:
    def __init__(self, base_outfit, outfit_request, subset, style_rules):
        self.base_outfit = simplify_dicts(base_outfit)
        self.subset = subset
        self.outfit_request = outfit_request
        self.style_rules = style_rules

        self.llm = ChatOpenAI(temperature=0)
        self.selected_items = {}
        
        self.base_layers_for_layering_to_choose_from = [item for sublist in [ALL_ADDITIONAL_LAYERS[layer] for layer in ["base_layers_for_layering"]] for item in sublist]
        self.base_layers_for_layering_subset_left_to_choose_from = simplify_dicts(
            list(
                filter(
                    lambda item: item.get('subsubcategory') in self.base_layers_for_layering_to_choose_from,
                    subset,
                )
            ),
            ["title", "brand"],
        )
#         self.base_layers_for_layering_subset_left_to_choose_from = "\n".join([f"{i+1}. {item['title']} by {item['brand']}" for i, item in enumerate(self.base_layers_for_layering_subset_left_to_choose_from)])
        
        self.jackets_and_other_outerwear_to_choose_from = [item for sublist in [ALL_ADDITIONAL_LAYERS[layer] for layer in ["jackets_and_other_outerwear"]] for item in sublist]
        self.jackets_and_other_outerwear_subset_left_to_choose_from = simplify_dicts(
            list(
                filter(
                    lambda item: item.get('subsubcategory') in self.jackets_and_other_outerwear_to_choose_from,
                    subset,
                )
            ),
            ["title", "brand"],
        )
#         self.jackets_and_other_outerwear_subset_left_to_choose_from = "\n".join([f"{i+1}. {item['title']} by {item['brand']}" for i, item in enumerate(self.jackets_and_other_outerwear_subset_left_to_choose_from)])
        
        self.coats_to_choose_from = [item for sublist in [ALL_ADDITIONAL_LAYERS[layer] for layer in ["coats"]] for item in sublist]
        self.coats_subset_left_to_choose_from = simplify_dicts(
                list(filter(
                    lambda item: item.get('subsubcategory') in self.coats_to_choose_from,
                    subset,
                )
            ),
            ["title", "brand"],
        )
#         self.coats_subset_left_to_choose_from = "\n".join([f"{i+1}. {item['title']} by {item['brand']}" for i, item in enumerate(self.coats_subset_left_to_choose_from)])
        
        self.additional_items_to_choose_from = [item for sublist in [ALL_ADDITIONAL_LAYERS[layer] for layer in ["additional_items"]] for item in sublist]
        base_layer_subcategories = list({item["subcategory"] for item in self.base_outfit if "subcategory" in item})
        dont_need_tights = ["Pants", "Jeans", "Suits", "Beachwear & Swimwear", "Activewear"]
        if bool(set(base_layer_subcategories) & set(dont_need_tights)):
            self.additional_items_to_choose_from = list(set(self.additional_items_to_choose_from) - set(["Tights and Pantyhose", "Stockings"]))
        self.additional_items_subset_left_to_choose_from = simplify_dicts(
            list(
                filter(
                    lambda item: item.get('subsubcategory') in self.additional_items_to_choose_from,
                    subset,
                )
            ),
            ["title", "brand"],
        )
#         self.additional_items_subset_left_to_choose_from = "\n".join([f"{i+1}. {item['title']} by {item['brand']}" for i, item in enumerate(self.additional_items_subset_left_to_choose_from)])
        
        self.accessories_to_choose_from = [item for sublist in [ALL_ADDITIONAL_LAYERS[layer] for layer in ["accessories"]] for item in sublist]
        self.accessories_subset_left_to_choose_from = simplify_dicts(
            list(
                filter(
                    lambda item: item.get('subsubcategory') in self.accessories_to_choose_from,
                    subset,
                )
            ),
            ["title", "brand"],
        )
#         self.accessories_subset_left_to_choose_from = "\n".join([f"{i+1}. {item['title']} by {item['brand']}" for i, item in enumerate(self.accessories_subset_left_to_choose_from)])
        
        self.jewelries_to_choose_from = [item for sublist in [ALL_ADDITIONAL_LAYERS[layer] for layer in ["jewelry"]] for item in sublist]
        self.jewelries_subset_left_to_choose_from = simplify_dicts(
            list(
                filter(
                    lambda item: item.get('subsubcategory') in self.jewelries_to_choose_from,
                    subset,
                )
            ),
            ["title", "brand"],
        )
#         self.jewelries_subset_left_to_choose_from = "\n".join([f"{i+1}. {item['title']} by {item['brand']}" for i, item in enumerate(self.jewelries_subset_left_to_choose_from)])
        
        self.bags_to_choose_from = [item for sublist in [ALL_ADDITIONAL_LAYERS[layer] for layer in ["bags"]] for item in sublist]
        self.bags_subset_left_to_choose_from = simplify_dicts(
            list(
                filter(
                    lambda item: item.get('subsubcategory') in self.bags_to_choose_from,
                    subset,
                )
            ),
            ["title", "brand"],
        )
#         self.bags_subset_left_to_choose_from = "\n".join([f"{i+1}. {item['title']} by {item['brand']}" for i, item in enumerate(self.bags_subset_left_to_choose_from)])

        self.prompt_template = PromptTemplate(
            template=(
                """You are a professional fashion stylist tasked with selecting items for the following layers.\n\n
                Outfit Request: {outfit_request}\n
                Base Outfit: {base_outfit_str}\n
                Style Rules: {style_rules}\n
                Rules:\n
                1. Understand if the base outfits needs another "top" item for layering. If yes, choose exclusively from this list: [{base_layers_for_layering_subset_left_to_choose_from}]. Leave blank if not necessary for the outfit request.
                2. Understand if the base outfits needs a jacket for layering. If yes, choose exclusively from this list: [{jackets_and_other_outerwear_subset_left_to_choose_from}]. Leave blank if not necessary for the outfit request.
                3. Understand if the base outfits needs a coat for layering. If yes, choose exclusively from this list: [{coats_subset_left_to_choose_from}]. Leave blank if not necessary for the outfit request.
                4. Select a list of additional items. Leave blank if not necessary for the outfit request. Choose exclusively from this list: [{additional_items_subset_left_to_choose_from}]. Leave blank if not necessary for the outfit request.
                5. Select a list of accessories.  Leave blank if not necessary for the outfit request. Choose exclusively from this list: [{accessories_subset_left_to_choose_from}]. Leave blank if not necessary for the outfit request.
                6. Select a list of jewelries.  Leave blank if not necessary for the outfit request. Choose exclusively from this list: [{jewelries_subset_left_to_choose_from}]. Leave blank if not necessary for the outfit request.
                7. Understand if the base outfits needs a bag for layering. If yes, choose exclusively from this list: [{bags_subset_left_to_choose_from}]. Leave blank if not necessary for the outfit request.
                8. Ensure selections align with the outfit request and style rules.\n
                9. Coordinate colors, materials, and styles across the outfit.\n\n
                10. Make sure the entire selection above are coherent with each other and the base outfit and that it makes sense (e.g. no conflicting items)
                Provide your response as JSON in the following format:\n

                    "base_layers_for_layering": [],
                    "jackets_and_other_outerwear": [],
                    "coats": [],
                    "additional_items": [],
                    "accessories": [],
                    "jewelries": [],
                    "bags": []

                """
            ),
            input_variables=[
                "base_layers_for_layering_subset_left_to_choose_from", 
                "jackets_and_other_outerwear_subset_left_to_choose_from", 
                "coats_subset_left_to_choose_from", 
                "additional_items_subset_left_to_choose_from", 
                "accessories_subset_left_to_choose_from", 
                "jewelries_subset_left_to_choose_from", 
                "bags_subset_left_to_choose_from", 
                "outfit_request", 
                "base_outfit_str", 
                "style_rules", 
            ]
        )

    def generate_matching_extra_layers(self, subset_left_to_choose_from):
        # Format items list
        base_outfit_str = "\n".join([f"{i+1}. {item['title']} by {item['brand']}" for i, item in enumerate(self.base_outfit)])
        items_str = "\n".join([f"{i+1}. {item['title']} by {item['brand']}" for i, item in enumerate(subset_left_to_choose_from)])

        # Generate the prompt
        formatted_prompt = self.prompt_template.format(
            base_layers_for_layering_subset_left_to_choose_from=self.base_layers_for_layering_subset_left_to_choose_from, 
            jackets_and_other_outerwear_subset_left_to_choose_from=self.jackets_and_other_outerwear_subset_left_to_choose_from, 
            coats_subset_left_to_choose_from=self.coats_subset_left_to_choose_from, 
            additional_items_subset_left_to_choose_from=self.additional_items_subset_left_to_choose_from, 
            accessories_subset_left_to_choose_from=self.accessories_subset_left_to_choose_from, 
            jewelries_subset_left_to_choose_from=self.jewelries_subset_left_to_choose_from, 
            bags_subset_left_to_choose_from=self.bags_subset_left_to_choose_from, 
            outfit_request=self.outfit_request,
            base_outfit_str=base_outfit_str,
            style_rules=self.style_rules,
#             subset_left_to_choose_from=items_str,
        )

        response = self.llm.invoke([HumanMessage(content=formatted_prompt)])

        # Parse response into structured output
        response_json = response.content.strip()
        try:
            parsed_output = LayeredOutfitOutput.parse_raw(response_json)
        except Exception as e:
            raise ValueError(f"Error parsing response: {e}\nResponse: {response_json}")

        return parsed_output

    def generate_all_extra_layer_items(self):
        # Filter items by categories
        # subsubcategories_left_to_choose_from = list(chain.from_iterable(EXTRA_LAYERS[layer] for layer in EXTRA_LAYERS))
        # subset_left_to_choose_from = list(filter(
        #     lambda item: item.get('subsubcategory') in subsubcategories_left_to_choose_from,
        #     self.subset,
        # ))

        # Generate the extra layers
        return self.generate_matching_extra_layers(self.subset)