// Generated per page load — refresh starts a new conversation.
// Swap for localStorage persistence when session memory lands.
const conversationId = crypto.randomUUID();

const messagesEl = document.getElementById("messages");
const formEl = document.getElementById("chat-form");
const inputEl = document.getElementById("message-input");
const sendButtonEl = document.getElementById("send-button");

function addMessage(role, text) {
  const el = document.createElement("div");
  el.className = `message ${role}`;
  el.textContent = text;
  messagesEl.appendChild(el);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function sendMessage(message) {
  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, conversation_id: conversationId }),
  });
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${await response.text()}`);
  }
  const data = await response.json();
  return data.reply;
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = inputEl.value.trim();
  if (!message) return;

  addMessage("user", message);
  inputEl.value = "";
  sendButtonEl.disabled = true;

  try {
    const reply = await sendMessage(message);
    addMessage("assistant", reply);
  } catch (error) {
    addMessage("error", `Request failed: ${error.message}`);
  } finally {
    sendButtonEl.disabled = false;
    inputEl.focus();
  }
});
