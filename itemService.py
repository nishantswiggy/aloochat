import call_ds
import get_item
import tranformItemData


def getWhatsappResponse(conversation, message):
    print(f"getWhatsappResponse conversation: {conversation}, message: {message}")
    ds_response = call_ds.call_ds(message, conversation)
    print(f"getWhatsappResponse ds_response: {ds_response}")
    items_json = {}
    if "search_query" in ds_response and len(ds_response["search_query"]) > 0:
        items_json = get_item.get_items(ds_response["search_query"][0])
        output = tranformItemData.convert_json(items_json)
        return output, ""
    print(items_json)
    return items_json, ds_response
