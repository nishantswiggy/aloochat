import json
import random
import json
def convert_json(data):
    print("data", data)
    # Initialize the result with a button and empty sections
    result = {
        "button": "Item options",
        "sections": []
    }
    print("data", data)

    # Loop through each restaurant in the input data
    for restaurant_id, restaurant_info in data.items():
        # Create a section for each restaurant
        section = {
            "title": restaurant_info["restaurant_name"][:21],  # Use restaurant name as title
            "rows": []  # Initialize rows for this restaurant
        }

        # Loop through each item in the restaurant's menu
        for item in restaurant_info["items"]:
            # Add each item as a row in the restaurant's section
            row = {
                "id": item["id"],
                "description": "SLA " + str(random.randint(15, 25)) + " mins \U0001F680" +"|"+ "₹" + str(item["price"])+" | "+item["rating"] +"\u2605",
                "title": item["name"][:21] + "..." if len(item["name"]) > 21 else item["name"],
            }
            section["rows"].append(row)

        # Add the section to the sections list
        result["sections"].append(section)

    print("type(result)", type(result))
    return json.dumps(result)