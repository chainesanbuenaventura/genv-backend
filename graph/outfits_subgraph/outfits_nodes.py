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
import asyncio

from fastapi import Request

from chains.outfits_subgraph import *
from tools import *
from graph.outfits_subgraph import *
from graph.outfits_subgraph.outfits_state import *
# from graph.outfit_layer_subgraph import *
# from graph.outfit_layer_subgraph.outfit_layer_state import *

from utils import *

from langchain_openai import ChatOpenAI 
from langchain_mistralai import ChatMistralAI
from langchain_ollama import ChatOllama

# Initialize the resources once
# llm = ChatOpenAI()
# local_llm = 'llama3.2'
# llm = ChatOllama(model=local_llm, temperature=0)

### Nodes
def rewrite_outfit_request_context(state: GenerateOutfitsState):
    """
    Node to extract colors from the outfit request.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the extracted colors and updated state.
    """
    # Extract relevant state variables
    messages = state["messages"]
    question = state["question"]
    model = state.get("model", "openai")
    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)
    rewrite_outfit_request_context_chain = get_rewrite_outfit_request_context_chain(llm)

    print("---REWRITING OUTFIT REQUEST COMTEXT---")

    # Invoke the chain to extract colors
    rewrite_outfit_request_context_output = rewrite_outfit_request_context_chain.invoke(
        {
            "messages": messages,
            "question": question,
            "outfit_request_context": state.get("outfit_request_context", ""),
        }
    )

    # Log the output for debugging
    print("Rewritten Outfit Context:", rewrite_outfit_request_context_output.outfit_request_context)

    # Update the state and return
    return {
        "outfit_request_context": rewrite_outfit_request_context_output.outfit_request_context,
    }

def extract_weighted_colors(state: GenerateOutfitsState):
    """
    Node to extract colors from the outfit request.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the extracted colors and updated state.
    """
    # Extract relevant state variables
    messages = state["messages"]
    question = state["question"]
    model = state.get("model", "openai")
    if model == "llama3.2":
        llm = ChatOllama(model=model, temperature=0)
    else:
        llm = ChatOpenAI(temperature=0)
    extract_colors_chain = get_extract_colors_chain(llm)

    print("---EXTRACTING COLORS---")

    # Invoke the chain to extract colors
    extracted_colors = extract_colors_chain.invoke(
        {
            "messages": messages,
            "question": question,
        }
    )

    # Log the output for debugging
    print("Extracted Colors:", extracted_colors.colors)

    # Update the state and return
    return {
        "extracted_colors": extracted_colors.colors,
    }

def retrieve_clothing_subset(state: GenerateOutfitsState):
    """
    Node to query a knowledge graph (KG) for relevant outfits based on user input.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the subset of outfits retrieved and their relevance scores.
    """
    # Retrieve necessary inputs from the state
    print("---RETRIEVING SEED ITEMS---")

    subset = retrieve_category_subset(state, "Clothing", 0.6)

    print("retrieved clothing subset: ", len(subset))

    return {
        "clothing_subset_items": subset, 
    }
def retrieve_shoes_subset(state: GenerateOutfitsState):
    """
    Node to query a knowledge graph (KG) for relevant outfits based on user input.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the subset of outfits retrieved and their relevance scores.
    """
    # Retrieve necessary inputs from the state
    print("---RETRIEVING SEED ITEMS---")

    subset = retrieve_category_subset(state, "Shoes", 0.25)

    print("retrieved shoes subset: ", len(subset))

    return {
        "shoes_subset_items": subset, 
    }

def retrieve_accessories_subset(state: GenerateOutfitsState):
    """
    Node to query a knowledge graph (KG) for relevant outfits based on user input.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the subset of outfits retrieved and their relevance scores.
    """
    # Retrieve necessary inputs from the state
    print("---RETRIEVING SEED ITEMS---")

    subset = retrieve_category_subset(state, "Accessories", 0.06)

    print("retrieved accessories subset: ", len(subset))

    return {
        "accessories_subset_items": subset, 
    }

def retrieve_bags_subset(state: GenerateOutfitsState):
    """
    Node to query a knowledge graph (KG) for relevant outfits based on user input.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the subset of outfits retrieved and their relevance scores.
    """
    # Retrieve necessary inputs from the state
    print("---RETRIEVING SEED ITEMS---")

    subset = retrieve_category_subset(state, "Bags", 0.05) 

    print("retrieved bags subset: ", len(subset))

    return {
        "bags_subset_items": subset, 
    }

