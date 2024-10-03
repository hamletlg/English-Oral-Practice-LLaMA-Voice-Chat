from flask import Flask, request, render_template, jsonify, session
import requests
import subprocess
import os
import logging
from config import Config 

app = Flask(__name__, template_folder='templates')

API_URL = Config.API_URL
HEADERS = Config.HEADERS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Set a secret key for session management
app.secret_key = 'rhgohñoo4o4' 

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload-audio', methods=['POST'])
def upload_audio():
    if 'file' not in request.files:
        logger.error("No file part")
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.error("No selected file")
        return jsonify({"error": "No selected file"}), 400
    
    try:
        # Save the uploaded audio file temporarily
        filepath = 'temp_recording.wav'
        file.save(filepath)
        logger.info(f"Saved file to {filepath}")

        # Process the audio file using ffmpeg
        output_file = 'output.wav'
        subprocess.run(['ffmpeg', '-i', filepath, '-hide_banner','-loglevel','error' ,'-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', output_file], check=True)
        logger.info(f"Processed audio saved to {output_file}")

        # Run the whisper command on the processed file
        whisper_output = subprocess.run(['/home/hamlet/INSTALADORES/whisper.cpp/main', '-nt', '-m', '/home/hamlet/INSTALADORES/whisper.cpp/models/ggml-model-whisper-medium.en-q5_0.bin', output_file], capture_output=True, text=True)
        if whisper_output.returncode != 0:
            logger.error("Whisper processing failed")
            return jsonify({"error": "Whisper processing failed", "details": whisper_output.stderr}), 500
        
        # Extract the text output from whisper
        user_input = whisper_output.stdout.strip()
        logger.info(f"Whisper output: {user_input}")

        data = {
            "model": "publisher/repo/DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf",
            "messages": [
                {"role": "system", "content": "You are helpful English instructor."},
                {"role": "user", "content": user_input}
            ],
            "temperature": 0.7,
            "max_tokens": -1,
        }
        response = requests.post(API_URL, headers=HEADERS, json=data)
        logger.info("Sent request to API")
                
        # Save the transcribed text and assistant's response in the session
        session['transcript'] = user_input
        session['assistant_response'] = response.json().get('choices', [{}])[0].get('message', {}).get('content', 'No response')
        
 
        return jsonify(response.json())

    except subprocess.CalledProcessError as e:
        logger.error(f"Subprocess error: {e}")
        return jsonify({"error": "Processing failed", "details": str(e)}), 500

    finally:
        # Clean up temporary files
        if os.path.exists(filepath):
            os.remove(filepath)
        if os.path.exists(output_file):
            os.remove(output_file)
        logger.info("Temporary files cleaned up")

 
@app.route('/get-assistant-response', methods=['POST'])
def get_assistant_response():
    transcribed_text = session.get('transcript')
    assistant_response = session.get('assistant_response')
    
    if transcribed_text and assistant_response:
        return jsonify({"text": f"user: {transcribed_text}\nassistant: {assistant_response}"})
    else:
        return jsonify({"error": "No response available yet"}), 404

