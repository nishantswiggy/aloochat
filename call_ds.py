import requests
import json


ConversationID = ""

def call_ds(message,conversation_id):
    # Headers
    headers = {
        "content-type": "application/json; charset=utf-8"
    }


    # Post request body (replace with actual data)
    post_request_body = {
           "user_id": "123",
           "message": message,
           "conversation_id":conversation_id,
           "personality": "funny"
         }

    # API URL
    TARGET_SERVICE_HOST_NAME = "http://localhost:8000/chat"
    # Make API Call
    response = requests.post(TARGET_SERVICE_HOST_NAME, headers=headers, json=post_request_body)
    return json.loads(response.text)