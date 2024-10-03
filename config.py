import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'another-secret-key'

    # Model paths
    WHISPER_MODEL_PATH = '/home/hamlet/INSTALADORES/whisper.cpp/models/ggml-model-whisper-medium.en-q5_0.bin'
    LLAMA_MODEL_PATH = '/home/hamlet/INSTALADORES/LLM-MODELS/hugging-quants/Llama-3.2-3B-Instruct-Q8_0-GGUF'

    # Piper session file path
    PIPER_SESSION_FILE = '/home/hamlet/INSTALADORES/piper/my-session-file'

    # Output and input text files for piper
    OUTPUT_TEXT_FILE = 'output.txt'
    INPUT_TEXT_FILE = 'input.txt'

    API_URL = "http://localhost:1234/v1/chat/completions"
    HEADERS = {"Content-Type": "application/json"}