def retrieve_jewelry_subset(state: GenerateOutfitsState):
    """
    Node to query a knowledge graph (KG) for relevant outfits based on user input.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the subset of outfits retrieved and their relevance scores.
    """
    # Retrieve necessary inputs from the state
    print("---RETRIEVING SEED ITEMS---")

    subset = retrieve_category_subset(state, "Jewelry", 0.04)

    print("retrieved jewelry subset: ", len(subset))

    return {
        "jewelry_subset_items": subset, 
    }

def retrieve_subset(state: GenerateOutfitsState):
    """
    Node to query a knowledge graph (KG) for relevant outfits based on user input.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the subset of outfits retrieved and their relevance scores.
    """
    # Retrieve necessary inputs from the state
    print("---RETRIEVING SEED ITEMS---")

    kg = get_neo4j_graph()

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_ENDPOINT = os.getenv('OPENAI_ENDPOINT')

    # # Query the KG using vector and fuzzy matching
    # subset = kg.query("""
    #     WITH genai.vector.encode(
    #         $question, 
    #         "OpenAI", 
    #         { token: $openAiApiKey, endpoint: $openAiEndpoint }
    #     ) AS question_embedding

    #     // Perform vector-based similarity search
    #     CALL db.index.vector.queryNodes(
    #         'captions', 
    #         1000,  // Retrieve a large number of nodes initially
    #         question_embedding
    #     ) YIELD node AS a, score

    #     // Normalize vector similarity score to a range of 0-1
    #     WITH a, score / 1.0 AS normalized_similarity_score

    #     // Convert colors_composition array to a single string for fuzzy matching
    #     WITH a, normalized_similarity_score, apoc.text.join(a.colors_composition, " ") AS colors_string

    #     // Perform fuzzy matching for colors
    #     WITH a, colors_string, normalized_similarity_score,
    #         size([color IN $colors WHERE apoc.text.fuzzyMatch(colors_string, color)]) AS fuzzy_color_match_count

    #     // Assign a binary score based on fuzzy matches
    #     WITH a, normalized_similarity_score,
    #         CASE WHEN fuzzy_color_match_count > 0 THEN 1 ELSE 0 END AS color_match_score

    #     // Combine vector similarity and keyword relevance, normalized
    #     WITH a, 
    #         (normalized_similarity_score * 0.7) + 
    #         (color_match_score * 0.3) AS combined_score

    #     // Filter by threshold
    #     // WHERE combined_score >= 0.5 
    #         //AND a.gender_category = $gender_category
    #         // AND a.category IN $valid_categories 
        
    #     WHERE a.gender_category = $gender_category

    #     // Tag retrieved nodes
    #     SET a:SubsetNode

    #     // Return relevant data
    #     RETURN a.products_href AS products_href, a.product_image_src AS product_image_src, a.brand AS brand, a.title AS title, a.image_caption AS image_caption, a.gender_category AS gender_category, a.colors_composition AS colors_composition, a.fabric_composition AS fabric_composition, a.category AS category, a.subcategory as subcategory, a.subsubcategory AS subsubcategory, combined_score
    #     ORDER BY combined_score DESC
    #     LIMIT 500
    #     """, 
    #     params={
    #         "openAiApiKey": OPENAI_API_KEY,
    #         "openAiEndpoint": OPENAI_ENDPOINT,
    #         "question": state.get("outfit_request_context", ""),
    #         "colors": state["extracted_colors"],
    #         "gender_category": 'Men' if state["user_profile"]["gender"].lower() == 'male' else 'Women',
    #     }
    # )

    k = 500  # Total number of items to retrieve
    category_limits = {
        "Clothing": int(k * 0.6),  # 50% for clothing
        "Shoes": int(k * 0.25),  # 25% for shoes
        "Accessories": int(k * 0.06),  # 5% for accessories
        "Bags": int(k * 0.05),  # 3% for bags
        "Jewelry": int(k * 0.04),  # 2% for jewelry
    }

    subset = []
    for category, limit in category_limits.items():
        category_subset = kg.query(f"""
            WITH genai.vector.encode(
                $question, 
                "OpenAI", 
                {{ token: $openAiApiKey, endpoint: $openAiEndpoint }}
            ) AS question_embedding

            CALL db.index.vector.queryNodes(
                'captions', 
                3000,  // Retrieve a large number of nodes initially
                question_embedding
            ) YIELD node AS a, score

            WITH a, score / 1.0 AS normalized_similarity_score
                                   
            // Convert colors_composition array to a single string for fuzzy matching
            WITH a, normalized_similarity_score, apoc.text.join(a.colors_composition, " ") AS colors_string

            // Perform fuzzy matching for colors
            WITH a, colors_string, normalized_similarity_score,
                size([color IN $colors WHERE apoc.text.fuzzyMatch(colors_string, color)]) AS fuzzy_color_match_count

            // Assign a binary score based on fuzzy matches
            WITH a, normalized_similarity_score,
                CASE WHEN fuzzy_color_match_count > 0 THEN 1 ELSE 0 END AS color_match_score
            
            WHERE a.gender_category = $gender_category
                AND a.category = $category  // Restrict to the current category
                                   
            // Combine vector similarity and keyword relevance, normalized
            WITH a, 
                (normalized_similarity_score * 0.7) + 
                (color_match_score * 0.3) AS combined_score

            // WITH a, 
            //     (normalized_similarity_score * 0.5) AS combined_score

            SET a:SubsetNode

            RETURN a.products_href AS products_href, 
                a.product_image_src AS product_image_src, 
                a.brand AS brand, 
                a.title AS title, 
                a.image_caption AS image_caption, 
                a.gender_category AS gender_category, 
                a.colors_composition AS colors_composition, 
                a.fabric_composition AS fabric_composition, 
                a.category AS category, 
                a.subcategory as subcategory, 
                a.subsubcategory AS subsubcategory, 
                combined_score
            ORDER BY combined_score DESC
            LIMIT $limit
        """, 
        params=
            {
                "openAiApiKey": OPENAI_API_KEY,
                "openAiEndpoint": OPENAI_ENDPOINT,
                "question": state.get("outfit_request_context", ""),
                "colors": state["extracted_colors"],
                "gender_category": 'Men' if state["user_profile"]["gender"].lower() == 'male' else 'Women',
                "category": category,
                "limit": limit
            }
        )

        print(f"Adding {limit} {category}")
        # print("subset_subsubcategories: ", set([item["category"] for item in category_subset]))
        print("Number of newly added: ", len(category_subset))

        subset.extend(category_subset)

    # print("gender: ", 'Men' if state["user_profile"]["gender"].lower() == 'male' else 'Women')

    return {
        "subset_items": subset, 
    }

