document.addEventListener('DOMContentLoaded', function () {
    const recordButton = document.getElementById('send-message');
    const chatBox = document.getElementById('messages');
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;  // State to track recording status
    let transcriptionText = '';  // Store the transcription text

    // Toggle recording on button click
    recordButton.onclick = async function () {
        if (!isRecording) {
            // Start recording
            startRecording();
        } else {
            // Stop recording
            stopRecording();
        }
    };

    // Start recording function
    function startRecording() {
        recordButton.textContent = "Stop Recording";  // Update button text
        recordButton.classList.add('recording'); // Add class for recording state
        isRecording = true;  // Update state
        showNotification('Recording... Speak now', 'success');

        // Start recording audio
        navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.start();

            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
            };
        }).catch(error => {
            console.error('Error accessing microphone: ', error);
            showNotification('Error accessing microphone', 'error')           
        });
    }

    // Stop recording function
    function stopRecording() {
        recordButton.textContent = "Start Recording";  // Reset button text
        recordButton.classList.remove('recording'); // Remove class for recording state
        isRecording = false;  // Update state
        mediaRecorder.stop();  // Stop recording

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            audioChunks = [];  // Clear chunks for the next recording
            uploadAudio(audioBlob);  // Send audio to server for processing
        };
    }

    // Function to upload audio and handle the transcription
    async function uploadAudio(audioBlob) {
        showNotification('Processing transcription...', 'success');
        const formData = new FormData();
        formData.append('file', audioBlob, 'audio.wav');    
        try {
            // Send the recorded audio to Flask
            const response = await fetch('/upload-audio', {
                method: 'POST',
                body: formData
            });
    
            // Check if the response is ok (status 200-299)
            if (!response.ok) {
                throw new Error('Failed to upload audio for transcription');
            }
    
            const data = await response.json();
    
            // Check if the response contains the transcription data
            if (!data.transcription) {
                throw new Error('Transcription data is missing');
            }
    
            // Show transcription and request LLM response
            transcriptionText = data.transcription;
            displayTranscription(transcriptionText);
    
            // Now fetch LLM response based on transcription
            await getLlmResponse(transcriptionText);
    
        } catch (error) {
            console.error('Error during audio upload and transcription:', error);
            showNotification('An error occurred during the transcription process. Please try again.', 'error');
        }
    }
    
    // Function to get LLM response based on transcription
    async function getLlmResponse(transcription) {
        showNotification('Processing assistant response...', 'success');    
        try {
            // Send the transcription to the server and request the LLM response
            const response = await fetch('/get-llm-response', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ transcription })
            });
    
            // Check if the response is ok (status 200-299)
            if (!response.ok) {
                throw new Error('Failed to fetch assistant response');
            }
    
            const data = await response.json();
    
            // Check if the response contains the necessary data (response and audio)
            if (!data.response || !data.audio) {
                throw new Error('Assistant response data is incomplete');
            }
    
            // Show LLM response and play the TTS audio
            displayResponse(data.response);
            playAudio(data.audio);
    
        } catch (error) {
            console.error('Error fetching LLM response:', error);
            showNotification('An error occurred while fetching the assistant response. Please try again.', 'error');
        }
    }

    // Function to play the streamed audio response
    function playAudio(audioPath) {
        const audio = new Audio(audioPath);
        audio.play();
    }

    // Helper function to reset recording state in case of errors
    function resetRecordingState() {
        recordButton.textContent = "Start Recording";
        isRecording = false;
        audioChunks = [];
    }

    function displayTranscription(text) {
        console.log(text);
        const messagesDiv = document.getElementById('messages');
        const messageElement = document.createElement('div');
        messageElement.classList.add('user-message')
        messageElement.innerHTML = marked.parse(`**User:** ${text}`);
        messageElement.style.textAlign = 'right'; // Align to the right for user's messages
        messagesDiv.appendChild(messageElement);
        messagesDiv.scrollTop = messagesDiv.scrollHeight; // Scroll to the bottom of the chat interface
    }

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

    // Function to show notifications
function showNotification(message, type = 'success') {
    const notification = document.getElementById('notification');
    notification.textContent = message;
    notification.className = `flash ${type}`; // Apply appropriate class based on type
    notification.style.display = 'block'; // Show the notification

    // Automatically hide the notification after a few seconds
    setTimeout(() => {
        notification.style.display = 'none';
    }, 5000);
}
});
