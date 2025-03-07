import amitabhTTS
import call_ds
import get_item
import tranformItemData
from app import send_media_message

ConversationID = ""
def getWhatsappResponse(to_number, message):
    global ConversationID
    print(f"getWhatsappResponse conversation: {ConversationID}, message: {message}")
    ds_response = call_ds.call_ds(message, ConversationID)
    if ds_response.conversation_id is not None:
        ConversationID = ds_response.conversation_id
    amitabhTTS.get_amitabh_audio(ds_response)
    send_media_message(to_number )
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