def get_valid_seed_item_list(state: GenerateOutfitsState):
    """
    List all valid seed items

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the subset of outfits retrieved and their relevance scores.
    """
    print("---FILTERING VALID SEED ITEMS FROM THE SUBSET---")

    subset = state.get("clothing_subset_items", []) + state.get("shoes_subset_items", []) + state.get("accessories_subset_items", []) + state.get("bags_subset_items", []) + state.get("jewelry_subset_items", [])

    valid_seed_item_list = list(filter(lambda item: item['category'] in ['Clothing', 'Shoes'], subset))
    # print(valid_seed_item_list)

    return {
        "subset_items": subset, 
        "valid_seed_items": valid_seed_item_list,
    }

def retrieve_seed_items(state: GenerateOutfitsState):
    """
    Node to query a knowledge graph (KG) for relevant outfits based on user input.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the subset of outfits retrieved and their relevance scores.
    """
    print("---GETTING BATCH SEED ITEMs---")
    # valid_seed_item_list = list(filter(lambda item: item['category'] in ['Clothing', 'Shoes'], state["subset"]))

    valid_seed_item_list = state["valid_seed_items"]
    current_seed_item_list = valid_seed_item_list[state["seed_item_start"]:state["seed_item_start"]+10]
    print("current_seed_item_list length ", len(current_seed_item_list))

    # print("len(current_seed_item_list): ", len(current_seed_item_list))

    # Update the state with the retrieved subset and return
    return {
        "seed_items": current_seed_item_list, 
    }

