import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'another-secret-key'

    # Model paths
    WHISPER_MODEL = '/home/hamlet/INSTALADORES/whisper.cpp/models/ggml-model-whisper-medium.en-q5_0.bin'
    LLAMA_MODEL_PATH = '/home/hamlet/INSTALADORES/LLM-MODELS/hugging-quants/Llama-3.2-3B-Instruct-Q8_0-GGUF'

    # Model to data json
    MODEL_NAME = "publisher/repo/DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf"

    # Role System
    ROLE_SYSTEM = "You are a helpful assistant."

    # MODEL_TEMP
    MODEL_TEMP = 0.7

    # Piper session file path
    PIPER_MODEL = '/home/hamlet/INSTALADORES/piper/models-piper/en_US-lessac-medium.onnx'

    # Output and input text files for piper
    OUTPUT_TEXT_FILE = 'output.txt'
    INPUT_TEXT_FILE = 'input.txt'

    # Executables
    WHISPER_EXECUTABLE = '/home/hamlet/INSTALADORES/whisper.cpp/main'

    API_URL = "http://localhost:1234/v1/chat/completions"
    HEADERS = {"Content-Type": "application/json"}

    UPLOAD_FOLDER = os.getcwd() + '/uploads'
    RESPONSES_FOLDER = os.getcwd() + '/responses'

    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg'}

    CONVERSATION_FILE = 'conversation.json'

