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
            startRecording();
        } else {
            stopRecording();
        }
    };

    function startRecording() {
        recordButton.textContent = "Stop Recording";  
        recordButton.classList.add('recording'); 
        isRecording = true; 
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

    function stopRecording() {
        recordButton.textContent = "Start Recording";  
        recordButton.classList.remove('recording'); 
        isRecording = false;  
        mediaRecorder.stop();  

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            audioChunks = [];  
            uploadAudio(audioBlob); 
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
      // Once the audio has finished playing, send a request to delete it from the server
      audio.onended = async function() {
        const filename = audioPath.split('/').pop();  // Extract the filename from the path
        try {
            const response = await fetch(`/delete-audio/${filename}`, {
                method: 'DELETE'
            });
            if (!response.ok) {
                console.error('Failed to delete the audio file');
            } else {
                console.log('Audio file deleted successfully');
            }
        } catch (error) {
            console.error('Error deleting audio file:', error);
        }
    };
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
        messageElement.classList.add('user-message', 'bg-info', 'text-white', 'my-2', 'p-2', 'rounded');    
        messageElement.innerHTML = marked.parse(`**User:** ${text}`);        
        messageElement.classList.add('text-end');        
        messagesDiv.appendChild(messageElement);        
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
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
    

    // Function to show notifications
    /* function showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        const overlay = document.getElementById('flash-overlay');
    
        // Set the notification message and type
        notification.textContent = message;
        notification.className = `flash ${type}`;
    
        // Show the notification and overlay by setting display and triggering opacity transition
        overlay.style.display = 'block';
        notification.style.display = 'block';
        
        // Trigger the fade-in by setting opacity to 1
        setTimeout(() => {
            overlay.style.opacity = '1';
            notification.style.opacity = '1';
        }, 10); // Slight delay to ensure CSS transition triggers
    
        // Automatically hide the notification and overlay after 5 seconds
        setTimeout(() => {
            // Fade out by setting opacity to 0
            overlay.style.opacity = '0';
            notification.style.opacity = '0';
            
            // After the fade-out transition is done (0.5s), hide the elements completely
            setTimeout(() => {
                overlay.style.display = 'none';
                notification.style.display = 'none';
            }, 500); // Match this with the CSS transition duration (0.5s)
        }, 2000); // Show for 5 seconds
    }*/

    document.getElementById('new-conversation').addEventListener('click', async () => {
        resetRecordingState();
        displayTranscription('');
        displayResponse('');
        document.getElementById('messages').innerHTML = '';
    
        try {
            const response = await fetch('/new-conversation', {
                method: 'POST'
            });
    
            if (!response.ok) {
                throw new Error('Failed to start a new conversation');
            }
        } catch (error) {
            console.error('Error starting a new conversation:', error);
            showNotification('An error occurred while starting a new conversation. Please try again.', 'error');
        }
    });

    function showNotification(message, type) {
        var notification = document.getElementById('notification');
        var flashClass = (type === 'error') ? 'alert-danger' : 'alert-success';
        notification.innerHTML = `
            <div class="alert ${flashClass} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>`;
        notification.classList.add('show');
        setTimeout(function() {
            notification.classList.remove('show');
            notification.innerHTML = ''; // Clear the message after a few seconds
        }, 5000);
    }
    
});