def retrieve_seed_item(state: GenerateOutfitsState):
    """
    Node to query a knowledge graph (KG) for relevant outfits based on user input.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the subset of outfits retrieved and their relevance scores.
    """
    print("---GETTING SEED ITEM---")
    # valid_seed_item_list = list(filter(lambda item: item['category'] in ['Clothing', 'Shoes'], state["subset"]))

    valid_seed_item_list = state["valid_seed_items"]
    current_seed_item_list = valid_seed_item_list[state["seed_item_start"]:state["seed_item_start"]+10]
    print("current_seed_item_list length ", len(current_seed_item_list))

    print("len(current_seed_item_list): ", len(current_seed_item_list))

    # Update the state with the retrieved subset and return
    return {
        "seed_item": current_seed_item_list[0], 
    }

# def get_style_rules_for_all_seed_items(state: GenerateOutfitsState):
#     """
#     Generate style rules for all seed items in one bulk LLM call.
#     """
#     seed_items = state["seed_items"]
#     outfit_request = state["outfit_request_context_subgraph"]

#     print("---GETTING STYLE RULES FOR ALL SEED ITEMS IN BULK---")

#     # Bulk LLM call
#     style_rules_output = get_style_rules_bulk(seed_items, outfit_request)

#     #tasks = []
#     for style_query in style_queries:
#         tasks.append(astyle_rules_chain(llm, style_query, outfit_request, seed_item_str))
#     results = await asyncio.gather(*tasks)

#     # Store results in the state
#     return {"style_rules_bulk": style_rules_output}

# def generate_outfit(state: OutfitState):
#     """
#     Node to query a knowledge graph (KG) for relevant outfits based on user input.

#     Args:
#         state (QuestionsState): The current graph state.

#     Returns:
#         dict: Contains the subset of outfits retrieved and their relevance scores.
#     """
#     try:
#         print("---GENERATING MATCHING ITEMS TO SEED---")

#         # Extract necessary data
#         seed_item = state["seed_item"]
#         seed_item_str = format_seed_item_as_string(seed_item)
#         subset_items = state["subset_items"]
#         outfit_request_context = state["outfit_request_context"]

#         async def async_task(seed_item_str, subset_items, outfit_request_context):
#             return await agenerate_outfit_with_internal_style_rules(
#                 seed_item_str, subset_items, outfit_request_context
#             )

#         # Use the running event loop if available
#         try:
#             loop = asyncio.get_running_loop()
#         except RuntimeError:
#             loop = None

#         if loop and loop.is_running():
#             # Run async function using `asyncio.create_task` within the running loop
#             results = asyncio.run_coroutine_threadsafe(
#                 async_task(seed_item_str, subset_items, outfit_request_context), loop
#             ).result()
#         else:
#             # If no running loop, use `asyncio.run` in standalone environments
#             results = asyncio.run(async_task(seed_item_str, subset_items, outfit_request_context))

#         # Format the results
#         outfit = {
#             "articles": [
#                 result["products_href"]
#                 for result in results["selected_items"]
#                 if "products_href" in result
#             ],
#             "image_sources": [
#                 result["product_image_src"][0]
#                 for result in results["selected_items"]
#                 if "product_image_src" in result
#             ],
#             "generated_by": "ai",
#             "style_rules_used": results["style_rules_used"],
#             "style_rules_sources": results["style_rules_sources"],
#         }

#         return {"outfits": [outfit]}

#     except Exception as e:
#         print(f"Error during outfit generation: {e}")
#         raise

