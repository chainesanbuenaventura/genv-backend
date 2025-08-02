import ast

def simplify_dicts(items, keys_to_keep=['brand', 'title', 'category', 'subcategory', 'subsubcategory']):
    return [{key: item[key] for key in keys_to_keep if key in item} for item in items]

def format_fabric_composition_as_string(fabric_composition):
    """
    Format the fabric composition as a single-line string.
    """
    # Parse the string into a Python object
    parsed_data = ast.literal_eval(fabric_composition)

    # Initialize an empty list for the formatted string
    formatted_string = []

    # Extract and format the data
    for layer in parsed_data:
        layer_name = layer.get("layer_name", "Unknown Layer")
        layer_string = [f"{layer_name}"]
        for composition in layer.get("composition", []):
            material = composition.get("material", "Unknown Material")
            percentage = composition.get("percentage", 0)
            layer_string.append(f"({material} {percentage}%);")
        formatted_string.append(" ".join(layer_string))

    # Join the formatted strings into one final output, with no newlines
    single_line_output = " ".join(formatted_string)
    
    return single_line_output

def format_seed_item_as_string(seed_item):
    seed_item_str = ""

    for key, value in seed_item.items():
        if key not in ["product_image_src", "products_href", "combined_score", "category", "brand"]:
            if key == "fabric_composition" and len(value) > 0:
                # print("formatting: ", value)
                value = "\n" + format_fabric_composition_as_string(value)
            seed_item_str += key.split(".")[-1] + ": " + str(value) + "\n"
    
    return seed_item_str

def filter_by_subset(original_list, subset):
    result = []
    for item in original_list:
        for sub_item in subset:
            # Check if all key-value pairs in sub_item match the current item
            if all(item.get(key) == value for key, value in sub_item.items()):
                result.append(item)
                break  # Avoid duplicate matches
    return result