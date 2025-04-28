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

    if (!Object.values(chatUI).every(element => element !== null)) {
        console.error('Chat elements missing from DOM');
        return;
    }

    function toggleChatVisibility() {
        chatUI.chatContainer.classList.toggle('show');
        if (chatUI.chatContainer.classList.contains('show')) {
            chatUI.userInputField.focus();
            scrollToBottom(true);
        }
    }

    function closeChat() {
        chatUI.chatContainer.classList.remove('show');
    }

    function scrollToBottom(instant = false) {
        const container = document.querySelector('.chat-messages-scroll-container');
        if (!container) return;
        
        // Use small timeout to ensure DOM updates are complete
        setTimeout(() => {
            container.scrollTo({
                top: container.scrollHeight,
                behavior: instant ? 'auto' : 'smooth'
            });
        }, 50);
    }

    function addMessage(text, isUserMessage = false) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${isUserMessage ? 'user-message' : 'bot-message'}`;

        const sanitizedText = text
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/\n{2,}/g, '<br><br>')
            .replace(/\n/g, '<br>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');

        const header = document.createElement('strong');
        header.className = 'message-sender';
        header.textContent = isUserMessage ? 'You' : 'Coach Bot';

        const contentContainer = document.createElement('div');
        contentContainer.className = 'message-content';
        contentContainer.innerHTML = sanitizedText;

        const timestamp = document.createElement('div');
        timestamp.className = 'message-timestamp';
        timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

        messageElement.appendChild(header);
        messageElement.appendChild(contentContainer);
        messageElement.appendChild(timestamp);

        messageElement.style.opacity = '0';
        chatUI.messageDisplay.appendChild(messageElement);
        
        setTimeout(() => {
            messageElement.style.transition = 'opacity 0.3s ease';
            messageElement.style.opacity = '1';
            scrollToBottom();
        }, 10);
    }

    async function sendMessage() {
        const userMessage = chatUI.userInputField.value.trim();
        if (!userMessage) return;

        chatUI.userInputField.disabled = true;
        chatUI.sendButton.disabled = true;
        const originalValue = chatUI.userInputField.value;
        chatUI.userInputField.value = '';

        try {
            addMessage(originalValue, true);

            const typingIndicator = document.createElement('div');
            typingIndicator.className = 'typing-indicator-container';
            typingIndicator.innerHTML = `
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            `;
            chatUI.messageDisplay.appendChild(typingIndicator);
            scrollToBottom();

            const response = await fetch('/api/chatbot', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: userMessage,
                    session_id: chatUI.sessionId
                }),
                credentials: 'include'
            });

            typingIndicator.remove();

            if (!response.ok) throw new Error(await response.text());
            
            const { success, reply } = await response.json();
            if (success) {
                reply.split(/\n\s*\n/).forEach((paragraph, i) => {
                    if (paragraph.trim()) {
                        setTimeout(() => addMessage(paragraph, false), i * 150);
                    }
                });
            } else {
                addMessage(`⚠️ ${reply}`, false);
            }
        } catch (error) {
            console.error('Chat error:', error);
            addMessage("⚠️ Couldn't connect to the server. Please try again.", false);
        } finally {
            chatUI.userInputField.disabled = false;
            chatUI.sendButton.disabled = false;
            chatUI.userInputField.focus();
        }
    }

    // Event listeners
    chatUI.toggleButton.addEventListener('click', toggleChatVisibility);
    chatUI.closeButton?.addEventListener('click', closeChat);
    chatUI.sendButton.addEventListener('click', sendMessage);
    chatUI.userInputField.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Welcome message
    setTimeout(() => {
        addMessage("Hi! I'm Coach Bot 🏀 Ask me about sports or training tips!", false);
    }, 1500);
});