#works well outfit generation API
# not used
def generate_outfit(state: OutfitState): #OutfitLayerState): #//retrieve_matching_items_to_seed(state: GenerateOutfitsState):
    """
    Node to query a knowledge graph (KG) for relevant outfits based on user input.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the subset of outfits retrieved and their relevance scores.
    """
    # Retrieve necessary inputs from the state
    print("---GENRATING MATCHING ITEMS TO SEED---")

    # kg = get_neo4j_graph()

    # OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    # OPENAI_ENDPOINT = os.getenv('OPENAI_ENDPOINT')

    # Extract the value for products_href
    seed_item = state["seed_item"]
    # products_href_value = seed_item["products_href"]

    # subset_products_href_list = [subset_item['products_href'] for subset_item in state["subset_items"]]

    # Generate Outfit
    print("problem")
    seed_item_str = format_seed_item_as_string(seed_item)
    style_rules_output = asyncio.run(
        agenerate_style_rules(
            seed_item_str = seed_item_str, 
            outfit_request=state["outfit_request_context_subgraph"],
        )
    )
    results = generate_outfit_with_internal_style_rules_sequential(
        subset=state["subset_items_subgraph"], 
        outfit_request=state["outfit_request_context_subgraph"],
        seed_item=seed_item,
        style_rules_output=style_rules_output
    )
    
    # print("Selected subsubcategories: ", [item["subcategory"] for item in results["selected_items"]])

    # results = asyncio.run(
    #     agenerate_outfit_with_internal_style_rules(seed_item_str, 
    #                                                state["subset_items"], 
    #                                                state["outfit_request_context"],
    #                                             #    seed_item,
    #                                                )
    # )
    # print("results ", results["selected_items"])
    # print("subsubcategory:", [result["subsubcategory"] for result in results["selected_items"] if "subsubcategory" in result],
    #     "title", [result["title"] for result in results["selected_items"] if "title" in result])

    outfit = {
        "subsubcategory": [result["subsubcategory"] for result in results["selected_items"] if "subsubcategory" in result],
        "title": [result["title"] for result in results["selected_items"] if "title" in result],
        "image_sources": [result["product_image_src"][0] for result in results["selected_items"] if "product_image_src" in result],
        "articles": [result["products_href"] for result in results["selected_items"] if "products_href" in result],
        "generated_by": "ai",
        # "outfit_description": results["outfit_description"],
        "style_rules_used": style_rules_output.style_rules,
        "style_rules_sources": style_rules_output.style_rules_sources,
    }
    # print("outfit: ", outfit)

    # print("outfit ", outfit.keys())
    # print(outfit)


    # print("connected_articles: ", connected_articles)
    # print("subset_products_href_list", subset_products_href_list)

    # print("matched_connected_articles: ", ma§dtched_connected_articles)

    return {
        "outfits": [outfit]
    }

def get_connected_neo4j_items_from_subset(state: OutfitState): #OutfitLayerState): #//retrieve_matching_items_to_seed(state: GenerateOutfitsState):
    """
    Node to query a knowledge graph (KG) for relevant outfits based on user input.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the subset of outfits retrieved and their relevance scores.
    """
    # Retrieve necessary inputs from the state
    print("---GETTING CONNECTED NEO4J ITEMS--")

    kg = get_neo4j_graph()

    # OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    # OPENAI_ENDPOINT = os.getenv('OPENAI_ENDPOINT')

    # Extract the value for products_href
    seed_item = state["seed_item"]
    products_href_value = seed_item["products_href"]

    subset_products_href_list = [subset_item['products_href'] for subset_item in state["subset_items"]]

    # Define the Cypher query using a parameter
    query = """ 
    MATCH (item:Article)<-[:COMPOSED_OF]-(outfit:Outfit)-[:COMPOSED_OF]->(related:Article)
    WHERE item.products_href = $products_href_value 
    WITH 
        collect({products_href: item.products_href, product_image_src: head(item.product_image_src)}) + 
        collect({products_href: related.products_href, product_image_src: head(related.product_image_src)}) AS combined_items
    UNWIND combined_items AS items
    RETURN DISTINCT items.products_href AS products_href, items.product_image_src AS product_image_src
    """

    # Execute the query with the parameter
    results = kg.query(
        query, params={
            "products_href_value": products_href_value, 
            "subset_products_href_list": subset_products_href_list
        }
    )
    connected_articles = {
        "articles": [result["products_href"] for result in results if "products_href" in result],
        "image_sources": [result["product_image_src"] for result in results if result.get("product_image_src")],
        "generated_by": "ai",
    }

    # print("connected_articles: ", connected_articles)
    # print("subset_products_href_list", subset_products_href_list)

    matched_connected_articles = {
        "articles": [item for item in connected_articles['articles'] if item in set(subset_products_href_list)],
        "image_sources": [
            src for item, src in zip(connected_articles['articles'], connected_articles['image_sources']) 
            if item in set(subset_products_href_list)
        ],
        "generated_by": connected_articles["generated_by"]
    }

    # print("matched_connected_articles: ", ma§dtched_connected_articles)

    return {
        "outfits": [matched_connected_articles]
    }

