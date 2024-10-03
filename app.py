from flask import Flask, request, render_template, jsonify
import requests
from config import Config 

app = Flask(__name__, template_folder='templates')

API_URL = Config.API_URL
HEADERS = Config.HEADERS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    data = {
        "model": "publisher/repo/DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf",
        "messages": [
            {"role": "system", "content": "You are helpful assistant"},
            {"role": "user", "content": user_input}
        ],
        "temperature": 0.7,
        "max_tokens": -1,
    }
    response = requests.post(API_URL, headers=HEADERS, json=data)
    return jsonify(response.json())

