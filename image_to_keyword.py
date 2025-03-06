import openai
import base64
import json

def encode_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

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

def analyze_image(image_path, api_key):
    base64_image = encode_image(image_path)
    
    client = openai.OpenAI(api_key=api_key, base_url="http://bedrock.llm.in-west.swig.gy/")
    
    response = client.chat.completions.create(
        model="bedrock-claude-3-sonnet",
        messages=[
            {
                "role": "system",
                "content": """you are a food expert vlogger -
                Given an image by your fans, you need to associate it with a food item in Indian context, \
                    and return one line explaining why you picked this food item in a funny Amitabh Bachchan vibe.
                Refrain from response on vulgar or politically sensitive or religious or temple images.
                Return the output in JSON format with the following keys
                {
                    food_item: Name of food item
                    reason: Amitabh Bachchan way of reasoning on how the image is connected with food item.
                }"""
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )
    
    content = response.choices[0].message.content if response.choices else ""
    if content:
        try:
            data = json.loads(content)
            food_item = data.get("food_item", "")
            reason = data.get("reason", "")
        except (json.JSONDecodeError, TypeError):
            food_item = ""
            reason = ""
    else:
        food_item = ""
        reason = ""
    
    return food_item, reason
