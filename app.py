import os

from flask import Flask, jsonify, request
# from pyngrok import ngrok, conf
import json
import requests

import itemService

# conf.get_default().verify_ssl = False
# Add this line before connecting
# ngrok.set_auth_token("2twNTpr5zG3U0ckMbzhUwg0acHA_388Ufsb8ZR56f38NyUsS3")

app = Flask(__name__)

# Replace with your third-party provider's API credentials
WHATSAPP_API_URL = 'https://graph.facebook.com/v22.0/601304399725157/messages'
PHONE_NUMBER = '+917503603082'

recipient = "+919041047119"
# update this token if you get token expiry issue
ACCESS_TOKEN = "EAAP3nUnNbEkBO3fCGYCqWPZCEngoRpvcBQdCa1tIApZBXVQPssQ8QbccPZANJZBStUSKiwWxJwk2lzsnXjxXc4NwFYrliWunwfWnZANSwp0NrviPAfwyrofe5XPxPU48QKtPrLFKLmMr9G3L5zfXQL5WA7rxxGZB3ZCbNd513sCuiZCJ7o7anlN2ROfZAO2u0XKsiFUkXPt1fkRAqVNF1Jzcn0jLEZBcZBxF5aomEQHbzKn"
audio_url = "https://dl.espressif.com/dl/audio/ff-16b-2c-44100hz.mp3"
STATIC_VERIFY_TOKEN_CONST="EAAh5gkR5E70BOZBUYBiVYeyOICETbTqs87ZCRWoVotc6VZA4ebZBJYgrhRoF8h9Ghq43MErZCLPl1toZCWLv4Nkq85Yb8n7zwZBH8IAlEbFkcONDZBZB8DYkiWA4s55bfiMMxo9ifnnEbOSZBP53StGQw4IJPOR7Fn6RrH9yb0bOt262cf2ZAmp1vnsF6b88noKf6tU5Wh7IFmPoTlSoV6dVTMIhJVyYdUZCyKhbgExPHQH1S2P6"
PHONE_NUMBER_ID=601304399725157

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Handles the webhook verification request from WhatsApp"""
    # Get the 'hub.mode', 'hub.challenge', and 'hub.STATIC_verify_token_CONST' from the query parameters
    mode = request.args.get('hub.mode')
    challenge = request.args.get('hub.challenge')
    token = request.args.get('hub.STATIC_verify_token_CONST')

    # Check if the verify token matches
    if token == STATIC_VERIFY_TOKEN_CONST:
        # If the token is valid, return the challenge to complete the verification
        return str(challenge), 200
    else:
        # If the token doesn't match, return an error response
        return 'Verification failed', 403


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Received webhook data:", data)

    try:
        messages = data['entry'][0]['changes'][0]['value'].get('messages', [])

        for message in messages:
            # ✅ Ignore messages categorized as "utility"
            if message.get("context", {}).get("category") == "utility":
                print("Ignoring utility message.")
                continue  # Skip processing this message

            message_type = message['type']
            from_number = message['from']

            if message_type == 'text':
                handle_text_message(message, from_number)
            elif message_type == 'image':
                handle_media_message(message, 'image', from_number)
            elif message_type == 'video':
                handle_media_message(message, 'video', from_number)
            elif message_type == 'audio':
                handle_media_message(message, 'audio', from_number)
            elif message_type == 'document':
                handle_media_message(message, 'document', from_number)
            elif message_type == 'location':
                handle_location_message(message, from_number)
            else:
                print(f"Unsupported message type: {message_type}")

        return jsonify({"status": "success"}), 200

    except Exception as e:
        print(f"Error processing message: {e}")
        return jsonify({"status": "failure", "error": str(e)}), 400


def handle_text_message(message, to_number):
    """Function to handle incoming text messages and send a text response"""
    text_body = message['text']['body']
    print(f"Received text message: {text_body}")

    # output = itemService.getWhatsappResponse("conversation", text_body)
    output = text_body

    print(f"output text message: {output}")

    # Respond with the same text
    send_text_message(to_number, output)

def handle_location_message(message, to_number):
    """Function to handle incoming location messages and send a location response"""
    latitude = message['location']['latitude']
    longitude = message['location']['longitude']
    print(f"Received location: Latitude={latitude}, Longitude={longitude}")

    # Respond with the same location
    send_location_message(to_number, latitude, longitude)


def send_text_message(to_number, text_body):
    """Send a text message back to the user"""
    response_data = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {
            "body": text_body
        }
    }
    send_message(response_data)

def send_location_message(to_number, latitude, longitude):
    """Send a location message back to the user"""
    response_data = {
        "to": to_number,
        "messaging_product": "whatsapp",
        "messages": [
            {
                "type": "location",
                "location": {
                    "latitude": latitude,
                    "longitude": longitude
                }
            }
        ]
    }
    send_message(response_data)


def send_message(response_data):
    """Send the response message via WhatsApp Business API"""
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Send the response to WhatsApp API
    response = requests.post(WHATSAPP_API_URL, json=response_data, headers=headers)

    if response.status_code == 200:
        print("Message sent successfully")
    else:
        print(f"Failed to send message. Status code: {response.status_code}, Error: {response.text}")

@app.route('/health-check',methods=['GET'])
def health_check():
    return jsonify({
        "message": "Hello World",
        "status": "success"
    })

def handle_media_message(message, media_type, to_number):
    media_id = message[media_type]['id']
    mime_type = message[media_type]['mime_type']
    original_media_url = get_media_url(media_id)
    if not original_media_url:
        print("Failed to retrieve media URL")
        return

    print(f"Received {media_type}: {media_id}, MIME: {mime_type}, Original URL: {original_media_url}")

    handle_received_media(media_id, media_type, mime_type, to_number, ACCESS_TOKEN, PHONE_NUMBER_ID)

def get_media_url(media_id):
    url = f'https://graph.facebook.com/v22.0/{media_id}?fields=url'
    headers = {'Authorization': f'Bearer {ACCESS_TOKEN}'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        media_data = response.json()
        return media_data.get('url')
    else:
        print(f"Failed to get media URL: {response.status_code}, {response.text}")
        return None

def handle_received_media(media_id, media_type, mime_type, to_number, token, phone_number_id):

    # Step 1: Get Media URL from WhatsApp
    media_url = get_media_url(media_id)
    if not media_url:
        print("Failed to retrieve media URL.")
        return

    # Step 2: Download media locally
    filepath = f'/tmp/{media_id}'
    headers = {'Authorization': f'Bearer {token}'}
    media_response = requests.get(media_url, headers=headers)
    if media_response.status_code != 200:
        print(f"Media download failed: {media_response.status_code}, {media_response.text}")
        return

    with open(filepath, 'wb') as f:
        f.write(media_response.content)

    upload_url = f"https://graph.facebook.com/v22.0/{phone_number_id}/media"
    headers = {'Authorization': f'Bearer {token}'}
    data = {
        'messaging_product': 'whatsapp'
    }
    with open(filepath, 'rb') as file_data:
        upload_response = requests.post(
            upload_url,
            headers=headers,
            data=data,  # ✅ this line was missing
            files={'file': (filepath.split("/")[-1], file_data, mime_type)}
        )

    if upload_response.status_code != 200:
        print(f"Media upload failed: {upload_response.status_code}, {upload_response.text}")
        return

    new_media_id = upload_response.json().get('id')

    # Step 4: Send media message using the new media_id
    send_message_url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": media_type,
        media_type: {"id": new_media_id}
    }

    send_response = requests.post(send_message_url, headers=headers, json=payload)

    if send_response.status_code == 200:
        print("Media message sent successfully.")
    else:
        print(f"Failed to send message: {send_response.status_code}, {send_response.text}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

