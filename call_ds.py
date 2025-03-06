import requests
import json
import uvicorn
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Optional, List
from datetime import datetime
from langchain.memory import ConversationBufferMemory
from langchain.schema import AIMessage, HumanMessage
import ast

ConversationID = ""


def call_ds(message, conversation_id):
    # Headers
    headers = {
        "content-type": "application/json; charset=utf-8"
    }

    # Post request body (replace with actual data)
    post_request_body = {
        "user_id": "123",
        "message": message,
        "conversation_id": conversation_id,
        "personality": "funny"
    }

    # API URL
    # TARGET_SERVICE_HOST_NAME = "http://localhost:8000/chat"
    # Make API Call
    print(f"call_ds post_request_body: {post_request_body}")
    # chat_input = ChatInput {
    #     user_id: str
    # message: str
    # conversation_id: Optional[str] = None
    # personality: Optional[str] = 'normal'
    #
    # }
    response = chat_endpoint(post_request_body["user_id"], post_request_body["message"],
                             post_request_body["conversation_id"], post_request_body["personality"])
    print(f"call_ds response: {response}")
    return json.loads(response.text)


app = FastAPI(title="Bedrock LLM Chatbot with Memory & Intelligent State")

# Store conversation memory per user session
conversations: Dict[str, ConversationBufferMemory] = {}

# Bedrock LLM API details
BEDROCK_API_URL = "https://bedrock.llm.in-west.swig.gy/chat/completions"
BEDROCK_API_KEY = "sk-kVV4BbEyB4iK-Bb2Ngb7bw"


class ChatInput(BaseModel):
    user_id: str
    message: str
    conversation_id: Optional[str] = None
    personality: Optional[str] = 'normal'  # New field to define agent personality


class ChatResponse(BaseModel):
    conversation_id: str
    response: str
    state: str  # New field to show conversation state
    search_query: Optional[List[str]] = None  # Optional search query suggestions


def get_or_create_memory(conversation_id: str) -> ConversationBufferMemory:
    """Retrieve or create a new memory buffer for a given conversation ID."""
    if conversation_id not in conversations:
        conversations[conversation_id] = ConversationBufferMemory(return_messages=True)
    print(f"get_or_create_memory conversations: {conversations}")
    return conversations[conversation_id]


def format_messages_for_bedrock(messages: List) -> List[Dict[str, str]]:
    """Convert LangChain messages into Bedrock API format."""
    formatted_messages = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            role = "user"
        elif isinstance(msg, AIMessage):
            role = "assistant"
        else:
            continue  # Ignore unknown message types

        formatted_messages.append({"role": role, "content": msg.content})
    return formatted_messages


# Update the query_bedrock_llm function to include personality

