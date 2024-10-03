document.addEventListener('DOMContentLoaded', function() {
    const recordButton = document.getElementById('send-message');
    let mediaRecorder;
    let recordedChunks = [];

    async function fetchAndDisplayMessage() {
        try {
            // Make a GET request to /get-assistant-response
            const response = await fetch('/get-assistant-response');
            
            // Check if the response is OK (status code in the range 200-299)
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            // Parse the JSON data from the response
            const data = await response.json();
            
            // Extract the user message from the data
            const userMessage = data.text;
            
            // Display the user message using the displayResponse function
            displayResponse(userMessage);
        } catch (error) {
            // Handle any errors that occur during the fetch operation
            console.error('Failed to fetch user message:', error);
        }
    }


    recordButton.onclick = function() {
        if (recordButton.textContent === 'Record') {
            // Start recording
            navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
                mediaRecorder = new MediaRecorder(stream);
                recordedChunks = [];
                mediaRecorder.ondataavailable = event => {
                    if (event.data.size > 0) {
                        recordedChunks.push(event.data);
                    }
                };
                mediaRecorder.onstop = () => {
                    const blob = new Blob(recordedChunks, { type: 'audio/wav' });
                    const formData = new FormData();
                    formData.append('file', blob, 'recording.wav');

                    fetch('/upload-audio', {
                        method: 'POST',
                        body: formData
                    }).then(response => response.json())
                      .then(data => {
                          console.log('Upload successful:', data);
                          if (data.error) {
                              displayError(data.error);
                          } else {
                              // Display the transcribed user message or any other relevant action
                              displayResponse(data.choices[0].message.content);
                          }
                      })
                      .catch(error => {
                          console.error('Error uploading file:', error);
                          displayError('Failed to upload audio file');
                      });
                };
                mediaRecorder.start();
                recordButton.textContent = 'Stop Record';
            }).catch(err => {
                console.error('The following error occurred during getUserMedia: ' + err);
                displayError('Failed to access microphone');
            });
        } else {
            // Stop recording
            if (mediaRecorder) {
                mediaRecorder.stop();
                recordButton.textContent = 'Record';
            }
        }
    };

    function displayResponse(responseText) {
        console.log(responseText);
        const messagesDiv = document.getElementById('messages');
        const messageElement = document.createElement('div');
        messageElement.innerHTML = marked.parse(responseText);
        messageElement.style.textAlign = 'left'; // Align to the right for assistant's responses
        messagesDiv.appendChild(messageElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight; // Scroll to the bottom of the chat interface
    }

    function displayError(errorText) {
        const errorElement = document.createElement('div');
        errorElement.innerHTML = marked.parse(`**Error:** ${errorText}`);
        errorElement.style.color = 'red';
        errorElement.style.textAlign = 'center'; // Center the error message
        document.getElementById('messages').appendChild(errorElement);
    }
});