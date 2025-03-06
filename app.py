from flask import Flask, jsonify
# from pyngrok import ngrok, conf
import json
import requests
# conf.get_default().verify_ssl = False
# Add this line before connecting
# ngrok.set_auth_token("2twNTpr5zG3U0ckMbzhUwg0acHA_388Ufsb8ZR56f38NyUsS3")

class AudioMessage:
    def __init__(self, to, audio_url):
        self.messaging_product = "whatsapp"
        self.to = to
        self.type = "audio"
        self.audio = {"link": audio_url}

    def to_json(self):
        return {
            "messaging_product": self.messaging_product,
            "to": self.to,
            "type": self.type,
            "audio": self.audio
        }


class ImageMessage:
    def __init__(self, to, image_url):
        self.messaging_product = "whatsapp"
        self.to = to
        self.type = "image"
        self.image = {
            "link": image_url,
            "caption": "Image sent via WhatsApp API"  # Optional caption
        }

    def to_json(self):
        return {
            "messaging_product": self.messaging_product,
            "to": self.to,
            "type": self.type,
            "image": self.image
        }


def send_whatsapp_image(to: str, token: str, image_url: str):
    url = "https://graph.facebook.com/v22.0/601304399725157/messages"

    # Create message payload
    message = ImageMessage(to, image_url)

    # Set headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # Send request
    response = requests.post(
        url,
        headers=headers,
        json=message.to_json()
    )

    print("Response Status:", response.status_code)
    return response

def send_whatsapp_audio(to: str, token: str, audio_url: str):
    url = "https://graph.facebook.com/v22.0/601304399725157/messages"

    # Create message payload
    message = AudioMessage(to, audio_url)

    # Set headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # Send request
    response = requests.post(
        url,
        headers=headers,
        json=message.to_json()
    )

    print("Response Status:", response.status_code)
    return response
app = Flask(__name__)

# @app.route('/', methods=['GET'])
# def hello_world():
#     return jsonify({
#         "message": "Hello World",
#         "status": "success"
#     })
# Replace with your third-party provider's API credentials
API_URL = 'https://your-whatsapp-api-endpoint.com/send_message'
API_KEY = 'your-api-key'
PHONE_NUMBER = 'your-phone-number'

recipient = "+919041047119"
access_token = "EAAP3nUnNbEkBO8o5NZCRoBoY4DYVFnFbSJoeQyyliIeWoJF0u25ij5JlPIa5sqnLlPAgVkAujzK9gSa4gU22ZCeZB28is6ZArXWMqNR4EHaVy30EeZAXrNvOEcP3HKVSFTjEpbsM6zjSqZAMBW3w1sZCJeyH1XzSIOin1ccXEZCS3RwBZBT7IDk2mbEinDBkj05wSZAwZCbrBPodcpDuAup70Im8Ta165wUuggTHry8ZB1eF"
audio_url = "https://dl.espressif.com/dl/audio/ff-16b-2c-44100hz.mp3"



@app.route('/', methods=['GET'])
def hello_world():
    print(send_whatsapp_image(recipient, access_token, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQXRwezuhFdnNG_jsRgGo7oklndpWxkft2r9Q&s'))
    # print(send_whatsapp_audio(recipient, access_token, audio_url))
    return jsonify({
        "message": "Hello World",
        "status": "success"
    })
#
# @app.route('/webhook', methods=['POST'])
# def webhook():
#     """This is the webhook endpoint that WhatsApp messages will hit."""
#     incoming_msg = request.json.get('message', '').strip()  # Assuming a JSON payload
#
#     # Send a response based on the incoming message
#     if incoming_msg.lower() == 'hello':
#         response_msg = "Hi there! How can I help you today?"
#     elif incoming_msg.lower() == 'bye':
#         response_msg = "Goodbye! Have a great day."
#     else:
#         response_msg = f"Sorry, I don't understand: {incoming_msg}"
#
#     # Prepare the message payload to send back to WhatsApp
#     payload = {
#         'to': PHONE_NUMBER,  # The recipient's phone number
#         'message': response_msg,  # The message to send
#         'api_key': API_KEY  # Your API key for authentication
#     }
#
#     # Make an API call to the WhatsApp provider's API to send the message
#     response = requests.post(API_URL, json=payload)
#
#     if response.status_code == 200:
#         return jsonify({"status": "success"}), 200
#     else:
#         return jsonify({"status": "error", "message": response.text}), 400


if __name__ == '__main__':
    app.run(debug=True, port=5000)

