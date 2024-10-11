import json
import os
from config import Config

def load_conversation():
    if os.path.exists(Config.CONVERSATION_FILE):
        with open(Config.CONVERSATION_FILE, 'r') as f:
            return json.load(f)
    return []

def save_conversation(conversation):
    with open(Config.CONVERSATION_FILE, 'w') as f:
        json.dump(conversation, f)
