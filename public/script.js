document.addEventListener('DOMContentLoaded', () => {
    const chatArea = document.getElementById('chat-area');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const typingIndicator = document.getElementById('typing-indicator');

    function scrollToBottom() {
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    function removeWelcomeMessage() {
        const welcomeMsg = chatArea.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.remove();
        }
    }

    function addMessage(text, type, sources = [], isMarkdown = false) {
        // Remove welcome message on first message
        removeWelcomeMessage();
        
        // Remove typing indicator temporarily to append message
        if (chatArea.contains(typingIndicator)) {
            chatArea.removeChild(typingIndicator);
        }

        const msgDiv = document.createElement('div');
        msgDiv.classList.add('message', type);
        
        if (isMarkdown) {
            // Simple markdown rendering for agentic responses
            let html = text
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/\n/g, '<br>');
            msgDiv.innerHTML = html;
        } else {
            msgDiv.textContent = text;
        }

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
        removeWelcomeMessage();
        typingIndicator.style.display = 'flex';
        typingIndicator.classList.add('show');
        scrollToBottom();
    }

    function hideTyping() {
        typingIndicator.style.display = 'none';
        typingIndicator.classList.remove('show');
    }

    // Mode selector tabs
    const modeTabs = document.querySelectorAll('.mode-tab');
    let currentMode = 'agentic'; // Default mode
    
    modeTabs.forEach(tab => {
        tab.addEventListener('click', () => {
            // Remove active class from all tabs
            modeTabs.forEach(t => t.classList.remove('active'));
            // Add active class to clicked tab
            tab.classList.add('active');
            currentMode = tab.dataset.mode;
        });
    });

    async function handleSend() {
        const query = userInput.value.trim();
        if (!query) return;

        // Get selected mode
        const mode = currentMode;

        // Add user message
        addMessage(query, 'user');
        userInput.value = '';

        // Show typing
        showTyping();

        try {
            // Determine API URL: Use localhost:8000 if we are on localhost (dev mode), otherwise relative path (prod/Vercel)
            const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
            const apiUrl = isLocal ? 'http://localhost:8000/search' : '/api/search';

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ query: query, mode: mode })
            });

            const data = await response.json();

            hideTyping();

            if (data.answer) {
                // Handle agentic mode response with agent plan and actions
                if (data.mode === 'agentic' && (data.agent_plan || data.actions_taken)) {
                    // Build enhanced answer for agentic mode
                    let answerText = '';
                    
                    // Add mode indicator
                    answerText += `🤖 **AGENTIC SEARCH MODE**\n\n`;
                    
                    // Add intent badge
                    if (data.intent) {
                        const intentMap = {
                            'compare': '🔀 COMPARISON',
                            'lookup': '🔍 LOOKUP',
                            'summarize': '📋 SUMMARIZE',
                            'analyze': '🔬 ANALYZE'
                        };
                        const intentBadge = intentMap[data.intent] || `🔍 ${data.intent.toUpperCase()}`;
                        answerText += `**Intent:** ${intentBadge}\n\n`;
                    }
                    
                    // Add agent plan
                    if (data.agent_plan) {
                        answerText += `**Agent Plan:**\n`;
                        answerText += `• Strategy: ${data.agent_plan.strategy}\n`;
                        if (data.agent_plan.search_queries && data.agent_plan.search_queries.length > 0) {
                            answerText += `• Search Queries: ${data.agent_plan.search_queries.join(', ')}\n`;
                        }
                        answerText += `\n`;
                    }
                    
                    // Add actions taken
                    if (data.actions_taken && data.actions_taken.length > 0) {
                        answerText += `**Actions Taken:**\n`;
                        data.actions_taken.forEach((action, idx) => {
                            answerText += `${idx + 1}. ${action}\n`;
                        });
                        answerText += `\n`;
                    }
                    
                    // Add evidence
                    if (data.evidence && data.evidence.length > 0) {
                        answerText += `**Evidence:** (${data.evidence.length} source(s))\n`;
                        data.evidence.slice(0, 2).forEach((ev, idx) => {
                            answerText += `${idx + 1}. ${ev.source}\n`;
                        });
                        answerText += `\n`;
                    }
                    
                    // Add confidence if available
                    if (data.confidence) {
                        answerText += `**Confidence:** ${(data.confidence * 100).toFixed(0)}%\n\n`;
                    }
                    
                    // Add separator
                    answerText += `---\n\n`;
                    
                    // Add the actual answer
                    answerText += `**Answer:**\n${data.answer}`;
                    
                    const sources = data.sources || [];
                    addMessage(answerText, 'bot', sources, true); // true = isMarkdown
                    
                    // Show detailed info in console for debugging/demo
                    console.log('🤖 Agentic Search Details:');
                    console.log('Mode:', data.mode);
                    console.log('Intent:', data.intent);
                    console.log('Agent Plan:', data.agent_plan);
                    console.log('Actions Taken:', data.actions_taken);
                    console.log('Evidence:', data.evidence);
                    console.log('Confidence:', data.confidence);
                } else {
                    // Simple RAG mode
                    let answerText = `📚 **SIMPLE RAG MODE**\n\n`;
                    answerText += `**Answer:**\n${data.answer}`;
                    const sources = data.sources || data.retrieved_docs || [];
                    addMessage(answerText, 'bot', sources, true); // true = isMarkdown
                }
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
