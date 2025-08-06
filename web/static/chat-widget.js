class ChatWidget extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });

    const style = document.createElement('style');
    style.textContent = `
      @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono&family=Roboto:wght@400;500&display=swap');

      :host {
        font-family: 'Roboto', sans-serif;
      }

      .chat-code {
        font-family: 'Roboto Mono', monospace;
      }

      .chat-body,
      .chat-msg-user,
      .chat-msg-bot,
      .chat-footer input,
      .chat-footer button,
      .chat-disclaimer {
        font-family: inherit;
      }

      .chat-btn {
        background-color: #0b3d91;
        color: white;
        border-radius: 9999px;
        position: fixed;
        bottom: 1rem;
        right: 1rem;
        width: 3.5rem;
        height: 3.5rem;
        z-index: 9999;
        display: flex;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        transition: transform 0.2s ease-in-out;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
      }
      .chat-btn:hover {
        background-color: #092f74;
        transform: scale(1.1);
      }
      .chat-modal {
        position: fixed;
        bottom: 6rem;
        right: 1rem;
        width: 24rem;
        height: 36rem;
        background: white;
        border-radius: 0.5rem;
        border: 1px solid #e5e7eb;
        box-shadow:
          0 2px 8px rgba(0, 0, 0, 0.05),
          0 8px 30px rgba(0, 0, 0, 0.1);
        z-index: 9998;
        display: flex;
        flex-direction: column;
        opacity: 0;
        transform: scale(0.95);
        transition: all 0.3s ease-in-out;
        overflow: hidden;
      }
      .chat-modal.open {
        opacity: 1;
        transform: scale(1);
      }
      .chat-header {
        background: #0b3d91;
        color: white;
        padding: 0.75rem 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: 'Roboto', sans-serif;
        font-weight: 500;
        font-size: 0.95rem;
        letter-spacing: 0.25px;
      }
      .chat-body {
        flex: 1;
        padding: 1rem;
        overflow-y: auto;
        background: #f9fafb;
        font-size: 0.875rem;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
      }
      .chat-footer {
        padding: 0.5rem;
        border-top: 1px solid #e5e7eb;
        display: flex;
        gap: 0.5rem;
      }
      .chat-footer input {
        flex: 1;
        padding: 0.5rem;
        font-size: 0.875rem;
        border: 1px solid #d1d5db;
        border-radius: 0.375rem;
      }
      .chat-footer button {
        background: #0b3d91;
        color: white;
        padding: 0.5rem 0.75rem;
        font-size: 0.875rem;
        border-radius: 0.375rem;
        border: none;
        cursor: pointer;
      }
      .chat-msg-user {
        align-self: flex-end;
        background: #e0f2fe;
        padding: 0.5rem;
        border-radius: 0.375rem;
        max-width: 80%;
        word-wrap: break-word;
        white-space: pre-wrap;
      }
      .chat-msg-bot {
        align-self: flex-start;
        background: white;
        padding: 0.5rem;
        border-radius: 0.375rem;
        max-width: 80%;
        border: 1px solid #e5e7eb;
        word-wrap: break-word;
        white-space: pre-wrap;
      }

      .chat-msg-bot ul {
        margin: 0.25rem 0 0 1rem;
        padding: 0;
        font-size: 0.75rem;
        color: #6b7280;
      }

      .chat-msg-bot a {
        color: #0b3d91;
        text-decoration: underline;
      }

      @media (max-width: 480px) {
        .chat-modal {
          width: 100vw;
          height: 100vh;
          bottom: 0;
          right: 0;
          border-radius: 0;
        }
      }

      .chat-disclaimer {
        font-size: 0.75rem;
        color: #9ca3af; 
        font-style: italic;
        text-align: left;
        text-align: center;
        margin-top: 0.25rem;
        padding: 0 0.5rem 0.5rem 0.5rem;
      }

      .typing-cursor {
        width: 2px;
        height: 1rem;
        background-color: #a1a1aa;
        animation: blink-cursor 1s step-start infinite;
        margin-left: 4px;
        align-self: center;
      }

      @keyframes blink-cursor {
        0%, 100% { opacity: 0; }
        50% { opacity: 1; }
      }

      .prompt-buttons {
        display: flex;
        gap: 0.5rem;
        padding: 0 0.5rem 0.5rem;
        margin-bottom: 0;
        justify-content: center;
        flex-wrap: wrap;
        align-items: center;
        background-color: #f9fafb; 
      }

      .prompt-button {
        background-color: #f3f4f6;
        color: #374151;
        border: 1px solid #d1d5db;
        font-size: 0.75rem;
        padding: 0.25rem 0.5rem;
        border-radius: 9999px;
        cursor: pointer;
        transition: background-color 0.2s ease;
      }

      .prompt-button:hover {
        background-color: #e5e7eb;
      }


      .typing-bubble {
        display: inline-flex;
        gap: 6px;
        align-self: flex-start;
        padding: 0.5rem;
        border-radius: 1rem;
        background: #f3f4f6;
        border: 1px solid #e5e7eb;
        max-width: fit-content;
        margin-left: 0.25rem;
        margin-top: 0.25rem;
      }

      .typing-dot {
        width: 6px;
        height: 6px;
        background-color: #a1a1aa;
        border-radius: 9999px;
        animation: typing-blink 1.4s infinite;
      }

      .typing-dot:nth-child(2) {
        animation-delay: 0.2s;
      }

      .typing-dot:nth-child(3) {
        animation-delay: 0.4s;
      }

      @keyframes typing-blink {
        0%, 80%, 100% { opacity: 0.3; }
        40% { opacity: 1; }
      }
    }
    `;

    const wrapper = document.createElement('div');
    wrapper.innerHTML = `
      <div class="chat-btn" title="Chat with us">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="none"
          stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path d="M12 6V2H8"/>
          <path d="m8 18-4 4V8a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2Z"/>
          <path d="M2 12h2"/>
          <path d="M9 11v2"/>
          <path d="M15 11v2"/>
          <path d="M20 12h2"/>
        </svg>
      </div>

      <div class="chat-modal" id="chatModal">
        <div class="chat-header">
          <span><strong>OSDR Data Assistant</strong></span>
          <button id="closeBtn" aria-label="Close chat" style="font-size: 1.25rem; background: none; border: none; color: white;">&times;</button>
        </div>
        <div class="chat-body" id="chatMessages">
          <div class="chat-msg-bot">Enter a question to retrieve study details or sample-level information from OSDR.</div>
        </div>
        <!-- Prompt Buttons -->
        <div class="prompt-buttons" id="promptButtons">
          <button class="prompt-button" data-prompt="Available samples from CBTM‑2">Available samples from CBTM‑2</button>
          <button class="prompt-button" data-prompt="Summarize RR-9">Summarize RR-9</button>
        </div>

        <!-- Chat Footer -->
        <div class="chat-footer">
          <input type="text" id="chatInput" placeholder="Type a message..." />
          <button id="sendBtn">Send</button>
        </div>

        <div class="chat-disclaimer">
          Please do not share sensitive or personally identifiable information. Please verify any important information.
        </div>
      </div>
    `;

    this.shadowRoot.appendChild(style);
    this.shadowRoot.appendChild(wrapper);

    const toggleBtn = this.shadowRoot.querySelector('.chat-btn');
    const modal = this.shadowRoot.getElementById('chatModal');
    const closeBtn = this.shadowRoot.getElementById('closeBtn');
    const sendBtn = this.shadowRoot.getElementById('sendBtn');
    const input = this.shadowRoot.getElementById('chatInput');
    const messages = this.shadowRoot.getElementById('chatMessages');

    const promptBtns = this.shadowRoot.querySelectorAll('.prompt-button');
    const promptContainer = this.shadowRoot.getElementById('promptButtons');
    promptBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        const prompt = btn.dataset.prompt;
        input.value = prompt;
        if (promptContainer) promptContainer.style.display = 'none';  // ✅ Hide
        this.sendMessage(input, messages);
      });
    });



    // Widget state memory with expiration
    const ONE_HOUR = 1000 * 60 * 60;
    const lastUsed = localStorage.getItem('chatWidgetLastUsed');
    if (lastUsed && Date.now() - Number(lastUsed) > ONE_HOUR) {
      localStorage.removeItem('chatWidgetOpen');
      localStorage.removeItem('chatWidgetLastUsed');
    }

    if (localStorage.getItem('chatWidgetOpen') === 'true') {
      modal.classList.add('open');
    }

    toggleBtn.addEventListener('click', () => {
      const isOpen = modal.classList.toggle('open');
      localStorage.setItem('chatWidgetOpen', isOpen);
      localStorage.setItem('chatWidgetLastUsed', Date.now());
    });

    closeBtn.addEventListener('click', () => {
      modal.classList.remove('open');
    });

    sendBtn.addEventListener('click', () => this.sendMessage(input, messages));
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.sendMessage(input, messages);
    });

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') modal.classList.remove('open');
    });
  }
  
  async sendMessage(input, messages) {
    const text = input.value.trim();
    if (!text) return;

    const userMsg = document.createElement('div');
    userMsg.className = 'chat-msg-user';
    userMsg.textContent = text;
    messages.appendChild(userMsg);

    input.value = '';
    messages.scrollTop = messages.scrollHeight;

    // Create typing bubble
    const typing = document.createElement('div');
    typing.className = 'typing-bubble';
    typing.innerHTML = `
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
      <div class="typing-dot"></div>
    `;
    messages.appendChild(typing);
    messages.scrollTop = messages.scrollHeight;

    const API_URL = window.ChatWidgetConfig?.API_URL;

    if (!API_URL) {
      console.error("API_URL is missing! Define it in config.js.");
    }

    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: text })
      });

      const data = await res.json();
      // console.log('Full API response:', data); // log and remove
      const answer = data.answer?.[0]?.text || "Sorry, I couldn't find an answer.";
      // console.log('Extracted answer:', answer);
      const urls = data.source_urls || [];

      // Remove typing animation
      typing.remove();

      // Add bot message
      const botMsg = document.createElement('div');
      botMsg.className = 'chat-msg-bot';
      botMsg.textContent = answer;
      // botMsg.innerHTML = `<pre style="white-space: pre-wrap;">${answer}</pre>`;
      messages.appendChild(botMsg);

      // Optional: Add source URLs
      if (urls.length > 0) {
        const sourceList = document.createElement('ul');
        urls.forEach(url => {
          const li = document.createElement('li');
          const a = document.createElement('a');
          a.href = url;
          a.textContent = url;
          a.target = '_blank';
          li.appendChild(a);
          sourceList.appendChild(li);
        });

        const sources = document.createElement('div');
        sources.className = 'chat-msg-bot';
        sources.innerHTML = `<strong>Sources:</strong><br>`;
        sources.appendChild(sourceList);
        messages.appendChild(sources);
      }

      messages.scrollTop = messages.scrollHeight;

    } catch (err) {
      console.error(err);
      typing.remove();
      const errorMsg = document.createElement('div');
      errorMsg.className = 'chat-msg-bot';
      errorMsg.textContent = '⚠️ Error fetching response.';
      messages.appendChild(errorMsg);
    }
  }
}

customElements.define('chat-widget', ChatWidget);
