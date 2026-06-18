// Chat interface state variables
let activeSessionId = null;
let isDictating = false;
let ttsEnabled = false;
let recognition = null;
let renameTargetId = null;

// DOM Selectors
const chatMessagesContainer = document.getElementById('chat-messages-container');
const chatEmptyState = document.getElementById('chat-empty-state');
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const micBtn = document.getElementById('mic-btn');
const speakerBtn = document.getElementById('speaker-btn');
const activeSessionTitle = document.getElementById('active-session-title');
const renameModal = document.getElementById('rename-modal');
const renameInput = document.getElementById('rename-input');

// Initialize Web Speech APIs
initSpeechAPI();

/**
 * Initialize Speech Recognition & Synthesis features
 */
function initSpeechAPI() {
    // Check Speech Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            isDictating = true;
            micBtn.classList.remove('text-slate-400');
            micBtn.classList.add('text-emerald-500', 'bg-emerald-500/10', 'border-emerald-500/20');
            chatInput.placeholder = "Listening...";
        };

        recognition.onend = () => {
            isDictating = false;
            micBtn.classList.add('text-slate-400');
            micBtn.classList.remove('text-emerald-500', 'bg-emerald-500/10', 'border-emerald-500/20');
            chatInput.placeholder = "Ask a question...";
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            chatInput.value = transcript;
            chatInput.focus();
        };

        recognition.onerror = (e) => {
            console.error("Speech recognition error:", e);
            showNotification("Speech recognition error: " + e.error, "danger");
        };
    } else {
        micBtn.style.display = 'none';
        console.warn("Speech Recognition API not supported in this browser.");
    }
}

/**
 * Toggle Dictation Speech-to-text mode
 */
function toggleDictation() {
    if (!recognition) return;
    if (isDictating) {
        recognition.stop();
    } else {
        recognition.start();
    }
}

/**
 * Toggle Text-to-speech audio playback
 */
function toggleTTS() {
    ttsEnabled = !ttsEnabled;
    if (ttsEnabled) {
        speakerBtn.innerHTML = '<i class="fa-solid fa-volume-high"></i>';
        speakerBtn.classList.remove('text-slate-400');
        speakerBtn.classList.add('text-brand-500', 'bg-brand-500/10', 'border-brand-500/20');
        showNotification("Text-to-speech enabled.", "info");
    } else {
        speakerBtn.innerHTML = '<i class="fa-solid fa-volume-xmark"></i>';
        speakerBtn.classList.add('text-slate-400');
        speakerBtn.classList.remove('text-brand-500', 'bg-brand-500/10', 'border-brand-500/20');
        // Stop any current speaking
        window.speechSynthesis.cancel();
    }
}

/**
 * Speak text out loud using Synthesis
 */
function speak(text) {
    if (!ttsEnabled) return;
    window.speechSynthesis.cancel(); // cancel any active speaking
    
    // Strip HTML tags if any
    const tempDiv = document.createElement("div");
    tempDiv.innerHTML = text;
    const cleanText = tempDiv.textContent || tempDiv.innerText || "";
    
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = 'en-US';
    window.speechSynthesis.speak(utterance);
}

/**
 * Helper to display toast notifications
 */
