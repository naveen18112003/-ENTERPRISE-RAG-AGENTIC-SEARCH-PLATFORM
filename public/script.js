document.addEventListener('DOMContentLoaded', () => {
    const chatArea = document.getElementById('chat-area');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const typingIndicator = document.getElementById('typing-indicator');

    function scrollToBottom() {
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    function addMessage(text, type, sources = []) {
        // Remove typing indicator temporarily to append message
        chatArea.removeChild(typingIndicator);

        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', type);
        msgDiv.textContent = text;

        if (sources && sources.length > 0) {
            const sourceDiv = document.createElement('div');
            sourceDiv.classList.add('sources');
            // Deduplicate sources
            const uniqueSources = [...new Set(sources)];
            sourceDiv.textContent = "Sources: " + uniqueSources.join(", ");
            msgDiv.appendChild(sourceDiv);
        }

        chatArea.appendChild(msgDiv);

        // Add typing indicator back at the bottom
        chatArea.appendChild(typingIndicator);

        scrollToBottom();
    }

    function showTyping() {
        typingIndicator.style.display = 'flex';
        scrollToBottom();
    }

    function hideTyping() {
        typingIndicator.style.display = 'none';
    }

    async function handleSend() {
        const query = userInput.value.trim();
        if (!query) return;

        // Add user message
        addMessage(query, 'user');
        userInput.value = '';

        // Show typing
        showTyping();

        try {
            // Determine API URL: Use localhost:8000 if we are on localhost (dev mode), otherwise relative path (prod/Vercel)
            const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
            const apiUrl = isLocal ? 'http://localhost:8000/query' : '/api/query';

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query })
            });

            const data = await response.json();

            hideTyping();

            if (data.answer) {
                // The API might return sources in 'retrieved_docs' or 'sources' depending on our implementation
                // Based on previous step, I should align api/index.py to return standard format
                const sources = data.sources || data.retrieved_docs || [];
                addMessage(data.answer, 'bot', sources);
            } else {
                addMessage("Sorry, I encountered an error.", 'bot');
            }

        } catch (error) {
            hideTyping();
            console.error('Error:', error);
            addMessage("Error connecting to the server.", 'bot');
        }
    }

    sendBtn.addEventListener('click', handleSend);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });

    // Upload Logic
    const uploadBtn = document.getElementById('upload-btn');
    const fileInput = document.getElementById('file-input');

    uploadBtn.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        addMessage(`Uploading ${file.name}...`, 'bot');

        const formData = new FormData();
        formData.append('file', file);

        try {
            // Determine API URL
            const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
            const apiUrl = isLocal ? 'http://localhost:8000/upload' : '/api/upload';

            const response = await fetch(apiUrl, {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (response.ok) {
                addMessage(data.message, 'bot');
            } else {
                addMessage(`Error: ${data.detail || 'Upload failed'}`, 'bot');
            }

        } catch (error) {
            console.error(error);
            addMessage("Error uploading file.", 'bot');
        }

        // Reset input
        fileInput.value = '';
    });
});
