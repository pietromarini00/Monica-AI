from openai import OpenAI

# src/tools/chat.py

def handle_user_message(message: str) -> str:
    if "venue" in message.lower():
        return "Looking for a venue? Any specific city in mind?"
    return f"I'm here to help you plan your wedding — you said: '{message}'"