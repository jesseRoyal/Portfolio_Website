document.addEventListener('DOMContentLoaded', () => {
    const chatUI = {
        toggleButton: document.getElementById('chatbot-toggle'),
        chatContainer: document.getElementById('chatbot-container'),
        closeButton: document.getElementById('close-chatbot'),
        sendButton: document.getElementById('send-btn'),
        userInputField: document.getElementById('user-input'),
        messageDisplay: document.getElementById('chat-messages'),
        sessionId: 'session-' + Math.random().toString(36).substring(2, 9)
    };

    // Verify all elements exist
    if (!Object.values(chatUI).every(element => element !== null)) {
        console.error('One or more chat elements are missing from the DOM');
        return;
    }

    function toggleChatVisibility() {
        chatUI.chatContainer.classList.toggle('show');
        if (chatUI.chatContainer.classList.contains('show')) {
            chatUI.userInputField.focus();
        }
    }

    function closeChat() {
        chatUI.chatContainer.classList.remove('show');
    }

    function addMessage(text, isUserMessage = false) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${isUserMessage ? 'user-message' : 'bot-message'}`;
        const sanitizedText = text.replace(/</g, '&lt;').replace(/>/g, '&gt;');
        messageElement.innerHTML = `<strong>${isUserMessage ? 'You' : 'Coach Bot'}:</strong> ${sanitizedText}`;
        chatUI.messageDisplay.appendChild(messageElement);
        chatUI.messageDisplay.scrollTop = chatUI.messageDisplay.scrollHeight;
    }

    async function sendMessage() {
        const userMessage = chatUI.userInputField.value.trim();
        if (!userMessage) return;

        // Disable UI during processing
        chatUI.userInputField.disabled = true;
        chatUI.sendButton.disabled = true;
        chatUI.userInputField.value = '';
        addMessage(userMessage, true);

        // Create typing indicator
        const typingIndicator = document.createElement('div');
        typingIndicator.className = 'message bot-message typing';
        typingIndicator.innerHTML = '<em>Coach Bot is typing...</em>';
        chatUI.messageDisplay.appendChild(typingIndicator);

        try {
            // 1. Verify the endpoint URL is correct
            const apiUrl = '/api/chatbot'; // Make sure this matches your server route
            
            // 2. Add more detailed request logging
            console.log('Sending request to:', apiUrl, {
                message: userMessage,
                session_id: chatUI.sessionId
            });

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify({
                    message: userMessage,
                    session_id: chatUI.sessionId
                }),
                credentials: 'include' // Important for sessions/cookies
            });

            console.log('Raw response:', response);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('Server response error:', errorText);
                throw new Error(`Server error: ${response.status} - ${errorText}`);
            }

            const responseData = await response.json();
            typingIndicator.remove();

            if (responseData.success) {
                addMessage(responseData.reply, false);
            } else {
                addMessage(`⚠️ ${responseData.reply}`, false);
            }
        } catch (error) {
            console.error('Full error details:', error);
            typingIndicator.remove();
            
            let errorMessage = "⚠️ Service unavailable. Please try again later.";
            if (error.message.includes('Failed to fetch')) {
                errorMessage = "⚠️ Couldn't reach the server. Check your network.";
            } else if (error.message.includes('No internet')) {
                errorMessage = "⚠️ You're offline. Please connect to the internet.";
            }
            
            addMessage(errorMessage, false);
        } finally {
            chatUI.userInputField.disabled = false;
            chatUI.sendButton.disabled = false;
            chatUI.userInputField.focus();
        }
    }

    // Event listeners
    chatUI.toggleButton.addEventListener('click', toggleChatVisibility);
    chatUI.closeButton.addEventListener('click', closeChat);
    chatUI.sendButton.addEventListener('click', sendMessage);
    chatUI.userInputField.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    // Initial greeting
    setTimeout(() => {
        addMessage("Hi! I'm Coach Bot 🏀 Ask me about sports or training tips!", false);
    }, 1000);
});