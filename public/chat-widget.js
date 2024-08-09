document.getElementById('chat-button').addEventListener('click', function() {
    const chatWidget = document.getElementById('chat-widget');
    if (chatWidget.style.display === 'none' || chatWidget.style.display === '') {
        chatWidget.style.display = 'flex';

        // Check if the initial message has already been added
        const chatHistory = document.getElementById('chat-history');
        if (!chatHistory.hasChildNodes()) {
            addInitialMessage();
        }
    } else {
        chatWidget.style.display = 'none';
    }
});

document.getElementById('chat-input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault(); // Prevent default behavior of Enter key
        sendMessage();  // Trigger the sendMessage function on Enter key press
    }
});

document.getElementById('chat-input').addEventListener('input', function() {
    autoResizeTextarea(this); // Adjust textarea height on input
});

// Function to generate a simple session ID (or use UUID)
function generateSessionId() {
    return '_' + Math.random().toString(36).substr(2, 9);
}

// Function to get or create a session ID (stored in localStorage)
function getSessionId() {
    let sessionId = localStorage.getItem('sessionId');
    if (!sessionId) {
        sessionId = generateSessionId();
        localStorage.setItem('sessionId', sessionId);
    }
    return sessionId;
}

async function sendMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    const sessionId = getSessionId(); // Ensure this function returns a valid sessionId

    if (message) {
        addMessage('user', message);
        input.value = '';
        autoResizeTextarea(input); // Reset the height after sending

        // Show the typing indicator
        showTypingIndicator();

        try {
            // Send message to the server
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message, sessionId: sessionId }), // Send message and sessionId
            });
            const data = await response.json();

            // Hide the typing indicator
            hideTypingIndicator();

            addMessage('bot', data.response); // Use the correct key "response"
        } catch (error) {
            console.error('Error:', error);
            hideTypingIndicator();
            addMessage('bot', 'Sorry, something went wrong. Please try again.');
        }
    }
}

function addMessage(sender, text) {
    const chatHistory = document.getElementById('chat-history');
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${sender}`;
    messageElement.textContent = text;
    chatHistory.appendChild(messageElement);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

function addInitialMessage() {
    const initialMessage = "Hi! My name is Astro, and I'm NASA's AI Assistant. Please note that answers may be inaccurate or biased, so ensure the information is reviewed.";
    addMessage('bot', initialMessage);
}

function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto'; // Reset the height
    textarea.style.height = textarea.scrollHeight + 'px'; // Set the height to fit the content
}

function showTypingIndicator() {
    const chatHistory = document.getElementById('chat-history');
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.id = 'typing-indicator';
    typingIndicator.innerHTML = '<span class="dot"></span><span class="dot"></span><span class="dot"></span>';
    chatHistory.appendChild(typingIndicator);
    chatHistory.scrollTop = chatHistory.scrollHeight;
    typingIndicator.style.display = 'flex';
}

function hideTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.style.display = 'none';
        typingIndicator.remove();
    }
}
