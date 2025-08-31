// Global variables
let currentTab = 'home';
let jwtToken = '';
let isAuthenticated = false;

// API Base URL - Production Railway backend
const API_BASE_URL = 'https://tamil-voice-gateway-production.up.railway.app';

// Provider selections
let selectedSTTProvider = 'google';
let selectedTTSProvider = 'elevenlabs';
let selectedVaangaSTTProvider = 'google';
let selectedVaangaTTSProvider = 'elevenlabs';
let selectedLLMProvider = 'gemini';

// Recording variables
let mediaRecorder;
let audioChunks = [];
let isRecording = false;

// Vaanga Pesalam variables
let vaangaRecording = false;
let vaangaMediaRecorder;
let vaangaAudioChunks = [];
let currentSessionId = null;

// Tab management
function showTab(tabName) {
    // Skip authentication check for testing
    // if (tabName !== 'home' && !isAuthenticated) {
    //     showStatus('tokenStatus', 'Please authenticate first in the Home tab', 'error');
    //     return;
    // }

    // Update nav tabs
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');

    // Update content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(tabName).classList.add('active');

    currentTab = tabName;
}

// Provider selection functions
function selectSTTProvider(provider) {
    selectedSTTProvider = provider;
    document.querySelectorAll('#listen .model-option').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelector(`#listen [data-provider="${provider}"]`).classList.add('selected');
}

function selectTTSProvider(provider) {
    selectedTTSProvider = provider;
    updateProviderCards('speak', provider);
}

function selectVaangaSTTProvider(provider) {
    selectedVaangaSTTProvider = provider;
    document.querySelectorAll('#vaanga-pesalam .stt-selector .model-option').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelector(`#vaanga-pesalam .stt-selector [data-provider="${provider}"]`).classList.add('selected');
}

function selectVaangaTTSProvider(provider) {
    selectedVaangaTTSProvider = provider;
    updateProviderCards('vaanga-tts', provider);
}

function selectLLMProvider(provider) {
    selectedLLMProvider = provider;
    document.querySelectorAll('#vaanga-pesalam .model-selector .model-option').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelector(`#vaanga-pesalam .model-selector [data-provider="${provider}"]`).classList.add('selected');
    console.log('LLM Provider selected:', provider);
}

function updateProviderCards(section, selectedProvider) {
    // This function is no longer needed as we handle selection directly in the specific functions
}

// Status display function
function showStatus(elementId, message, type = 'info') {
    const element = document.getElementById(elementId);
    if (element) {
        element.innerHTML = `<div class="status ${type}">${message}</div>`;
    }
}

// Authentication functions
async function generateToken() {
    try {
        showStatus('tokenStatus', 'Generating token...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/v1/auth/token`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                user_id: 'test_user',
                expires_in: 3600
            })
        });

        if (response.ok) {
            const result = await response.json();
            document.getElementById('jwtToken').value = result.access_token;
            jwtToken = result.access_token;
            isAuthenticated = true;
            showStatus('tokenStatus', 'Token generated successfully', 'success');
            
            document.getElementById('tokenInfo').style.display = 'block';
            document.getElementById('tokenDetails').innerHTML = `
                <strong>Token Type:</strong> ${result.token_type}<br>
                <strong>Expires In:</strong> ${result.expires_in} seconds
            `;
        } else {
            const error = await response.json();
            showStatus('tokenStatus', `Token generation failed: ${error.detail}`, 'error');
        }
    } catch (error) {
        showStatus('tokenStatus', `Network error: ${error.message}`, 'error');
    }
}

async function validateToken() {
    const token = document.getElementById('jwtToken').value.trim();
    if (!token) {
        showStatus('tokenStatus', 'Please enter a JWT token', 'error');
        return;
    }

    try {
        showStatus('tokenStatus', 'Validating token...', 'info');
        
        const response = await fetch(`${API_BASE_URL}/v1/auth/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.ok) {
            const result = await response.json();
            jwtToken = token;
            isAuthenticated = true;
            showStatus('tokenStatus', 'Token validated successfully', 'success');
            
            document.getElementById('tokenInfo').style.display = 'block';
            document.getElementById('tokenDetails').innerHTML = `
                <strong>User ID:</strong> ${result.user_id}<br>
                <strong>Valid Until:</strong> ${new Date(result.exp * 1000).toLocaleString()}
            `;
        } else {
            const error = await response.json();
            isAuthenticated = false;
            showStatus('tokenStatus', `Token validation failed: ${error.detail}`, 'error');
        }
    } catch (error) {
        isAuthenticated = false;
        showStatus('tokenStatus', `Network error: ${error.message}`, 'error');
    }
}

// Listen module functions
async function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

async function startRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            processRecording();
        };

        mediaRecorder.start();
        isRecording = true;
        
        document.getElementById('recordBtn').textContent = '⏹️ Stop Recording';
        document.getElementById('recordingStatus').innerHTML = '<span class="recording-indicator"></span> Recording...';
        
    } catch (error) {
        showStatus('listenStatus', `Recording error: ${error.message}`, 'error');
    }
}

function stopRecording() {
    if (mediaRecorder && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        
        document.getElementById('recordBtn').textContent = '🎤 Start Recording';
        document.getElementById('recordingStatus').textContent = '';
        
        mediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
}

async function processRecording() {
    try {
        showStatus('listenStatus', 'Processing audio...', 'info');
        
        const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('audio', audioBlob);
        formData.append('stt_provider', selectedSTTProvider);
        formData.append('language', 'auto');
        formData.append('timestamps', 'false');

        const response = await fetch(`${API_BASE_URL}/v1/listen`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${jwtToken}`,
                'x-skip-auth': 'true'
            },
            body: formData
        });

        if (response.ok) {
            const result = await response.json();
            document.getElementById('transcriptResult').style.display = 'block';
            document.getElementById('transcriptContent').innerHTML = `
                <div><strong>Original (${result.original_language}):</strong> ${result.original_text}</div>
                <div><strong>English Translation:</strong> ${result.english_transcript}</div>
                <div><strong>Provider:</strong> ${result.stt_provider}</div>
                <div><strong>Confidence:</strong> ${(result.confidence * 100).toFixed(1)}%</div>
            `;
            showStatus('listenStatus', 'Transcription completed successfully', 'success');
        } else {
            const error = await response.json();
            showStatus('listenStatus', `Error: ${error.detail || 'Transcription failed'}`, 'error');
        }
    } catch (error) {
        showStatus('listenStatus', `Network error: ${error.message}`, 'error');
    }
}

