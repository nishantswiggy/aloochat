import call_ds
import get_item
import tranformItemData

def getWhatsappResponse(conversation, message):
    ds_response = call_ds.call_ds(conversation, message)
    items_json = {}
    if "search_query" in ds_response and len(ds_response["search_query"]) >0:
        items_json = get_item.get_items(ds_response["search_query"][0])
        tranformItemData.convert_json(items_json)
    print(items_json)
    return items_json
