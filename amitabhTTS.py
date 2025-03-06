import requests


def get_amitabh_audio(message: str) -> bytes:
    url = "https://api.elevenlabs.io/v1/text-to-speech/OZ3qxpjeirCVj5mSbi4D?output_format=mp3_44100_128"
    headers = {
        "xi-api-key": "sk_87436592157f9b25077ae35b32994eb1fff013d057c46b2d",
        "Content-Type": "application/json"
    }
    payload = {
        "text": message,
        "model_id": "eleven_multilingual_v2"
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Error: {response.status_code}, {response.text}")

    audio_data = response.content

    # Write to a file
    with open("amit.mp3", "wb") as f:
        f.write(audio_data)

    return audio_data
