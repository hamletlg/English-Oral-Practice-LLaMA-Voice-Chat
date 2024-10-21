import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'YOUR-SECRET-KEY'
    
    # Model paths
    WHISPER_MODEL = 'YOUR-PATH/whisper.cpp/models/...'
    
    # LLM Model 
    MODEL_NAME = "publisher/repo/DeepSeek-Coder-V2-Lite-Instruct-Q4_K_M.gguf"

    # Default Role System
    ROLE_SYSTEM = "You are a helpful assistant"

    # MODEL_TEMP
    MODEL_TEMP = 0.7

    # Piper MODEL session file path
    PIPER_MODEL = 'YOUR-PATH//piper/models-piper/en_US-lessac-medium.onnx'

    # Output and input text files for piper
    OUTPUT_TEXT_FILE = 'output.txt'
    INPUT_TEXT_FILE = 'input.txt'

    # Executables
    WHISPER_EXECUTABLE = 'YOUR-PATH/whisper.cpp/main'

    # LLM local server endpoint. 
    API_URL = "http://localhost:1234/v1/chat/completions"
    HEADERS = {"Content-Type": "application/json"}

    UPLOAD_FOLDER = os.getcwd() + '/uploads'
    RESPONSES_FOLDER = os.getcwd() + '/responses'

    ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg'}

    CONVERSATION_FILE = 'conversation.json'

