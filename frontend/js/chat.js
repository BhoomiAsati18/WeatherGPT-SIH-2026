/**
 * WeatherGPT - Chat Orchestration & API Handler
 */

const API_BASE_URL = 'http://localhost:8000/api';

class ChatController {
  constructor() {
    this.messagesContainer = document.getElementById('chatMessages');
    this.inputField = document.getElementById('chatInput');
    this.form = document.getElementById('chatForm');
    this.suggestionContainer = document.getElementById('suggestionChips');
  }

  init(onWeatherUpdateCallback) {
    this.onWeatherUpdate = onWeatherUpdateCallback;

    if (this.form) {
      this.form.addEventListener('submit', (e) => {
        e.preventDefault();
        const text = this.inputField.value.trim();
        if (text) {
          this.sendMessage(text);
          this.inputField.value = '';
        }
      });
    }

    // Clear chat button
    const clearBtn = document.getElementById('clearChatBtn');
    if (clearBtn) {
      clearBtn.addEventListener('click', () => {
        this.messagesContainer.innerHTML = '';
        this.appendAssistantMessage("Conversation cleared. How can I assist with weather & disaster safety?", null, [], []);
      });
    }
  }

  appendUserMessage(text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message user-msg';
    msgDiv.innerHTML = `
      <div class="msg-avatar">👤</div>
      <div class="msg-body">
        <div class="msg-text">${this.escapeHTML(text)}</div>
      </div>
    `;
    this.messagesContainer.appendChild(msgDiv);
    this.scrollToBottom();
  }

  appendAssistantMessage(answerText, alert, advisories, followups) {
    const msgDiv = document.createElement('div');
    msgDiv.className = 'message assistant-msg';

    // Format markdown bold & line breaks
    let formatted = this.escapeHTML(answerText)
      .replace(/\*\*(.*?)\*\*/g, '<b>$1</b>')
      .replace(/\n/g, '<br>');

    // Alert pill if active
    let alertHTML = '';
    if (alert && alert.severity !== 'normal') {
      const isRed = alert.severity === 'severe';
      const badgeBg = isRed ? '#dc2626' : '#ea580c';
      alertHTML = `
        <div style="background:${badgeBg}; color:#fff; padding:6px 12px; border-radius:6px; font-weight:700; font-size:0.8rem; margin-bottom:8px; display:inline-flex; align-items:center; gap:6px;">
          <span>🚨</span>
          <span>${alert.headline}</span>
        </div>
      `;
    }

    // Actionable advice pills
    let advHTML = '';
    if (advisories && advisories.length > 0) {
      advHTML = `
        <div style="margin-top:10px; background:rgba(6, 182, 212, 0.1); border-left:3px solid var(--accent-cyan); padding:8px 12px; border-radius:6px; font-size:0.85rem;">
          <b>Actionable Advice:</b>
          <ul style="margin-left:16px; margin-top:4px;">
            ${advisories.map(a => `<li>${a}</li>`).join('')}
          </ul>
        </div>
      `;
    }

    msgDiv.innerHTML = `
      <div class="msg-avatar">🤖</div>
      <div class="msg-body">
        ${alertHTML}
        <div class="msg-text">${formatted}</div>
        ${advHTML}
        <div class="msg-meta">
          <span>Grounded Meteorological Data</span>
          <button class="btn-tts" title="Listen to response (TTS)">🔊 Listen</button>
        </div>
      </div>
    `;

    // TTS speaker click handler
    const ttsBtn = msgDiv.querySelector('.btn-tts');
    if (ttsBtn) {
      ttsBtn.addEventListener('click', () => {
        window.voiceEngine.speakText(answerText, window.currentLanguage);
      });
    }

    this.messagesContainer.appendChild(msgDiv);
    this.scrollToBottom();

    // Update suggestions if provided
    if (followups && followups.length > 0) {
      this.updateSuggestions(followups);
    }
  }

  appendLoadingMessage() {
    const loaderDiv = document.createElement('div');
    loaderDiv.className = 'message assistant-msg msg-loading';
    loaderDiv.id = 'loadingMsg';
    loaderDiv.innerHTML = `
      <div class="msg-avatar">🤖</div>
      <div class="msg-body">
        <div class="msg-text" style="color:var(--text-muted); font-style:italic;">
          Fetching verified meteorological data & analyzing advisories...
        </div>
      </div>
    `;
    this.messagesContainer.appendChild(loaderDiv);
    this.scrollToBottom();
  }

  removeLoadingMessage() {
    const el = document.getElementById('loadingMsg');
    if (el) el.remove();
  }

  async sendMessage(queryText) {
    this.appendUserMessage(queryText);
    this.appendLoadingMessage();

    const payload = {
      message: queryText,
      persona: window.currentPersona || 'citizen',
      language: window.currentLanguage || 'hinglish',
      city: window.currentCity || 'Indore'
    };

    try {
      const resp = await fetch(`${API_BASE_URL}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      this.removeLoadingMessage();

      if (resp.ok) {
        const data = await resp.json();
        this.appendAssistantMessage(
          data.answer,
          data.alert,
          data.actionable_advisory,
          data.suggested_followups
        );

        // Notify dashboard to update weather cards
        if (data.weather_card && this.onWeatherUpdate) {
          this.onWeatherUpdate(data.weather_card);
        }
      } else {
        this.appendAssistantMessage(
          "Maaf kijiye, weather data fetch karne mein temporary issue aaya. Kripya punah prayas karein.",
          null, [], []
        );
      }
    } catch (err) {
      this.removeLoadingMessage();
      console.error("Chat API fetch error:", err);
      this.appendAssistantMessage(
        "Backend server se connect nahi ho paya (http://localhost:8000). Kripya check karein ki FastAPI server running hai.",
        null, [], []
      );
    }
  }

  updateSuggestions(suggestions) {
    if (!this.suggestionContainer) return;
    this.suggestionContainer.innerHTML = '';
    suggestions.forEach(query => {
      const btn = document.createElement('button');
      btn.className = 'sug-chip';
      btn.textContent = query;
      btn.addEventListener('click', () => {
        this.sendMessage(query);
      });
      this.suggestionContainer.appendChild(btn);
    });
  }

  scrollToBottom() {
    this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
  }

  escapeHTML(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;');
  }
}

window.chatController = new ChatController();
