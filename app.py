import json
import os
from flask import Flask, render_template, request, jsonify, send_file, session
from flask_cors import CORS
import logging
import markdown2
from config import Config
#from scenarios.predefined_scenarios import get_scenarios
from llm.llm_handler import get_llm_response, process_conversation


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.secret_key = Config.SECRET_KEY

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    transcription = process_conversation(file)
    return jsonify({'transcription': transcription})

@app.route('/get-llm-response', methods=['POST'])
def get_llm_response_route():
    data = request.get_json()
    prompt = data.get('transcription', '')
    system_role = session.get('system_role', Config.ROLE_SYSTEM)
    llm_response, grammar, tts_audio_file = get_llm_response(prompt, system_role)
    logger.info(f"tts_audio_path: {tts_audio_file}")
    return jsonify({
        'response': llm_response,
        'grammar': grammar,
        'audio': '/responses/' + tts_audio_file
    })

@app.route('/responses/<path:filename>', methods=['GET'])
def stream_audio(filename):
    filepath = os.path.join(Config.RESPONSES_FOLDER, filename)
    return send_file(filepath, mimetype='audio/wav')


@app.route('/delete-audio/<filename>', methods=['DELETE'])
def delete_audio(filename):
    filepath = os.path.join(Config.RESPONSES_FOLDER, filename)
    
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            logger.info(f"Deleted audio file: {filename}")
            return jsonify({'success': True}), 200
        except Exception as e:
            logger.error(f"Error deleting audio file: {e}")
            return jsonify({'error': 'Failed to delete the audio file'}), 500
    else:
        return jsonify({'error': 'Audio file not found'}), 404
    

@app.route('/new-conversation', methods=['POST'])
def new_conversation():
    # Clear any existing conversation data if necessary
    if os.path.exists(Config.CONVERSATION_FILE):
        os.remove(Config.CONVERSATION_FILE)
    
    return jsonify({'status': 'success'}), 200

@app.route('/role-play')
def roleplay():
    roles_images = {
        "restaurant": "card-restaurant.jpg",
        "shopping": "card-shopping.jpg",
        "clinic": "card-clinic.jpg",
        "car-rental": "card-rental.jpg",
        "custom": "card-custom.jpg",
        "free": "card-free.jpg"
    }
    role = request.args.get('role', 'default') 
    image_name = roles_images.get(role)
    with open('ConfigRoles.json', 'r') as file:
        data = json.load(file)
    system_role = data[role]
    presentation_html = markdown2.markdown(system_role.get('presentation', '')).replace("\n", "<br>")
    logger.info(f"presentation: {presentation_html}")
    session['system_role'] = system_role['system-role'] 
    return render_template('free_chat.html', presentation=presentation_html, image=image_name)


@app.route('/free-chat')
def free_chat():
    return render_template('free_chat.html')


if __name__ == '__main__':
    app.run(debug=True)