// Speak module functions
async function generateSpeech() {
    const text = document.getElementById('speakText').value.trim();
    const language = document.getElementById('speakLanguage').value;
    const speed = 1.0; // Default speed since speakSpeed element doesn't exist

    if (!text) {
        showStatus('speakStatus', 'Please enter text to speak', 'error');
        return;
    }

    try {
        showStatus('speakStatus', 'Generating speech...', 'info');

        const response = await fetch(`${API_BASE_URL}/v1/speak`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-skip-auth': 'true'
            },
            body: JSON.stringify({
                english_text: text,
                target_language: language,
                voice_speed: speed,
                voice_provider: selectedTTSProvider
            })
        });

        if (response.ok) {
            const audioBlob = await response.blob();
            const audioUrl = URL.createObjectURL(audioBlob);
            
            const audioPlayer = document.getElementById('audioPlayer');
            audioPlayer.src = audioUrl;
            audioPlayer.style.display = 'block';
            
            document.getElementById('speakResult').style.display = 'block';
            showStatus('speakStatus', 'Speech generated successfully', 'success');
        } else {
            const error = await response.json();
            showStatus('speakStatus', `Error: ${error.detail || 'Speech generation failed'}`, 'error');
        }
    } catch (error) {
        showStatus('speakStatus', `Network error: ${error.message}`, 'error');
    }
}

function clearSpeakResults() {
    document.getElementById('speakResult').style.display = 'none';
    document.getElementById('speakStatus').innerHTML = '';
    document.getElementById('speakText').value = '';
}

// Update speed display
document.addEventListener('DOMContentLoaded', function() {
    const speedSlider = document.getElementById('speakSpeed');
    const speedValue = document.getElementById('speedValue');
    
    if (speedSlider && speedValue) {
        speedSlider.addEventListener('input', function() {
            speedValue.textContent = this.value + 'x';
        });
    }
});

// Vaanga Pesalam functions
async function toggleVaangaRecording() {
    if (vaangaRecording) {
        stopVaangaRecording();
    } else {
        startVaangaRecording();
    }
}

async function startVaangaRecording() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        vaangaMediaRecorder = new MediaRecorder(stream);
        vaangaAudioChunks = [];
        
        vaangaMediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                vaangaAudioChunks.push(event.data);
            }
        };
        
        vaangaMediaRecorder.onstop = () => {
            processVaangaRecording();
        };
        
        vaangaMediaRecorder.start();
        vaangaRecording = true;
        
        // Update button UI for recording state
        const recordBtn = document.getElementById('vaangaRecordBtn');
        const micIcon = recordBtn.querySelector('.mic-icon');
        const callText = recordBtn.querySelector('.call-text');
        
        recordBtn.classList.add('recording');
        micIcon.textContent = '⏸️';
        callText.textContent = 'Stop recording';
        
        showStatus('vaangaStatus', 'Listening... Speak now!', 'info');
        
    } catch (error) {
        showStatus('vaangaStatus', `Recording error: ${error.message}`, 'error');
    }
}

function stopVaangaRecording() {
    if (vaangaMediaRecorder && vaangaRecording) {
        vaangaMediaRecorder.stop();
        vaangaRecording = false;
        
        // Reset button UI to default state
        const recordBtn = document.getElementById('vaangaRecordBtn');
        const micIcon = recordBtn.querySelector('.mic-icon');
        const callText = recordBtn.querySelector('.call-text');
        
        recordBtn.classList.remove('recording');
        micIcon.textContent = '🎤';
        callText.textContent = 'Talk to agent';
        
        showStatus('vaangaStatus', 'Processing your message...', 'info');
        
        vaangaMediaRecorder.stream.getTracks().forEach(track => track.stop());
    }
}

