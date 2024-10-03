import requests 

@app.route('/api/user_prompt', methods=['POST'])
def generate_user_response():
    data = request.get_json()
    prompt = data['prompt']

    # Generate user response using llamacpp
    user_response, _ = generate(prompt)

    return jsonify({'user_response': user_response})

