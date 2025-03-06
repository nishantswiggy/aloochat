import requests
import json
import re

def get_items(search_query):
    # Headers
    headers = {
        "Host": "disc.swiggy.com",
        "user-agent": "Swiggy-Android",
        "tid": "ef892bd0-3613-48b2-ab91-fd07db1a3e04",
        "sid": "iea6e2fe-5410-4aa5-8582-c55bff4f683c",
        "version-code": "10004",
        "app-version": "4.72.0",
        "latitude": "12.9304278",
        "longitude": "77.678404",
        "os-version": "14",
        "accessibility_enabled": "false",
        "current-latitude": "12.9304267",
        "current-longitude": "77.6784033",
        "swuid": "64f133eb27216c70",
        "token": "996e4b17-e909-444a-b190-d749d1fd003c5cf1cd1f-dae0-4290-b82b-43758fbbaa37",
        "deviceid": "64f133eb27216c70",
        "device": "swiggy_qa",
        "x-network-quality": "GOOD",
        "pl-version": "88",
        "cache-control": "no-store",
        "accept": "application/json; charset=utf-8",
        "content-type": "application/json; charset=utf-8"
    }


    # Parameters
    params = {
        "lat": "12.9327",
        "lng": "77.6036"
    }

    # Post request body (replace with actual data)
    post_request_body = {"categoryPage":"FOOD","deselectedFacets":{},"isSimilarRxFlow":0,"marketplaces":[{"businessLineId":"FOOD","marketplaceId":"SWIGGY"}],"query":search_query,"queryUniqueId":"af895978-a197-4046-95aa-d2309746746b","redirection":1,"sldEnabled":0,"submitAction":"DEEPLINK","supportedMarketplaces":[{"businessLineId":"FOOD","marketplaceId":"SWIGGY"},{"businessLineId":"INSTAMART","marketplaceId":"SWIGGY"},{"businessLineId":"DINEOUT","marketplaceId":"SWIGGY"}],"supportedTabs":["RESTAURANT","DISH","INSTAMART"],"trackingId":"3080b488-12a9-42a9-a997-9262591785fb"}

    # API URL
    TARGET_SERVICE_HOST_NAME = "https://disc.swiggy.com"
    endpoint = "/api/v3/json/search/DISH"
    url = f"{TARGET_SERVICE_HOST_NAME}{endpoint}"
    image_url_prefix = "https://media-assets.swiggy.com/swiggy/image/upload/"
    # Make API Call
    response = requests.post(url, headers=headers, params=params, json=post_request_body)
    json_obj = json.loads(response.text)
    restaurant_dishes = {}  # Dictionary to store restaurant-wise dishes

    for card in json_obj["success"]["cards"][0]["groupedCard"]["cardGroupMap"]["DISH"]["cards"]:
        if (
                "card" in card
                and "card" in card["card"]
                and "@type" in card["card"]["card"]
                and card["card"]["card"]["@type"] == "type.googleapis.com/swiggy.presentation.food.v2.DishGroup"
        ):
            restaurant_id = card["card"]["card"]["restaurant"]["info"]["id"]
            restaurant_name = re.sub(r'[^A-Za-z0-9 ]+', '', card["card"]["card"]["restaurant"]["info"]["name"])
            if len(restaurant_dishes) > 2:
                break
            # Initialize restaurant entry if not already present
            if restaurant_id not in restaurant_dishes:
                restaurant_dishes[restaurant_id] = {
                    "restaurant_name": restaurant_name,
                    "items": []
                }

            # Loop through dishes and add them to the restaurant's list
            for dish in card["card"]["card"]["dishes"]:
                if "imageId" in dish["info"] and "id" in dish["info"] and "name" in dish["info"] :
                    if len(restaurant_dishes[restaurant_id]["items"]) > 2:
                        break
                    dish_obj = {
                        "id": dish["info"]["id"],
                        "name": re.sub(r'[^A-Za-z0-9 ]+', '', dish["info"]["name"]),
                        "imageId": image_url_prefix + dish["info"]["imageId"]
                    }
                    restaurant_dishes[restaurant_id]["items"].append(dish_obj)

    # Return the structured data
    return restaurant_dishes