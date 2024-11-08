function scrollToBottom() {
    const messageContainer = document.getElementById('messageContainer');
    messageContainer.scrollTop = messageContainer.scrollHeight;
}

function formatTimestamp() {
    const now = new Date();
    return now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });
}

function appendMessage(content, isUser) {
    const messageContainer = document.getElementById('messageContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;

    const timestamp = document.createElement('div');
    timestamp.className = 'timestamp';
    timestamp.textContent = formatTimestamp();

    messageDiv.innerHTML = content;
    messageDiv.appendChild(timestamp);

    messageContainer.appendChild(messageDiv);
    scrollToBottom();
}

function sendMessage() {
    const messageInput = document.getElementById('messageInput');
    const message = messageInput.value.trim();

    if (message) {
        // Add user message
        appendMessage(message, true);

        // Create AI response container
        const aiMessage = document.createElement('div');
        aiMessage.className = 'message ai-message';
        messageContainer.appendChild(aiMessage);

        // Stream AI response
        const eventSource = new EventSource(`/chat/generate-completion/${encodeURIComponent(message)}/`);

        eventSource.onmessage = function(e) {
            aiMessage.innerHTML += e.data;

            // Add timestamp if it doesn't exist
            if (!aiMessage.querySelector('.timestamp')) {
                const timestamp = document.createElement('div');
                timestamp.className = 'timestamp';
                timestamp.textContent = formatTimestamp();
                aiMessage.appendChild(timestamp);
            }

            scrollToBottom();
        };

        eventSource.onerror = function() {
            eventSource.close();
            scrollToBottom();
        };

        messageInput.value = '';
    }
}

// Send message on Enter key
document.getElementById('messageInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Scroll to bottom on page load
window.onload = function() {
    scrollToBottom();
};