function showNotification(message, category = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast-item pointer-events-auto flex items-center p-4 rounded-xl shadow-lg border backdrop-blur-glass transition-all duration-300 transform translate-x-0 bg-white/95 dark:bg-[#0c1220]/95
        ${category === 'success' ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-600 dark:text-emerald-400' : ''}
        ${category === 'danger' ? 'bg-rose-500/10 border-rose-500/20 text-rose-600 dark:text-rose-400' : ''}
        ${category === 'info' ? 'bg-blue-500/10 border-blue-500/20 text-blue-600 dark:text-blue-400' : ''}`;
        
    toast.innerHTML = `
        <div class="mr-3 text-lg">
            <i class="fa-solid ${category === 'success' ? 'fa-circle-check' : category === 'danger' ? 'fa-circle-xmark' : 'fa-circle-info'}"></i>
        </div>
        <div class="flex-1 text-sm font-medium">${message}</div>
        <button onclick="this.parentElement.remove()" class="ml-4 text-slate-400 hover:text-slate-650 transition-colors">
            <i class="fa-solid fa-xmark"></i>
        </button>
    `;
    
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100px)';
        setTimeout(() => toast.remove(), 300);
    }, 5000);
}

/**
 * Auto scrolls to the bottom of the chat container
 */
function scrollToBottom() {
    chatMessagesContainer.scrollTo({
        top: chatMessagesContainer.scrollHeight,
        behavior: 'smooth'
    });
}

/**
 * Fills query input from quick recommendations
 */
function fillQuery(text) {
    chatInput.value = text;
    chatInput.focus();
}

/**
 * Clears chat bubbles from current view
 */
function clearCurrentChat() {
    chatMessagesContainer.innerHTML = '';
    chatEmptyState.classList.remove('hidden');
    chatMessagesContainer.appendChild(chatEmptyState);
    showNotification("Chat display cleared.", "info");
}

/**
 * Sidebar responsive toggler
 */
function toggleSidebar() {
    const sidebar = document.getElementById('chat-sidebar');
    const backdrop = document.getElementById('sidebar-backdrop');
    sidebar.classList.toggle('-translate-x-full');
    backdrop.classList.toggle('hidden');
}

/**
 * Start a new chat (resets active state)
 */
function startNewChat() {
    activeSessionId = null;
    activeSessionTitle.innerText = "New Chat";
    
    // Clear display
    chatMessagesContainer.innerHTML = '';
    chatEmptyState.classList.remove('hidden');
    chatMessagesContainer.appendChild(chatEmptyState);
    
    // Remove active styles from sidebar
    document.querySelectorAll('.session-row').forEach(row => {
        row.classList.remove('bg-brand-500/10', 'text-brand-600', 'dark:bg-brand-500/5', 'dark:text-brand-400');
        row.classList.add('text-slate-600', 'dark:text-slate-400');
    });

    // Close sidebar on mobile
    if (!document.getElementById('sidebar-backdrop').classList.contains('hidden')) {
        toggleSidebar();
    }
}

/**
 * Render standard chat bubbles
 */
function appendMessage(sender, text, timestamp = null, confidence = null, matchedKeywords = [], suggestions = []) {
    // Hide empty state if visible
    if (!chatEmptyState.classList.contains('hidden')) {
        chatEmptyState.classList.add('hidden');
        chatMessagesContainer.innerHTML = '';
    }

    const timeString = timestamp ? new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    const isBot = sender === 'bot';
    
    const bubbleWrapper = document.createElement('div');
    bubbleWrapper.className = `flex items-start space-x-3.5 max-w-4xl ${isBot ? 'mr-auto' : 'ml-auto flex-row-reverse space-x-reverse'}`;

    let messageContent = text;
    
    // Highlight matched keywords
    if (isBot && matchedKeywords && matchedKeywords.length > 0) {
        matchedKeywords.forEach(kw => {
            const regex = new RegExp(`\\b(${kw})\\b`, 'gi');
            messageContent = messageContent.replace(regex, '<span class="highlight-word">$1</span>');
        });
    }

    const avatarHtml = isBot 
        ? `<div class="w-9 h-9 rounded-xl bg-brand-600 flex items-center justify-center text-white text-sm shadow-md shrink-0"><i class="fa-solid fa-robot"></i></div>`
        : `<div class="w-9 h-9 rounded-xl bg-gradient-to-br from-indigo-500 to-brand-500 flex items-center justify-center text-white font-bold text-xs shrink-0">${document.querySelector('header .rounded-lg').innerText}</div>`;

    let confidenceHtml = '';
    if (isBot && confidence !== null) {
        const confPercent = (confidence * 100).toFixed(1);
        confidenceHtml = `
            <div class="mt-2 flex items-center space-x-2 text-[10px] font-bold ${confidence >= 0.35 ? 'text-brand-500 dark:text-brand-400' : 'text-rose-500'}">
                <i class="fa-solid ${confidence >= 0.35 ? 'fa-circle-check' : 'fa-triangle-exclamation'}"></i>
                <span>Match confidence: ${confPercent}%</span>
            </div>
        `;
    }

    let suggestionsHtml = '';
    if (isBot && suggestions && suggestions.length > 0) {
        suggestionsHtml = `
            <div class="mt-4 border-t border-slate-200/40 dark:border-slate-800/40 pt-3">
                <div class="text-[10px] uppercase font-bold text-slate-400 mb-2">Did you mean:</div>
                <div class="flex flex-col gap-1.5">
                    ${suggestions.map(s => `
                        <button onclick="fillQuery(\`${s.question.replace(/"/g, '&quot;')}\`); submitQuery(null);" class="text-left text-xs font-semibold text-brand-600 dark:text-brand-400 hover:underline flex items-center space-x-1">
                            <i class="fa-solid fa-link text-[9px]"></i>
                            <span>${s.question}</span>
                        </button>
                    `).join('')}
                </div>
            </div>
        `;
    }

    bubbleWrapper.innerHTML = `
        ${avatarHtml}
        <div class="flex flex-col space-y-1 max-w-[80%]">
            <div class="px-4 py-3 rounded-xl shadow-sm border ${isBot ? 'bg-white dark:bg-[#0c1220] border-slate-200/50 dark:border-slate-800/50 text-slate-850 dark:text-slate-200' : 'bg-brand-600 text-white border-brand-600'} text-sm leading-relaxed">
                <div>${messageContent}</div>
                ${confidenceHtml}
                ${suggestionsHtml}
            </div>
            <span class="text-[9px] font-bold text-slate-400 uppercase self-start px-1">${timeString}</span>
        </div>
    `;

    chatMessagesContainer.appendChild(bubbleWrapper);
    scrollToBottom();
    
    // TTS audio playback
    if (isBot) {
        speak(text);
    }
}

/**
 * Show temporary typing indicator
 */
let typingIndicator = null;
function showTypingIndicator() {
    if (typingIndicator) return;
    
    typingIndicator = document.createElement('div');
    typingIndicator.className = 'flex items-start space-x-3.5 max-w-4xl mr-auto';
    typingIndicator.innerHTML = `
        <div class="w-9 h-9 rounded-xl bg-brand-600 flex items-center justify-center text-white text-sm shadow-md shrink-0"><i class="fa-solid fa-robot"></i></div>
        <div class="flex flex-col space-y-1">
            <div class="px-4 py-3 rounded-xl bg-white dark:bg-[#0c1220] border border-slate-200/50 dark:border-slate-800/50 text-slate-400 flex items-center space-x-1.5 h-10">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        </div>
    `;
    
    chatMessagesContainer.appendChild(typingIndicator);
    scrollToBottom();
}

function removeTypingIndicator() {
    if (typingIndicator) {
        typingIndicator.remove();
        typingIndicator = null;
    }
}

/**
 * Handle form submissions
 */
async function submitQuery(event) {
    if (event) event.preventDefault();
    
    const query = chatInput.value.trim();
    if (!query) return;

    // Append user bubble
    appendMessage('user', query);
    chatInput.value = '';
    
    // Show typing
    showTypingIndicator();

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: query,
                session_id: activeSessionId
            })
        });

        const data = await response.json();
        removeTypingIndicator();

        if (response.ok) {
            const isNewSession = activeSessionId === null;
            activeSessionId = data.session_id;
            activeSessionTitle.innerText = data.session_title;
            
            // Append bot response
            appendMessage(
                'bot', 
                data.response.answer, 
                null, 
                data.response.confidence, 
                data.response.matched_keywords, 
                data.response.suggestions
            );
            
            if (isNewSession) {
                // Fetch updated sidebar list
                refreshSessionsList();
            }
        } else {
            appendMessage('bot', "Error: " + (data.error || "Unable to retrieve response."));
        }
    } catch (err) {
        removeTypingIndicator();
        console.error(err);
        appendMessage('bot', "Network error: Unable to connect to similarity engine.");
    }
}

/**
 * Reload chat sessions in the sidebar
 */
async function refreshSessionsList() {
    try {
        const response = await fetch('/api/chat/sessions');
        if (!response.ok) return;
        const sessions = await response.json();
        
        const container = document.getElementById('sessions-container');
        container.innerHTML = '';
        
        if (sessions.length === 0) {
            container.innerHTML = `<div id="no-sessions" class="text-center py-8 text-xs text-slate-400 font-medium">No conversations yet.</div>`;
            return;
        }

        sessions.forEach(s => {
            const activeClass = s.id === activeSessionId ? 'bg-brand-500/10 text-brand-600 dark:bg-brand-500/5 dark:text-brand-400' : 'text-slate-600 dark:text-slate-400';
            const row = document.createElement('div');
            row.setAttribute('data-session-id', s.id);
            row.className = `session-row group flex items-center justify-between px-3 py-3 rounded-xl cursor-pointer hover:bg-slate-100 dark:hover:bg-slate-800/40 transition-colors ${activeClass}`;
            
            row.innerHTML = `
                <div onclick="loadSession('${s.id}')" class="flex items-center space-x-3 flex-1 min-w-0">
                    <i class="fa-regular fa-comment text-sm shrink-0"></i>
                    <span class="text-xs font-semibold truncate session-title">${s.title}</span>
                </div>
                <div class="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onclick="renameSessionPrompt('${s.id}', event)" class="p-1 text-slate-400 hover:text-brand-500 text-2xs" title="Rename">
                        <i class="fa-solid fa-pen"></i>
                    </button>
                    <button onclick="deleteSession('${s.id}', event)" class="p-1 text-slate-400 hover:text-rose-500 text-2xs" title="Delete">
                        <i class="fa-solid fa-trash"></i>
                    </button>
                </div>
            `;
            container.appendChild(row);
        });
    } catch (e) {
        console.error("Failed to load sessions:", e);
    }
}

/**
 * Load history messages of a specific session
 */
async function loadSession(id) {
    activeSessionId = id;
    
    // Close sidebar on mobile
    if (!document.getElementById('sidebar-backdrop').classList.contains('hidden')) {
        toggleSidebar();
    }
    
    // Apply visual active classes
    document.querySelectorAll('.session-row').forEach(row => {
        if (row.getAttribute('data-session-id') === id) {
            row.classList.add('bg-brand-500/10', 'text-brand-600', 'dark:bg-brand-500/5', 'dark:text-brand-400');
            row.classList.remove('text-slate-600', 'dark:text-slate-400');
        } else {
            row.classList.remove('bg-brand-500/10', 'text-brand-600', 'dark:bg-brand-500/5', 'dark:text-brand-400');
            row.classList.add('text-slate-600', 'dark:text-slate-400');
        }
    });

    showTypingIndicator();

    try {
        const response = await fetch(`/api/chat/session/${id}`);
        const data = await response.json();
        removeTypingIndicator();

        if (response.ok) {
            activeSessionTitle.innerText = data.session.title;
            chatMessagesContainer.innerHTML = '';
            
            if (data.messages.length === 0) {
                chatEmptyState.classList.remove('hidden');
                chatMessagesContainer.appendChild(chatEmptyState);
            } else {
                chatEmptyState.classList.add('hidden');
                data.messages.forEach(msg => {
                    appendMessage(msg.sender, msg.message, msg.timestamp, msg.confidence_score);
                });
            }
        } else {
            showNotification(data.error || "Failed to load session details", "danger");
        }
    } catch (err) {
        removeTypingIndicator();
        console.error(err);
        showNotification("Failed to connect to history server.", "danger");
    }
}

/**
 * Filter sessions list in the sidebar (Local Search)
 */
function filterSessions() {
    const filter = document.getElementById('search-sessions').value.toLowerCase();
    document.querySelectorAll('.session-row').forEach(row => {
        const text = row.querySelector('.session-title').innerText.toLowerCase();
        if (text.includes(filter)) {
            row.classList.remove('hidden');
        } else {
            row.classList.add('hidden');
        }
    });
}

/**
 * Rename session handlers
 */
function renameSessionPrompt(id, event) {
    if (event) event.stopPropagation();
    renameTargetId = id;
    
    // Find current title
    const row = document.querySelector(`.session-row[data-session-id="${id}"]`);
    const currentTitle = row.querySelector('.session-title').innerText;
    
    renameInput.value = currentTitle;
    renameModal.classList.remove('hidden');
    renameInput.focus();
}

function closeRenameModal() {
    renameModal.classList.add('hidden');
    renameTargetId = null;
}

async function submitRename() {
    const newTitle = renameInput.value.trim();
    if (!newTitle) return;
    
    const id = renameTargetId;
    closeRenameModal();
    
    try {
        const response = await fetch(`/api/chat/session/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: newTitle })
        });
        
        if (response.ok) {
            showNotification("Session renamed.", "success");
            if (id === activeSessionId) {
                activeSessionTitle.innerText = newTitle;
            }
            refreshSessionsList();
        } else {
            const data = await response.json();
            showNotification(data.error || "Rename failed", "danger");
        }
    } catch (e) {
        showNotification("Network error renaming session.", "danger");
    }
}