def query_bedrock_llm(messages: List[Dict[str, str]], personality: str = 'normal') -> str:
    """Query Bedrock LLM API with conversation history and personality."""
    headers = {
        "Authorization": f"Bearer {BEDROCK_API_KEY}",
        "Content-Type": "application/json"
    }

    system_message = "You are a concise assistant. Prioritize brevity and focus primarily on the most recent message."
    if personality == 'funny':
        system_message += " Your responses should be humorous and witty."
    else:
        system_message += " Maintain a professional and normal conversational tone."

    payload = {
        "model": "bedrock-claude-3-5-sonnet",
        "messages": [{"role": "system", "content": system_message}] + messages
    }

    try:
        response = requests.post(BEDROCK_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Bedrock API: {str(e)}"


def define_state(conversation_history: List[Dict[str, str]]) -> str:
    """
    Calls the LLM to determine if the conversation is in a state where food recommendations are needed.
    Forces the response to either:
    - "search" → If food recommendations should be made.
    - "non-search" → If the conversation is general.
    """
    headers = {
        "Authorization": f"Bearer {BEDROCK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "bedrock-claude-3-5-sonnet",
        "messages": [
            {"role": "system",
             "content": "You are a strict classifier. You must return ONLY 'search' or 'chatting'. No extra text."},
            {"role": "user", "content": "Here is the chat history:\n" + str(
                conversation_history) + "\n\nDetermine the state: ONLY return 'search' if food recommendations are needed, else return 'chatting'. Stress heavily on the most recent messagein the chat history"}
        ]
    }

    try:
        print(f"hitting BEDROCK_API_URL for headers: {headers}, payload: {payload}")
        response = requests.post(BEDROCK_API_URL, headers=headers, json=payload)
        print(f"BEDROCK_API_URL response: {response}")
        response.raise_for_status()
        result = response.json().get("choices", [{}])[0].get("message", {}).get("content", "").strip().lower()
        print(result)
        return "searching_food" if "search" in result else "chatting"
    except requests.exceptions.RequestException as e:
        print(f"BEDROCK_API_URL error, response: {e}")
        return "chatting"


def get_food_keywords(description, veg_preference):
    """Calls the Bedrock API to extract food search keywords and ensures they are from a predefined set."""

    BASIC_DISHES = {
        "Appam", "Bath", "Biryani", "Blueberry Smoothie", "Bonda", "Brownie", "Burgers", "Burrito", "Buttermilk",
        "Cakes", "Cheese Garlic Bread", "Cheesecake", "Chicken Biryani", "Chicken Butter Masala", "Chicken Chowmien",
        "Chicken Manchurian", "Chilli Paneer", "Chilli Potato", "Chinese", "Chocolate Icecream", "Chocolate Mousse",
        "Chole Bhature", "Crispy Corn", "Croissant", "Curd Rice", "Cutlet", "Dal Khichdi", "Dal Makhani", "Dessert",
        "Dhokla", "Dosa", "Fish Curry", "Fish Fry", "French Fries", "Fried Rice", "Gulab Jamun", "Haleem",
        "Hot and sour vegetable soup", "Hot chocolate", "Hot Coffee", "Hummus", "Ice Cream", "Idiyappam", "Idli",
        "Indian Snacks", "Indian Thali", "Jalebi", "Juice", "Kachori", "Kanafeh", "Kebabs", "Khandvi", "Khao Suey",
        "Khichdi", "Kombucha", "Lasagna", "Lassi", "Mac And Cheese", "Maggi", "Manchurian", "Milk Tea", "Momos",
        "Mousse", "Mutton Curry", "Nachos", "Noodles", "North Indian", "Nuggets", "Omelette", "Orange Juice",
        "Pakoda", "Pancakes", "Paneer Butter Masala", "Pani Puri", "Paniyaram", "Paratha", "Parotta", "Pasta",
        "Pastry", "Patty", "Pav Bhaji", "Pesarattu", "Pizzas", "Poha", "Pongal", "Poori", "Pothichoru", "Pulao",
        "Punugulu", "Pure Veg", "Puttu", "Quesadilla", "Rasgulla", "Rasmalai", "Risotto", "Rolls", "Salad", "Samosa",
        "Sandwich", "Sausage", "Shake", "Shawarma", "Souffle", "South Indian", "Spaghetti", "Spring Roll", "Sushi",
        "Tacos", "Tandoori Chicken", "Thai Curry", "Thepla", "Tiramisu", "Upma", "Uthappam", "Vada", "Vada Pav",
        "Waffle"
    }

    print("User description:", description)

    url = "https://bedrock.llm.in-west.swig.gy/chat/completions"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {BEDROCK_API_KEY}'
    }
    data = {
        "model": "bedrock-claude-3-5-sonnet",
        "messages": [
            {
                "role": "user",
                "content": f"""You are a food search assistant. Extract up to 3 most popular dishes from the predefined set below:

                Predefined Dish Set: {', '.join(BASIC_DISHES)}

                Example:
                Input:
                description: italian dishes

                Output should be a simple JSON array of dish names, Example:
                ["Pizza", "Pasta", "Lasagna"]

                Input:
                description: {description}
                """
            }
        ]
    }

    response = requests.post(url, headers=headers, json=data, timeout=120)
    print("Bedrock LLM Response:", response.json())

    if response.status_code == 200:
        response_data = response.json()
        content = response_data.get('choices', [{}])[0].get('message', {}).get('content', 'No content available')

        try:
            # Extract array from response content
            start = content.find('[')
            end = content.rfind(']') + 1
            if start != -1 and end != -1:
                extracted_dishes = ast.literal_eval(content[start:end])

                # Ensure the output is a valid list and filter only allowed dishes
                if isinstance(extracted_dishes, list):
                    filtered_dishes = [dish for dish in extracted_dishes if dish in BASIC_DISHES]
                    return filtered_dishes if filtered_dishes else []
            return []
        except Exception:
            return []
    else:
        return []


def chat_endpoint(user_id_arg, message_arg, conversation_id_arg, personality_arg):
    user_id = user_id_arg
    message = message_arg
    personality = personality_arg
    conversation_id = conversation_id_arg or f"conv_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    memory = get_or_create_memory(conversation_id)
    memory.chat_memory.add_user_message(message)

    conversation_history = memory.chat_memory.messages
    print(f"conversation_history: {conversation_history}")
    formatted_history = format_messages_for_bedrock(conversation_history)
    print(f"formatted_history: {formatted_history}")

    conversation_state = define_state(formatted_history)

    search_query = []
    print(f"conversation_state: {conversation_state}")
    if conversation_state == "searching_food":
        search_query = get_food_keywords(message, "veg")
        return ChatResponse(conversation_id=conversation_id, response="", state=conversation_state,
                            search_query=search_query)

    response = query_bedrock_llm(formatted_history, personality=personality)
    print(f"query_bedrock_llm response: {response}")
    memory.chat_memory.add_ai_message(response)

    return ChatResponse(conversation_id=conversation_id, response=response, state=conversation_state,
                        search_query=search_query)
