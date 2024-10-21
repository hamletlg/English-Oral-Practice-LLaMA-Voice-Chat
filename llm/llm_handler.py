import os
import subprocess
from flask import jsonify
import requests
import logging
import re
from config import Config
from werkzeug.utils import secure_filename
from models.conversation import load_conversation, save_conversation
from tts.tts_handler import generate_speech

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def process_conversation(audio_file):
    # Procesar el archivo de audio usando Whisper o algún otro servicio
    
    if audio_file and allowed_file(audio_file.filename):
        filename = secure_filename(audio_file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        audio_file.save(filepath)


    output_file = os.path.join(Config.UPLOAD_FOLDER, 'output.wav')
    subprocess.run(['ffmpeg', '-i', filepath, '-ar', '16000', '-ac', '1', '-c:a', 'pcm_s16le', output_file], check=True)
    
    transcription = transcribe_audio(output_file)
    # Delete the uploaded and output file after transcription
    try:
        os.remove(filepath)
        logger.info(f"Deleted temporary file: {filepath}")
    except Exception as e:
        logger.error(f"Error deleting temporary file: {e}")
    
    try:
        os.remove(output_file)
        logger.info(f"Deleted temporary file: {output_file}")
    except Exception as e:
        logger.error(f"Error deleting temporary file: {e}")

    # Load the existing conversation
    conversation = load_conversation()

    # Store the user's transcription in the conversation
    conversation.append({'role': 'user', 'content': transcription})
    save_conversation(conversation)  # Save the updated conversation to the file
    return transcription

def transcribe_audio(audio_path):
       # Run the whisper command on the processed file
        whisper_output = subprocess.run([Config.WHISPER_EXECUTABLE, '-nt', '-m', Config.WHISPER_MODEL, audio_path], capture_output=True, text=True)
        if whisper_output.returncode != 0:
            logger.error("Whisper processing failed")
            return jsonify({"error": "Whisper processing failed", "details": whisper_output.stderr}), 500        
        # Extract the text output from whisper
        user_input = whisper_output.stdout.strip()
        logger.info(f"Whisper output: {user_input}")
        return user_input

def get_llm_response(user_input, system_role):
    conversation = load_conversation()
    messages = [{'role': 'system', 'content': system_role}] + conversation
    data = {"model": Config.MODEL_NAME, "messages": messages, "temperature": Config.MODEL_TEMP}
    
    response = requests.post(Config.API_URL, json=data, headers=Config.HEADERS)
    llm_response = response.json().get('choices', [{}])[0].get('message', {}).get('content', 'No response')

    llm_role_responses = re.findall(r'<bot>(.*?)</bot>', llm_response)
    llm_grammar_responses = re.findall(r'<grammar>(.*?)</grammar>', llm_response)

    logger.info(f"llm response: {llm_role_responses}")
    
    if not llm_role_responses:
        # Handle the case where there is nothing between the <role> tags
        llm_role_responses = ['No response from the llm']
        logger.warning("No message found in LLM response")

    if not llm_grammar_responses:
        # Handle the case where there is nothing between the <role> tags
        llm_grammar_response = ['No grammar response from the llm']
        logger.warning("No grammar message found in LLM response")

    role_response = ''.join(llm_role_responses)

    # Guardar respuesta en la conversación
    conversation.append({'role': 'assistant', 'content': role_response})
    save_conversation(conversation)

    # Generar el archivo de TTS con la respuesta
    tts_audio_file = generate_speech(role_response)
    return role_response, llm_grammar_responses[0], tts_audio_file