async function processVaangaRecording() {
    try {
        const audioBlob = new Blob(vaangaAudioChunks, { type: 'audio/webm' });
        
        if (!currentSessionId) {
            currentSessionId = 'session_' + Date.now();
        }

        // Convert audio to base64
        const reader = new FileReader();
        reader.onloadend = async () => {
            try {
                const base64Audio = reader.result.split(',')[1];
                
                const response = await fetch(`${API_BASE_URL}/v1/vaanga-pesalam`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'x-skip-auth': 'true'
                    },
                    body: JSON.stringify({
                        audio_data: base64Audio,
                        session_id: currentSessionId,
                        stt_provider: selectedVaangaSTTProvider || 'google',
                        llm_provider: selectedLLMProvider || 'gemini',
                        tts_provider: 'elevenlabs',
                        voice_speed: 1.0
                    })
                });

                if (response.ok) {
                    const errorType = response.headers.get('X-Error-Type');
                    
                    if (errorType === 'quota_exceeded') {
                        // Handle quota exceeded - show text response
                        const data = await response.json();
                        const userTranscriptB64 = response.headers.get('X-User-Transcript');
                        const userTranscript = userTranscriptB64 ? decodeURIComponent(escape(atob(userTranscriptB64))) : '';
                        
                        addChatMessage('user', userTranscript);
                        addChatMessage('ai', data.text_response);
                        showStatus('vaangaStatus', '⚠️ Voice quota exceeded. Text response shown.', 'warning');
                    } else {
                        // Normal audio response
                        const userTranscriptB64 = response.headers.get('X-User-Transcript');
                        const aiResponseB64 = response.headers.get('X-AI-Response');
                        const sessionId = response.headers.get('X-Session-ID');
                        
                        const userTranscript = userTranscriptB64 ? decodeURIComponent(escape(atob(userTranscriptB64))) : '';
                        const aiResponse = aiResponseB64 ? decodeURIComponent(escape(atob(aiResponseB64))) : '';
                        
                        // Display conversation in chat
                        addChatMessage('user', userTranscript);
                        addChatMessage('ai', aiResponse);
                        
                        // Play AI response audio
                        const audioBlob = await response.blob();
                        const audioUrl = URL.createObjectURL(audioBlob);
                        const audio = new Audio(audioUrl);
                        audio.play();
                        
                        showStatus('vaangaStatus', 'Response received! 🎵', 'success');
                    }
                } else {
                    const errorData = await response.json();
                    showStatus('vaangaStatus', `❌ Error: ${errorData.detail}`, 'error');
                }
                
            } catch (error) {
                showStatus('vaangaStatus', `❌ Network error: ${error.message}`, 'error');
            }
        };
        
        reader.readAsDataURL(audioBlob);
        
    } catch (error) {
        showStatus('vaangaStatus', `❌ Processing error: ${error.message}`, 'error');
    }
}

function addChatMessage(sender, message) {
    const chatContainer = document.getElementById('chatContainer');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message';
    
    const avatarClass = sender === 'user' ? 'user-avatar' : 'ai-avatar';
    const avatarText = sender === 'user' ? 'U' : 'AI';
    
    messageDiv.innerHTML = `
        <div class="chat-avatar ${avatarClass}">${avatarText}</div>
        <div class="chat-content">${message}</div>
    `;
    
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function clearVaangaChat() {
    const chatContainer = document.getElementById('chatContainer');
    chatContainer.innerHTML = `
        <div class="chat-message">
            <div class="chat-avatar ai-avatar">AI</div>
            <div class="chat-content">
                வணக்கம்! I'm ready to chat with you in Tamil or English. Click "Start Conversation" and speak!
            </div>
        </div>
    `;
    currentSessionId = null;
    // Force reset the LLM provider to ensure Gemini is selected
    selectedLLMProvider = 'gemini';
    // Update UI to show Gemini as selected
    document.querySelectorAll('#vaanga-pesalam .model-selector .model-option').forEach(card => {
        card.classList.remove('selected');
    });
    const geminiCard = document.querySelector('#vaanga-pesalam .model-selector [data-provider="gemini"]');
    if (geminiCard) {
        geminiCard.classList.add('selected');
    }
    console.log('Chat cleared, LLM provider reset to:', selectedLLMProvider);
    showStatus('vaangaStatus', '', 'info');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    // Auto-generate token for easier testing
    generateToken();
    
    // Force Gemini selection on page load
    selectedLLMProvider = 'gemini';
    console.log('Page loaded, LLM provider initialized to:', selectedLLMProvider);
    
    // Ensure Gemini button is visually selected
    setTimeout(() => {
        const geminiCard = document.querySelector('#vaanga-pesalam .model-selector [data-provider="gemini"]');
        if (geminiCard && !geminiCard.classList.contains('selected')) {
            document.querySelectorAll('#vaanga-pesalam .model-selector .model-option').forEach(card => {
                card.classList.remove('selected');
            });
            geminiCard.classList.add('selected');
            console.log('Gemini button visually selected on page load');
        }
    }, 100);
});
