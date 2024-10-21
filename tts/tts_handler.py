import os
import subprocess
import uuid
from config import Config

def generate_speech(text):
    clean_text = clean_characters_to_piper(text)
    unique_filename = f"{uuid.uuid4()}.wav"
    tts_audio_file = os.path.join(Config.RESPONSES_FOLDER, unique_filename)
    
    command = f'echo "{clean_text}" | piper --model {Config.PIPER_MODEL} --output_file {tts_audio_file}'
    subprocess.run(command, shell=True, check=True)
    
    return unique_filename

def clean_characters_to_piper(text):
    return text.replace('*', '').replace('(', '').replace(')', '').replace('-', '')