# Here we will judge the best joke
def generate_outfit_cards(state: GenerateOutfitsState):
    print("---GENERATING OUTFIT CARDS---")
    first_name = state["user_profile"]["first_name"]

    # Format the data into a string
    formatted_string = ""
    for index, item in enumerate(state["outfits"], start=1):
        outfit_urls = "\n    ".join(item['image_sources'])
        formatted_string += f"**Outfit {index}**:\n    {outfit_urls}\n"
        formatted_string += f"**Titles**:\n    {item['title']}\n"
        formatted_string += f"**Subsubcategories**:\n    {item['subsubcategory']}\n"
        # formatted_string += f"**Styles Rule Used**:\n    {item['style_rules_used']}\n"
        formatted_string += f"**Sources**:\n    {item['style_rules_sources']}\n\n"

    print("number of outfits: ", len(state["outfits"]))

    return {
        "generation": f"Here are the generated outfits based on your needs, {first_name}! \n\n{formatted_string}",
        "stage": 3,
    }

def retrieve_outfits(state: GenerateOutfitsState):
    """
    Node to query a knowledge graph (KG) for relevant outfits based on user input.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the subset of outfits retrieved and their relevance scores.
    """
    # Retrieve necessary inputs from the state
    print("---QUERYING KNOWLEDGE GRAPH FOR RELEVANT OUTFITS---")

    question = state["question"]

    kg = get_neo4j_graph()

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_ENDPOINT = os.getenv('OPENAI_ENDPOINT')

    # Query the KG using vector and fuzzy matching
    subset = kg.query("""
        WITH genai.vector.encode(
            $question, 
            "OpenAI", 
            { token: $openAiApiKey, endpoint: $openAiEndpoint }
        ) AS question_embedding

        // Perform vector-based similarity search
        CALL db.index.vector.queryNodes(
            'captions', 
            1000,  // Retrieve a large number of nodes initially
            question_embedding
        ) YIELD node AS a, score

        // Normalize vector similarity score to a range of 0-1
        WITH a, score / 1.0 AS normalized_similarity_score

        // Convert colors_composition array to a single string for fuzzy matching
        WITH a, normalized_similarity_score, apoc.text.join(a.colors_composition, " ") AS colors_string

        // Perform fuzzy matching for colors
        WITH a, colors_string, normalized_similarity_score,
            size([color IN $colors WHERE apoc.text.fuzzyMatch(colors_string, color)]) AS fuzzy_color_match_count

        // Assign a binary score based on fuzzy matches
        WITH a, normalized_similarity_score,
            CASE WHEN fuzzy_color_match_count > 0 THEN 1 ELSE 0 END AS color_match_score

        // Combine vector similarity and keyword relevance, normalized
        WITH a, 
            (normalized_similarity_score * 0.6) + 
            (color_match_score * 0.3) AS combined_score

        // Filter by threshold
        WHERE combined_score >= 0.5

        // Tag retrieved nodes
        SET a:SubsetNode

        // Return relevant data
        RETURN a.products_href, a.title, a.image_caption, a.colors_composition, combined_score
        ORDER BY combined_score DESC
        LIMIT 10
        """, 
        params={
            "openAiApiKey": OPENAI_API_KEY,
            "openAiEndpoint": OPENAI_ENDPOINT,
            "question": state["outfit_request_context"],
            "colors": state["extracted_colors"],
        }
    )

    # Log the output for debugging
    # print("Retrieved Subset:", subset)

    outfits = []

    for seed_item in subset:
        # Extract the value for products_href
        products_href_value = seed_item["a.products_href"]

        # Define the Cypher query using a parameter
        query = """
        MATCH (item:Article)<-[:COMPOSED_OF]-(outfit:Outfit)-[:COMPOSED_OF]->(related:Article)
        WHERE item.products_href = $products_href_value
        MATCH (outfit)-[:COMPOSED_OF]->(related:Article)
        WITH collect(item.products_href) + collect(related.products_href) AS combined_items
        UNWIND combined_items AS items
        RETURN DISTINCT items
        """
        
        # Execute the query with the parameter
        results = kg.query(query, params={"products_href_value": products_href_value})
        outfits.append({"articles": [result["items"] for result in results], "generated_by": "ai"})

    # Format the data into a string
    formatted_string = ""
    for index, item in enumerate(outfits, start=1):
        outfit_urls = "\n    ".join(item['articles'])
        formatted_string += f"Outfit {index}:\n    {outfit_urls}\n\n"

    # Print the formatted string
    # print(formatted_string)

    # product_image_src

    messages = [
        HumanMessage(content=state["question"]),
        SystemMessage(content="Here are some outfits tailored to your needs!"),
    ]

    user_name = state["user_profile"]["first_name"]

    # Update the state with the retrieved subset and return
    return {
        "outfits": outfits, 
        "messages": messages,
        "generation": f"Here are some outfits tailored to your needs, {user_name}!"
    }

