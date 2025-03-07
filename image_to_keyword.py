import openai
import base64
import json
import requests
import re
import warnings

def encode_image(image_path):
    print("encode_image, image_path:", image_path)

    with open(image_path, 'rb') as file_data:
        return base64.b64encode(file_data.read()).decode("utf-8")

# def extract_keywords(response):
#     match = re.search(r"\[(.*?)\]", response, re.S)
#     if match:
#         array_str = "[" + match.group(1) + "]"
#         try:
#             keywords = ast.literal_eval(array_str)
#             if isinstance(keywords, list):
#                 return keywords
#         except (SyntaxError, ValueError):
#             pass
#     return []

def analyze_image(image_path):

    api_key="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"
    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }

    base64_image = encode_image(image_path)
    prompt = """you are a food expert vlogger -
                Given an image by your fans, you need to associate it with a food item in Indian context, \
                    and return one line explaining why you picked this food item in a funny Amitabh Bachchan vibe.
                Refrain from response on vulgar or politically sensitive or religious or temple images.
                Return the output in JSON format with the following keys
                {
                    food_item: Name of food item
                    reason: Amitabh Bachchan way of reasoning on how the image is connected with food item.
                }"""

    data = {
        "model": "claude-3-7-sonnet-20250219",
        "max_tokens": 512,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": base64_image
                        }
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=data, verify=False)
        response.raise_for_status()  # Raises an HTTPError for bad responses

        response_json = response.json()
        if 'content' in response_json and response_json['content']:
            content_text = response_json['content'][0]['text']
            json_match = re.search(r'```json\n(.*?)\n```', content_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                inner_json = json.loads(json_str)
                return inner_json.get('food_item', ''), inner_json.get('reason', '')

    except (requests.RequestException, json.JSONDecodeError, KeyError, IndexError):
        pass

    return '', ''  # Return empty strings for both food_item and reason in all error cases
#
# def analyze_image(image_path, api_key):
#     base64_image = encode_image(image_path)
#
#     print(f"base64_image: {base64_image}")
#     client = openai.OpenAI(api_key=api_key, base_url="http://bedrock.llm.in-west.swig.gy/")
#
#     response = client.chat.completions.create(
#         model="bedrock-claude-3-sonnet",
#         messages=[
#             {
#                 "role": "system",
#                 "content": """you are a food expert vlogger -
#                 Given an image by your fans, you need to associate it with a food item in Indian context, \
#                     and return one line explaining why you picked this food item in a funny Amitabh Bachchan vibe.
#                 Refrain from response on vulgar or politically sensitive or religious or temple images.
#                 Return the output in JSON format with the following keys
#                 {
#                     food_item: Name of food item
#                     reason: Amitabh Bachchan way of reasoning on how the image is connected with food item.
#                 }"""
#             },
#             {
#                 "role": "user",
#                 "content": [
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": f"data:image/jpeg;base64,{base64_image}"
#                         }
#                     }
#                 ]
#             }
#         ]
#     )
#
#     print(f"response.choices[0]: {response.choices[0]}")
#
#     content = response.choices[0].message.content if response.choices else ""
#     if content:
#         try:
#             data = json.loads(content)
#             food_item = data.get("food_item", "")
#             reason = data.get("reason", "")
#         except (json.JSONDecodeError, TypeError):
#             food_item = ""
#             reason = ""
#     else:
#         food_item = ""
#         reason = ""
#
#     return food_item, reason
