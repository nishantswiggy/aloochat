import random

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
    return response


# Initialize FastAPI
app = FastAPI(title="Bedrock LLM Chatbot with Memory & Intelligent State")

# Store conversation memory per user session
conversations: Dict[str, ConversationBufferMemory] = {}

BEDROCK_API_URL = "https://api.anthropic.com/v1/messages"


# BEDROCK_API_KEY = "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"


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


    headers = {
        "x-api-key": "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",
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }

    system_message = "You are an assistant for Swiggy to help customers discover their next order. Be concise and focus primarily on the most recent message. Only respond for queries related to only food delivery. Politely decline discussing any other topic and try to veer the conversation towards food delivery"
    if personality == 'funny':
        system_message += " Your responses should be humorous and witty."
    else:
        system_message += " Maintain a professional and normal conversational tone."

    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 512,
        "system": system_message,
        "messages": messages
    }

    try:
        print("payload:", payload)
        response = requests.post(BEDROCK_API_URL, headers=headers, json=payload, verify=False)
        response.raise_for_status()
        result = response.json()
        print(result)
        # return result["choices"][0]["message"]["content"]
        return result["content"][0]["text"]
    except requests.exceptions.RequestException as e:
        return f"Error connecting to Bedrock API line 96: {str(e)}"


def define_state(conversation_history: List[Dict[str, str]]) -> str:
    """
    Calls the LLM to determine if the conversation is in a state where food recommendations are needed.
    Forces the response to either:
    - "search" → If food recommendations should be made.
    - "non-search" → If the conversation is general.
    """

    conversations = ". ".join([i['content'] for i in conversation_history])

    headers = {
        "x-api-key": "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",
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }

    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 512,
        "system": "You are a strict classifier. You must return ONLY 'search' or 'chatting'. No extra text. 'search' is the state when the user mentions some intent to order food",
        "messages": [
            {"role": "user", "content": "Here is the chat history:\n" + str(
                conversations) + "\n\nDetermine the state: ONLY return 'search' if food recommendations are needed, else return 'chatting'. Stress heavily on the most recent message in the chat history"}
        ]
    }

    try:
        print(payload, "line 119")
        response = requests.post(BEDROCK_API_URL, headers=headers, json=payload, verify=False)
        response.raise_for_status()
        result = response.json().get("content", [{}])[0].get("text", {}).strip().lower()
        print(result, "line 122")
        return "searching_food" if "search" in result else "chatting"
    except requests.exceptions.RequestException as e:
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

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": "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",
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    data = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 512,
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

    response = requests.post(url, headers=headers, json=data, verify=False)
    print("Bedrock LLM Response:", response.json())

    if response.status_code == 200:
        response_data = response.json()
        content = response_data.get('content', [{}])[0].get('text', {})

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
    formatted_history = format_messages_for_bedrock(conversation_history)

    conversation_state = define_state(formatted_history)

    search_query = []
    if conversation_state == "searching_food":
        search_query = get_food_keywords(message, "veg")
        return ChatResponse(conversation_id=conversation_id, response=random.choice(
            ["Namaskar! Main Amitabh Bachchan bol raha hoon. Khaane mein kya chalega?",
             "Aaj kya lock karein khane main?",
             "Swad anusar chunav karein! Khane mein kya pasand hai?",
             "Kaun Banega Bhukkad? Aaj kya special bane?",
             "Amitabh Bachchan bol raha hoon, aaj khaane ka shubh muhurat kya hai?",
             "Aaj ka swaad kya hoga—spicy ya sweet?",
             "Aap bataiye, khaane mein kaunsi dish superstar banegi?",
             "Swagat hai khaane ke mahotsav mein! Kya pasand karenge?",
             "Khaane ki ghooshna ho chuki hai! Aaj kya banta hai?",
             "Aaj khaane ka plan tight hai ya diet hai?",
             "Eyy macha! Biriyani na bajji? Yen order madona?",
             "Aaj kal ka diet chod de re, Vada Pav ya Misal Pav?",
             "Inniku Sapadku enna venum? Sambar saadam-a illa pizza-a?",
             "Dosa ke rice bath? Yen taste thumba hotthu?",
             "Khaayla kai venum? Idli sambar-a illa Poori masala-a?",
             "Bhookh lagi hai ya mood mein swag hai? Burger ya Pav Bhaji?",
             "Tiffin fix cheddama? Biryani leka Dosa?",
             "Ithu tea time-a? Samosa vechikiriya illa filter coffee?",
             "Khaau pyaayla kaay havay? Misal Pav ki Pithla Bhakri?"
             ]), state=conversation_state,
                            search_query=search_query)

    response = query_bedrock_llm(formatted_history, personality=personality)
    memory.chat_memory.add_ai_message(response)

    return ChatResponse(conversation_id=conversation_id, response=response, state=conversation_state,
                        search_query=search_query)