def retrieve_image_outfits(state: GenerateOutfitsState):
    """
    Node to query a knowledge graph (KG) for relevant outfits based on user input.

    Args:
        state (QuestionsState): The current graph state.

    Returns:
        dict: Contains the subset of outfits retrieved and their relevance scores.
    """
    # Retrieve necessary inputs from the state
    print("---QUERYING KNOWLEDGE GRAPH FOR RELEVANT OUTFITS---")

    kg = get_neo4j_graph()

    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_ENDPOINT = os.getenv('OPENAI_ENDPOINT')

    # Query the KG using vector and fuzzy matching
    subset = kg.query("""
        WITH genai.vector.encode(
            $question, 
            "OpenAI", 
            { token: $openAiApiKey, endpoint: $openAiEndpoint }
        ) AS question_embedding

        // Perform vector-based similarity search
        CALL db.index.vector.queryNodes(
            'captions', 
            1000,  // Retrieve a large number of nodes initially
            question_embedding
        ) YIELD node AS a, score

        // Normalize vector similarity score to a range of 0-1
        WITH a, score / 1.0 AS normalized_similarity_score

        // Convert colors_composition array to a single string for fuzzy matching
        WITH a, normalized_similarity_score, apoc.text.join(a.colors_composition, " ") AS colors_string

        // Perform fuzzy matching for colors
        WITH a, colors_string, normalized_similarity_score,
            size([color IN $colors WHERE apoc.text.fuzzyMatch(colors_string, color)]) AS fuzzy_color_match_count

        // Assign a binary score based on fuzzy matches
        WITH a, normalized_similarity_score,
            CASE WHEN fuzzy_color_match_count > 0 THEN 1 ELSE 0 END AS color_match_score

        // Combine vector similarity and keyword relevance, normalized
        WITH a, 
            (normalized_similarity_score * 0.6) + 
            (color_match_score * 0.3) AS combined_score

        // Filter by threshold
        WHERE combined_score >= 0.5 AND a.gender_category = $gender_category

        // Tag retrieved nodes
        SET a:SubsetNode

        // Return relevant data
        RETURN a.products_href, a.title, a.image_caption, a.colors_composition, combined_score
        ORDER BY combined_score DESC
        LIMIT 10
        """, 
        params={
            "openAiApiKey": OPENAI_API_KEY,
            "openAiEndpoint": OPENAI_ENDPOINT,
            "question": state["outfit_request_context"],
            "colors": state["extracted_colors"],
            "gender_category": state["user_profile"]["gender"],
        }
    )

    # Log the output for debugging
    # print("Retrieved Subset:", subset)

    outfits = []

    for seed_item in subset:
        # Extract the value for products_href
        products_href_value = seed_item["a.products_href"]

        # Define the Cypher query using a parameter
        query = """
        MATCH (item:Article)<-[:COMPOSED_OF]-(outfit:Outfit)-[:COMPOSED_OF]->(related:Article)
        WHERE item.products_href = $products_href_value
        MATCH (outfit)-[:COMPOSED_OF]->(related:Article)
        WITH collect(item.product_image_src) + collect(related.product_image_src) AS combined_items
        UNWIND combined_items AS image_source
        RETURN DISTINCT image_source
        """
        
        # Execute the query with the parameter
        results = kg.query(query, params={"products_href_value": products_href_value})
        outfits.append({"outfit": [result["image_source"][0] for result in results]})

    # Format the data into a string
    formatted_string = ""
    for index, item in enumerate(outfits, start=1):
        outfit_urls = "\n    ".join(item['outfit'])
        formatted_string += f"Outfit {index}:\n    {outfit_urls}\n\n"

    # Print the formatted string
    # print(formatted_string)

    # product_image_src

    # Update the state with the retrieved subset and return
    return {
        "generated_outfits": outfits,
        "outfits": outfits, 
        "generation": f"Here are the generated outfits based on your needs! {formatted_string}"
    }
