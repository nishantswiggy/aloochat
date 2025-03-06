import os

from flask import Flask, jsonify, request
# from pyngrok import ngrok, conf
import json
import requests
# conf.get_default().verify_ssl = False
# Add this line before connecting
# ngrok.set_auth_token("2twNTpr5zG3U0ckMbzhUwg0acHA_388Ufsb8ZR56f38NyUsS3")

# class AudioMessage:
#     def __init__(self, to, audio_url):
#         self.messaging_product = "whatsapp"
#         self.to = to
#         self.type = "audio"
#         self.audio = {"link": audio_url}
#
#     def to_json(self):
#         return {
#             "messaging_product": self.messaging_product,
#             "to": self.to,
#             "type": self.type,
#             "audio": self.audio
#         }
#
#
# class ImageMessage:
#     def __init__(self, to, image_url):
#         self.messaging_product = "whatsapp"
#         self.to = to
#         self.type = "image"
#         self.image = {
#             "link": image_url,
#             "caption": "Image sent via WhatsApp API"  # Optional caption
#         }
#
#     def to_json(self):
#         return {
#             "messaging_product": self.messaging_product,
#             "to": self.to,
#             "type": self.type,
#             "image": self.image
#         }
#
# def send_whatsapp_image(to: str, token: str, image_url: str):
#     url = "https://graph.facebook.com/v22.0/601304399725157/messages"
#
#     # Create message payload
#     message = ImageMessage(to, image_url)
#
#     # Set headers
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {token}"
#     }
#
#     # Send request
#     response = requests.post(
#         url,
#         headers=headers,
#         json=message.to_json()
#     )
#
#     print("Response Status:", response.status_code)
#     return response
#
# def send_whatsapp_audio(to: str, token: str, audio_url: str):
#     url = "https://graph.facebook.com/v22.0/601304399725157/messages"
#
#     # Create message payload
#     message = AudioMessage(to, audio_url)
#
#     # Set headers
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": f"Bearer {token}"
#     }
#
#     # Send request
#     response = requests.post(
#         url,
#         headers=headers,
#         json=message.to_json()
#     )
#
#     print("Response Status:", response.status_code)
#     return response
app = Flask(__name__)

# @app.route('/', methods=['GET'])
# def hello_world():
#     return jsonify({
#         "message": "Hello World",
#         "status": "success"
#     })
# Replace with your third-party provider's API credentials
WHATSAPP_API_URL = 'https://graph.facebook.com/v22.0/601304399725157/messages'
PHONE_NUMBER = '+917503603082'

recipient = "+919041047119"
ACCESS_TOKEN = "EAAh5gkR5E70BOxfEgkYZAxztMzjxLO0bkeZC2ZA863r5bpa3gC89iZAoZAoCXWWL9NGrudoNGPEvEmIgIieom4aN2xMHHowuKE8gQxBBwiZBPRE6iVbgdACYi46xZAz7uE7RApxPTaFYxujPuNVIOpNmECtbzNyPJT6nQmXDqmP1db4xstZA2JhZB8RWTOWfBWGQRsXMPLDTkyZAgIeFZAYOsVGYCJ2RtcLW7Ct4LQmJnDX"
audio_url = "https://dl.espressif.com/dl/audio/ff-16b-2c-44100hz.mp3"
VERIFY_TOKEN="EAAh5gkR5E70BOZBUYBiVYeyOICETbTqs87ZCRWoVotc6VZA4ebZBJYgrhRoF8h9Ghq43MErZCLPl1toZCWLv4Nkq85Yb8n7zwZBH8IAlEbFkcONDZBZB8DYkiWA4s55bfiMMxo9ifnnEbOSZBP53StGQw4IJPOR7Fn6RrH9yb0bOt262cf2ZAmp1vnsF6b88noKf6tU5Wh7IFmPoTlSoV6dVTMIhJVyYdUZCyKhbgExPHQH1S2P6"

@app.route('/', methods=['GET'])
def verify_webhook():
    """Handles the webhook verification request from WhatsApp"""
    # Get the 'hub.mode', 'hub.challenge', and 'hub.verify_token' from the query parameters
    mode = request.args.get('hub.mode')
    challenge = request.args.get('hub.challenge')
    token = request.args.get('hub.verify_token')

    # Check if the verify token matches
    if token == VERIFY_TOKEN:
        # If the token is valid, return the challenge to complete the verification
        return str(challenge), 200
    else:
        # If the token doesn't match, return an error response
        return 'Verification failed', 403


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Received webhook data:", data)

    # Loop through the messages and handle based on message type
    try:
        messages = data['entry'][0]['changes'][0]['value']['messages']

        for message in messages:
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

    # Respond with the same text
    send_text_message(to_number, text_body)


def handle_media_message(message, media_type, to_number):
    """Function to handle media messages and send a media response"""
    media_url = message[media_type]['url']
    media_id = message[media_type]['id']
    mime_type = message[media_type]['mime_type']
    print(f"Received {media_type} message: {media_url}, MIME Type: {mime_type}")

    # Respond with the same media (re-use the media URL)
    send_media_message(to_number, media_type, media_url, mime_type)


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


def send_media_message(to_number, media_type, media_url, mime_type):
    """Send a media message (image, video, etc.) back to the user"""
    response_data = {
        "to": to_number,
        "messaging_product": "whatsapp",
        "messages": [
            {
                "type": media_type,
                media_type: {
                    "url": media_url,
                    "mime_type": mime_type
                }
            }
        ]
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5151)

