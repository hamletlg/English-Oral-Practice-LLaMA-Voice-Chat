document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('send-message').onclick = sendMessage;
});

function sendMessage() {
    const input = document.getElementById('user-input');
    const userMessage = input.value;
    
    if (userMessage) {
        // Add the user's message first
        const messagesContainer = document.getElementById('messages'); 
        messagesContainer.innerHTML += `<div class="user-message">${userMessage}</div>`;
        fetch('/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: userMessage})
        })
        .then(response => response.json())  // Parse the JSON response
        .then(data => {
            const messagesContainer = document.getElementById('messages'); 
            console.log(data); // Log the data to see what it looks like
            
            if (data && data.choices && data.choices[0] && data.choices[0].message && data.choices[0].message.content) {
                const renderedContent = marked.parse(data.choices[0].message.content);
                messagesContainer.innerHTML += `<div class="assistant-message">${renderedContent}</div>`;
            } else {
                messagesContainer.innerHTML += `<div class="assistant-message">No response from server.</div>`;
            }
            
            input.value = ''; // Clear the input field
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while sending your message.');
        });        
    }
}
