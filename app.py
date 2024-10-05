import os
import subprocess
from flask import Flask, request, render_template, jsonify, send_file, flash
from flask_cors import CORS
from werkzeug.utils import secure_filename
import requests
import logging
from config import Config 

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

LLM_API_URL = Config.API_URL
HEADERS = Config.HEADERS
WHISPER_MODEL = Config.WHISPER_MODEL_PATH
WHISPER_EXECUTABLE = Config.WHISPER_EXECUTABLE
UPLOAD_FOLDER = Config.UPLOAD_FOLDER
ALLOWED_EXTENSIONS = Config.ALLOWED_EXTENSIONS
ROLE_SYSTEM = Config.ROLE_SYSTEM
MODEL_TEMP = Config.MODEL_TEMP
PIPER_MODEL = Config.PIPER_MODEL
RESPONSES_FOLDER = Config.RESPONSES_FOLDER

PIPER_VOICE_PATH = './voices/piper_voice'

MODEL_NAME = Config.MODEL_NAME

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

# Route for receiving uploaded audio and returning only the transcription
@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Process the audio file using ffmpeg
        output_file = os.path.join(UPLOAD_FOLDER,'output.wav')
        subprocess.run(['ffmpeg', '-i', filepath, '-hide_banner','-loglevel','error' ,'-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', output_file], check=True)
        logger.info(f"Processed audio saved to {output_file}")        
        
        # Transcribe using Whisper.cpp
        transcription = transcribe_audio(output_file)
        
        # Return transcription first, then LLM response will be handled separately
        return jsonify({'transcription': transcription})
    
    return jsonify({'error': 'Invalid file format'}), 400

# Route for generating LLM response based on transcription
@app.route('/get-llm-response', methods=['POST'])
def get_llm_response_route():
    data = request.get_json()
    prompt = data.get('transcription', '')
    
    if not prompt:
        return jsonify({'error': 'No transcription provided'}), 400
    
    # Send transcription to LLM
    llm_response = get_llm_response(prompt)
    
    # Generate speech using Piper    
    tts_audio_path = generate_speech(llm_response)

    # Construct the URL for the audio file
    audio_url = f"/responses/{os.path.basename(tts_audio_path)}"

    
    return jsonify({
        'response': llm_response,
         'audio': audio_url
    })

def transcribe_audio(audio_path):
        # Run the whisper command on the processed file
        whisper_output = subprocess.run([WHISPER_EXECUTABLE, '-nt', '-m', WHISPER_MODEL, audio_path], capture_output=True, text=True)
        if whisper_output.returncode != 0:
            logger.error("Whisper processing failed")
            return jsonify({"error": "Whisper processing failed", "details": whisper_output.stderr}), 500        
        # Extract the text output from whisper
        user_input = whisper_output.stdout.strip()
        logger.info(f"Whisper output: {user_input}")
        return user_input

  
def get_llm_response(user_input):
    headers = {'Content-Type': 'application/json'}
    data = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": ROLE_SYSTEM},
                {"role": "user", "content": user_input}
            ],
            "temperature": MODEL_TEMP,
            "max_tokens": -1,
        }
    response = requests.post(LLM_API_URL, json=data, headers=HEADERS)
    logger.info("Sent request to LLAMA API")
    return response.json().get('choices', [{}])[0].get('message', {}).get('content', 'No response')

def generate_speech(text):
    logger.info("Generating speech.")  
    clean_text = clean_characters_to_piper(text)  
    # Define the path for the generated TTS audio file
    tts_audio_file = os.path.join(RESPONSES_FOLDER, 'response.wav')
    # Command to pipe the text to piper via echo and generate the speech
    command = f'echo "{clean_text}" | piper --model {PIPER_MODEL} --output_file {tts_audio_file}'    
    # Run the subprocess to execute the piper command
    subprocess.run(command, shell=True, check=True)
    return tts_audio_file


# Route to stream the Piper TTS audio
@app.route('/responses/<path:filename>', methods=['GET'])
def stream_audio(filename):
    filepath = os.path.join(RESPONSES_FOLDER, filename)
    return send_file(filepath, mimetype='audio/wav')


def clean_characters_to_piper(input_string):
    # Remove asterisks, parentheses, and hyphens
    output_string = input_string.replace('*', '') \
                                 .replace('(', '') \
                                 .replace(')', '') \
                                 .replace('-', '') \
                                 .replace('$', '')
    return output_string

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