/**
 * Delete session handler
 */
async function deleteSession(id, event) {
    if (event) event.stopPropagation();
    if (!confirm("Are you sure you want to delete this conversation?")) return;
    
    try {
        const response = await fetch(`/api/chat/session/${id}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            showNotification("Conversation deleted.", "info");
            if (id === activeSessionId) {
                startNewChat();
            }
            refreshSessionsList();
        } else {
            const data = await response.json();
            showNotification(data.error || "Delete failed", "danger");
        }
    } catch (e) {
        showNotification("Network error deleting session.", "danger");
    }
}

/**
 * Export chat history (TXT or PDF)
 */
function exportChat(type) {
    // Collect all loaded messages
    const bubbles = chatMessagesContainer.querySelectorAll('.flex.items-start');
    if (bubbles.length === 0 || !chatEmptyState.classList.contains('hidden') === false) {
        showNotification("No messages available to export.", "danger");
        return;
    }

    const title = activeSessionTitle.innerText;
    let textContent = `SMART FAQ ASSISTANT CHAT LOG\nConversation: ${title}\nExport Date: ${new Date().toLocaleString()}\n========================================\n\n`;
    
    const messages = [];
    bubbles.forEach(b => {
        const isBot = b.querySelector('.fa-robot') !== null;
        const sender = isBot ? "Bot" : "User";
        const contentDiv = b.querySelector('.px-4.py-3 > div:first-child');
        
        if (contentDiv) {
            const msgText = contentDiv.textContent.trim();
            const timeSpan = b.querySelector('span.text-\\[9px\\]');
            const time = timeSpan ? timeSpan.textContent.trim() : "";
            
            messages.push({ sender, text: msgText, time });
            textContent += `[${time}] ${sender}: ${msgText}\n\n`;
        }
    });

    if (type === 'txt') {
        const blob = new Blob([textContent], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `chat_export_${title.replace(/\s+/g, '_')}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        showNotification("TXT file downloaded.", "success");
    } else if (type === 'pdf') {
        try {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            
            // PDF Styling
            doc.setFont("helvetica", "normal");
            doc.setFontSize(18);
            doc.setTextColor(124, 58, 237); // Brand violet
            doc.text("Smart FAQ Assistant Chat Log", 15, 20);
            
            doc.setFontSize(10);
            doc.setTextColor(100, 116, 139); // Slate-500
            doc.text(`Conversation: ${title}`, 15, 27);
            doc.text(`Exported: ${new Date().toLocaleString()}`, 15, 32);
            
            doc.setLineWidth(0.5);
            doc.setDrawColor(226, 232, 240);
            doc.line(15, 36, 195, 36);
            
            let y = 45;
            doc.setFontSize(10);
            
            messages.forEach(m => {
                // Check page height limit
                if (y > 270) {
                    doc.addPage();
                    y = 20;
                }
                
                doc.setFont("helvetica", "bold");
                if (m.sender === "Bot") {
                    doc.setTextColor(124, 58, 237);
                } else {
                    doc.setTextColor(15, 23, 42);
                }
                doc.text(`${m.sender} [${m.time}]:`, 15, y);
                
                doc.setFont("helvetica", "normal");
                doc.setTextColor(51, 65, 85);
                
                // Split text to fit page width
                const splitText = doc.splitTextToSize(m.text, 170);
                doc.text(splitText, 15, y + 5);
                
                y += 10 + (splitText.length * 5);
            });
            
            doc.save(`chat_export_${title.replace(/\s+/g, '_')}.pdf`);
            showNotification("PDF file downloaded.", "success");
        } catch (err) {
            console.error("PDF export error:", err);
            showNotification("Failed to generate PDF.", "danger");
        }
    }
}
