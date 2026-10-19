/* Gardenbot – AI Assistant page JavaScript */

document.addEventListener('DOMContentLoaded', checkAiStatus);

async function checkAiStatus() {
    const badge = document.getElementById('ai-status');
    try {
        const serverUrl = document.getElementById('ai-server').value;
        // We check via our own backend proxy
        const resp = await fetch('/ai/status');
        const data = await resp.json();
        if (data.connected) {
            badge.textContent = '● Connected';
            badge.style.background = '#d4edda';
            badge.style.color = '#155724';
        } else {
            badge.textContent = '○ Disconnected';
            badge.style.background = '#f8d7da';
            badge.style.color = '#721c24';
        }
    } catch {
        badge.textContent = '○ Disconnected';
        badge.style.background = '#f8d7da';
        badge.style.color = '#721c24';
    }
}

async function sendQuery(event) {
    event.preventDefault();
    const input = document.getElementById('ai-input');
    const message = input.value.trim();
    if (!message) return;

    // Show user message
    appendMessage(message, 'user');
    input.value = '';

    // Disable input while processing
    const submitBtn = document.getElementById('ai-submit');
    submitBtn.disabled = true;
    submitBtn.textContent = '...';

    try {
        const resp = await fetch('/ai/query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message }),
        });
        const data = await resp.json();

        if (data.response) {
            appendMessage(data.response, 'assistant');
        } else if (data.error) {
            appendMessage(`Error: ${data.error}`, 'error');
        } else {
            appendMessage(data.message || 'No response received.', 'assistant');
        }
    } catch (e) {
        appendMessage('Failed to reach the AI backend. Check your connection.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Send';
    }
}

function quickAction(action) {
    const input = document.getElementById('ai-input');
    const prefixes = {
        'suggest plants': 'Suggest plants for my garden considering sun exposure and existing plantings.',
        'critique layout': 'Critique the current layout of my yard and suggest improvements.',
        'care schedule': 'Generate a monthly care schedule for my current plantings.',
        'companion planting': 'What are good companion planting combinations for my garden?',
    };
    input.value = prefixes[action] || action;
    input.focus();
}

function appendMessage(text, type) {
    const container = document.getElementById('chat-messages');
    const div = document.createElement('div');
    div.className = `message ${type}`;
    div.innerHTML = `<p>${escapeHtml(text)}</p>`;
    container.appendChild(div);
    container.scrollTop = container.scrollHeight;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
