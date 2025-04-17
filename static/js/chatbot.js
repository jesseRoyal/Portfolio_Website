document.addEventListener('DOMContentLoaded', function() {
    const toggleBtn = document.getElementById('chatbot-toggle');
    const container = document.getElementById('chatbot-container');
    const closeBtn = document.getElementById('close-chatbot');
    const sendBtn = document.getElementById('send-btn');
    const userInput = document.getElementById('user-input');
    const chatMessages = document.getElementById('chat-messages');
    
    // Sports knowledge base - enhanced with more responses
    const sportsKnowledge = {
        "hi": "Hello athlete! 🏅 What sports question can I help with today?",
        "hello": "Hey there champion! Ready to talk sports?",
        "training": "Pro tip: Always warm up for 10-15 minutes before training! Try dynamic stretches like leg swings and arm circles.",
        "nutrition": "For peak performance: 🍌 Carbs before, protein after, and hydrate constantly! Water is your best friend!",
        "basketball": "Remember BEEF for shooting: Balance, Eyes on target, Elbow straight, Follow-through! 🏀",
        "track": "Interval training improves speed! Try 400m repeats with 2min rest between. 🏃‍♂️",
        "soccer": "Practice ball control with 'keepy-uppies' daily! Start with 10 as a goal. ⚽",
        "recover": "Recovery is just as important as training! Try foam rolling and cold baths after intense sessions.",
        "coach": "Great coaches communicate clearly, demonstrate skills, and motivate consistently!",
        "default": "I'm your virtual sports coach! Ask about:\n- Training techniques\n- Sports nutrition\n- Injury prevention\n- Coaching strategies"
    };
    
    // Toggle chatbot visibility with smooth animation
    toggleBtn.addEventListener('click', () => {
        container.classList.toggle('show');
        if (container.classList.contains('show')) {
            userInput.focus();
        }
    });
    
    closeBtn.addEventListener('click', () => {
        container.classList.remove('show');
    });
    
    // Add message to chat with typing indicator
    function addMessage(text, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
        messageDiv.innerHTML = `<strong>${isUser ? 'You' : 'Coach Bot'}:</strong> ${text}`;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Process user input with enhanced matching
    function processInput() {
        const question = userInput.value.trim();
        userInput.value = '';
        
        if (question) {
            addMessage(question, true);
            
            // Show typing indicator
            const typingIndicator = document.createElement('div');
            typingIndicator.className = 'message bot-message';
            typingIndicator.innerHTML = '<strong>Coach Bot:</strong> <em>Typing...</em>';
            chatMessages.appendChild(typingIndicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Find best matching response
            const lowerQuestion = question.toLowerCase();
            let response = sportsKnowledge.default;
            
            for (const [key, value] of Object.entries(sportsKnowledge)) {
                if (lowerQuestion.includes(key)) {
                    response = value;
                    break;
                }
            }
            
            // Simulate typing delay
            setTimeout(() => {
                chatMessages.removeChild(typingIndicator);
                addMessage(response);
                
                // Auto-close after 5 messages
                if (chatMessages.children.length > 10) {
                    container.classList.remove('show');
                }
            }, 1000 + Math.random() * 1000); // Random delay between 1-2 seconds
        }
    }
    
    // Event listeners
    sendBtn.addEventListener('click', processInput);
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') processInput();
    });
    
    // Initial greeting
    setTimeout(() => {
        addMessage("Hi there! I'm your Sports Education Assistant. Ask me about training techniques, sports science, or coaching strategies!", false);
    }, 1000);
});