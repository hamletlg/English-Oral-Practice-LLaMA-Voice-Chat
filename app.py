import os
from flask import Flask, render_template, request, jsonify, send_file, session
from flask_cors import CORS
import logging
from config import Config
#from scenarios.predefined_scenarios import get_scenarios
from llm.llm_handler import get_llm_response, process_conversation

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
app.secret_key = 'kjnñdkfpieauhuegr8y34uhpjw4'

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
    llm_response, tts_audio_file = get_llm_response(prompt)
    logger.info(f"tts_audio_path: {tts_audio_file}")
    return jsonify({
        'response': llm_response,
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
 

@app.before_request
def clear_conversation_on_new_session():
    logger.info(f"Before request: {session['conversation_started']}")
    # Limpiar conversación al inicio de una nueva sesión
    if 'conversation_started' not in session:
        if os.path.exists(Config.CONVERSATION_FILE):
            os.remove(Config.CONVERSATION_FILE)
        session['conversation_started'] = True

if __name__ == '__main__':
    app.run(debug=True)
