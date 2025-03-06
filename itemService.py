import amitabhTTS
import call_ds
import get_item
import tranformItemData
from app import send_media_message


def getWhatsappResponse(to_number, conversation, message):
    print(f"getWhatsappResponse conversation: {conversation}, message: {message}")
    ds_response = call_ds.call_ds(message, conversation)
    #amitabhTTS.get_amitabh_audio(ds_response)
    #send_media_message(to_number )
    print(f"getWhatsappResponse ds_response: {ds_response}")
    items_json = {}
    print("search_query" in ds_response)
    print(len(ds_response.search_query))
    if len(ds_response.search_query) > 0:
        print(f"Inside search query: {ds_response.search_query}:")
        items_json = get_item.get_items(ds_response.search_query[0])
        output = tranformItemData.convert_json(items_json)
        return output, ""
    return items_json, ds_response.response
