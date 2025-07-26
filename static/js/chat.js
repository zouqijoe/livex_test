// Simple chat implementation with conversation history
let chatMessages = null;
let messageInput = null;
let sendButton = null;
let isTyping = false;
let userEmail = null; // Store user's email
let conversationHistory = [
    {
        role: 'system',
        content: `You are a helpful assistant that helps users book meetings and manage their calendar through Cal.com.\nYou can help users:\n- Book new meetings by asking for details like date, time, and reason\n- Show scheduled events for a user\n- Cancel events\n- Reschedule events\n- Create new event types when they don't exist\n\nIMPORTANT:\n- Only ask for the user's email if they haven't already provided it in the current conversation. If they have already shared their email, remember it and use it for subsequent requests.\n- Always use American date format (MM/DD/YYYY) when discussing dates with users. For example: 10/02/2025 for October 2nd, 2025.\n- When calling functions that require dates, convert American format to ISO format (YYYY-MM-DD) for the API.\n- If a user wants to book a meeting but no suitable event type exists, offer to create one for them.\nBe friendly and helpful in your responses.`
    }
];

function initializeChat() {
    chatMessages = document.getElementById('chatMessages');
    messageInput = document.getElementById('messageInput');
    sendButton = document.getElementById('sendButton');
    if (!chatMessages || !messageInput || !sendButton) return;
    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    messageInput.addEventListener('input', function() {
        sendButton.disabled = messageInput.value.trim() === '';
    });
}

function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || isTyping) return;
    
    // Extract email from user message if not already stored
    if (!userEmail) {
        const emailMatch = message.match(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/);
        if (emailMatch) {
            userEmail = emailMatch[0];
            console.log('Extracted email:', userEmail);
        }
    }
    
    addMessageToChat(message, 'user');
    conversationHistory.push({ role: 'user', content: message });
    messageInput.value = '';
    sendButton.disabled = true;
    showTypingIndicator();
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            message: message,
            user_email: userEmail, // Send stored email
            history: conversationHistory
        })
    })
    .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
    })
    .then(data => {
        hideTypingIndicator();
        addMessageToChat(data.response, 'bot');
        conversationHistory.push({ role: 'assistant', content: data.response });
    })
    .catch(error => {
        hideTypingIndicator();
        addMessageToChat('Sorry, I encountered an error. Please try again.', 'bot');
    });
}

function addMessageToChat(content, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.style.display = 'flex';
    messageDiv.style.marginBottom = '15px';
    messageDiv.style.animation = 'fadeIn 0.3s ease-in';
    messageDiv.style.justifyContent = sender === 'user' ? 'flex-end' : 'flex-start';
    const messageContent = document.createElement('div');
    messageContent.style.maxWidth = '70%';
    messageContent.style.padding = '15px 20px';
    messageContent.style.borderRadius = '20px';
    messageContent.style.wordWrap = 'break-word';
    messageContent.style.minHeight = '20px';
    messageContent.style.display = 'block';
    if (sender === 'user') {
        messageContent.style.background = 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)';
        messageContent.style.color = 'white';
        messageContent.style.borderBottomRightRadius = '5px';
    } else {
        messageContent.style.background = 'white';
        messageContent.style.color = '#333';
        messageContent.style.border = '1px solid #e9ecef';
        messageContent.style.borderBottomLeftRadius = '5px';
        messageContent.style.boxShadow = '0 2px 10px rgba(0, 0, 0, 0.1)';
        const icon = document.createElement('i');
        icon.className = 'fas fa-robot';
        icon.style.marginRight = '8px';
        icon.style.fontSize = '16px';
        messageContent.appendChild(icon);
    }
    const textDiv = document.createElement('div');
    textDiv.textContent = content;
    textDiv.style.lineHeight = '1.5';
    messageContent.appendChild(textDiv);
    messageDiv.appendChild(messageContent);
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    isTyping = true;
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typingIndicator';
    typingDiv.style.display = 'flex';
    typingDiv.style.justifyContent = 'flex-start';
    typingDiv.style.marginBottom = '15px';
    const content = document.createElement('div');
    content.style.display = 'flex';
    content.style.alignItems = 'center';
    content.style.gap = '10px';
    content.style.padding = '15px 20px';
    content.style.background = 'white';
    content.style.borderRadius = '20px';
    content.style.border = '1px solid #e9ecef';
    content.style.maxWidth = '70%';
    const icon = document.createElement('i');
    icon.className = 'fas fa-robot';
    content.appendChild(icon);
    const text = document.createElement('span');
    text.textContent = 'Typing...';
    content.appendChild(text);
    const dots = document.createElement('div');
    dots.style.display = 'flex';
    dots.style.gap = '5px';
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.style.width = '8px';
        dot.style.height = '8px';
        dot.style.borderRadius = '50%';
        dot.style.background = '#667eea';
        dot.style.animation = 'typing 1.4s infinite ease-in-out';
        dot.style.animationDelay = `${i * 0.16}s`;
        dots.appendChild(dot);
    }
    content.appendChild(dots);
    typingDiv.appendChild(content);
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function hideTypingIndicator() {
    isTyping = false;
    const typingIndicator = document.getElementById('typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

function sendQuickMessage(message) {
    if (messageInput) {
        messageInput.value = message;
        sendMessage();
    }
}

document.addEventListener('DOMContentLoaded', function() {
    setTimeout(initializeChat, 100);
}); 