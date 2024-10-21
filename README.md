# English Oral Practice: LLaMA Voice Chat

[![Python Version](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10-blue)](https://www.python.org/)

Alpha: 0.2

A local Flask application designed to help users practice and improve their English oral language skills through conversational roleplays with an AI assistant. The app utilizes models like Whisper, Piper, and LLaMA for speech recognition, text-to-speech, and interactive conversations.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Roles and Scenarios](#roles-and-scenarios)
- [Customization](#customization)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Speech Recognition**: Use your microphone to input text, practicing pronunciation and oral language skills.
- **AI-Driven Conversations**: Engage in realistic conversations with an AI assistant that adapts to various roles and scenarios.
- **Grammar Feedback**: Receive instant grammar feedback after each response, helping you learn and improve.
- **Text-to-Speech**: Hear the AI's responses spoken aloud for a more immersive learning experience.
- **Roleplay Scenarios**: Choose from pre-set roleplays or create your own custom scenario.

## Prerequisites

- Python (3.8, 3.9, or 3.10)
- Virtualenv
- A modern web browser (Chrome, Firefox, Safari, etc.)
- Piper
- whisper.cpp executable
- Local LLM with OpenAI compatible endpoint
- ffmpeg

## Installation

1. Clone this repository:

```bash
git clone https://github.com/hamletlg/english-oral-practice.git
cd english-oral-practice
```

2. Create and activate a virtual environment:

```bash
virtualenv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:

```bash
pip install -r requirements.txt
```

4. Download whisper.cpp executable and suitable model. Refer to [official whisper.cpp repository](https://github.com/ggerganov/whisper.cpp)

5. Setup local LLM model endpoint.

6. Run the Flask application:

```bash
python app.py
```

## Usage

1. Open your web browser and navigate to `http://127.0.0.1:5000/`.
2. Select a roleplay scenario or create a custom one.
3. Follow the on-screen instructions to engage in a conversational roleplay with the AI assistant.

## Roles and Scenarios

- Restaurant
- Shopping
- Clinic (Dental appointment)
- Car Rental
- Custom (User-defined scenario)
- Free Conversation (General chat)

## Customization

Create or modify scenarios by editing the `ConfigRoles.json` file. Add, remove, or update roles and their respective system roles to adapt the app to your learning needs.

## Contributing

Contributions are welcome! If you encounter any issues, have suggestions, or want to add new features, please submit an issue or pull request.

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make changes and write tests if applicable.
4. Submit a pull request describing your changes.

## License

English Oral Practice: LLaMA Voice Chat is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright © 2024 [hamletlg]
