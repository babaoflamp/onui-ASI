// This file will contain the JavaScript logic for the dictionary widget (krdict) and chatbot.
// The floating button expansion will be handled purely by CSS hover effects.

document.addEventListener("DOMContentLoaded", () => {
  // Dictionary Widget Elements
  const krdictToggle = document.getElementById("krdict-toggle");
  const krdictWindow = document.getElementById("krdict-window");
  const krdictClose = document.getElementById("krdict-close");
  const krdictForm = document.getElementById("krdict-widget-form");
  const krdictQuery = document.getElementById("krdict-widget-query");
  const krdictSubmit = document.getElementById("krdict-widget-submit");
  const krdictPart = document.getElementById("krdict-widget-part");
  const krdictMethod = document.getElementById("krdict-widget-method");
  const krdictNum = document.getElementById("krdict-widget-num");
  const krdictStatus = document.getElementById("krdict-widget-status");
  const krdictResults = document.getElementById("krdict-widget-results");

  // Chatbot Widget Elements
  const chatbotToggle = document.getElementById("chatbot-toggle");
  const chatbotWindow = document.getElementById("chatbot-window");
  const chatbotClose = document.getElementById("chatbot-close");
  const chatMessages = document.getElementById("chat-messages");
  const userInput = document.getElementById("user-input");
  const sendButton = document.getElementById("send-button");
  const suggestionButtons = document.querySelectorAll(".suggestion-btn");

  function loadKrdictWidgetPreferences() {
    if (typeof localStorage !== "undefined") {
      const part = localStorage.getItem("krdict-widget-part");
      const method = localStorage.getItem("krdict-widget-method");
      const num = localStorage.getItem("krdict-widget-num");
      if (krdictPart && part !== null) krdictPart.value = part;
      if (krdictMethod && method !== null) krdictMethod.value = method;
      if (krdictNum && num !== null) krdictNum.value = num;
    }
  }

  function saveKrdictWidgetPreferences() {
    if (typeof localStorage !== "undefined") {
      if (krdictPart)
        localStorage.setItem("krdict-widget-part", krdictPart.value || "");
      if (krdictMethod)
        localStorage.setItem("krdict-widget-method", krdictMethod.value || "");
      if (krdictNum)
        localStorage.setItem("krdict-widget-num", krdictNum.value || "10");
    }
  }

  function setKrdictStatus(text) {
    if (!krdictStatus) return;
    if (!text) {
      krdictStatus.classList.add("hidden");
      krdictStatus.textContent = "";
      return;
    }
    krdictStatus.textContent = text;
    krdictStatus.classList.remove("hidden");
  }

  function renderKrdictItem(item) {
    const sensesHtml = (item.senses || [])
      .map(
        (sense) => `
        <p class="text-gray-700 text-sm mb-1">
          ${escapeHtml(String(sense.sense_order || ""))}. ${escapeHtml(sense.definition || "")}
        </p>
        ${(sense.translations || [])
          .map(
            (trans) =>
              `<p class="text-gray-500 text-xs pl-4">(${escapeHtml(trans.trans_lang || "")}) ${escapeHtml(trans.trans_word || "-")}: ${escapeHtml(trans.trans_dfn || "-")}</p>`,
          )
          .join("")}
      `,
      )
      .join("");

    const detailLabel = (typeof translations !== 'undefined' && translations['dict.open_full']) || "Open in full page →";
    const safeLink = (item.link && /^https?:\/\//.test(item.link)) ? item.link : null;
    return `
      <div class="bg-white p-4 rounded-lg shadow-sm border border-gray-100">
        <div class="flex justify-between items-start mb-2">
          <h4 class="font-bold text-md text-gray-800">${escapeHtml(item.word || "")}</h4>
          <span class="text-xs text-gray-500">${escapeHtml(item.pos || "")} ${escapeHtml(item.word_grade || "")}</span>
        </div>
        ${sensesHtml}
        ${
          safeLink
            ? `<a href="${safeLink}" target="_blank" rel="noopener noreferrer" class="text-xs text-emerald-700 hover:text-emerald-600 font-semibold">${escapeHtml(detailLabel)}</a>`
            : ""
        }
      </div>
    `;
  }

  async function fetchKrdictResults(query) {
    const searchingText = "Searching...";
    setKrdictStatus(searchingText);
    if (krdictResults) {
      krdictResults.innerHTML = `
        <div class="text-center py-4 text-gray-500">
          <div class="spinner"></div>
          <p>${searchingText}</p>
        </div>
      `;
    }

    const params = new URLSearchParams({
      q: query,
      start: "1",
      num: (krdictNum && krdictNum.value) || "10",
    });
    if (krdictPart && krdictPart.value) params.set("part", krdictPart.value);
    if (krdictMethod && krdictMethod.value)
      params.set("method", krdictMethod.value);

    try {
      const response = await fetch(`/api/krdict/search?${params.toString()}`);
      const result = await response.json();

      if (!response.ok) {
        const message = result.error
          ? result.error.message || "Unknown error"
          : "Search request failed";
        setKrdictStatus(message);
        if (krdictResults) {
          krdictResults.innerHTML = `
            <div class="text-center py-4 text-red-500">
              <p>${message}</p>
            </div>
          `;
        }
        return;
      }

      const items = result.items || [];
      if (items.length === 0) {
        const noResults = "No results found.";
        setKrdictStatus(noResults);
        if (krdictResults) {
          krdictResults.innerHTML = `
            <div class="text-center py-4 text-gray-500">
              <p>${noResults}</p>
              <p class="text-xs mt-1">Try a different word or search method.</p>
            </div>
          `;
        }
      } else {
        setKrdictStatus(""); // Clear status on success
        if (krdictResults) {
          krdictResults.innerHTML = items.map(renderKrdictItem).join("");
        }
      }
    } catch (error) {
      console.error("KRDIC search error:", error);
      const errorMsg = "Failed to process search request.";
      setKrdictStatus(errorMsg);
      if (krdictResults) {
        krdictResults.innerHTML = `
          <div class="text-center py-4 text-red-500">
            <p>${errorMsg}</p>
            <p class="text-xs mt-1">Check your network or server.</p>
          </div>
        `;
      }
    } finally {
      if (krdictSubmit) krdictSubmit.disabled = false;
    }
  }

  function closeKrdictWindow() {
    if (krdictWindow) krdictWindow.classList.add("hidden");
  }

  function openKrdictWindow() {
    if (!krdictWindow) return;
    krdictWindow.classList.remove("hidden");
    loadKrdictWidgetPreferences();
    setTimeout(() => krdictQuery?.focus(), 0);
  }

  // Helper function to escape HTML for display
  function escapeHtml(text) {
    const div = document.createElement("div");
    div.appendChild(document.createTextNode(text));
    return div.innerHTML;
  }

  // Scroll chat to bottom
  function scrollToBottom() {
    if (chatMessages) {
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  }

  // Add user message to chat
  function addUserMessage(text) {
    const messageDiv = document.createElement("div");
    messageDiv.className = "flex items-start space-x-3 justify-end";
    messageDiv.innerHTML = `
      <div class="flex-1 flex justify-end">
        <div class="bg-gradient-to-br from-orange-500 to-pink-500 rounded-2xl rounded-tr-sm p-4 shadow-sm max-w-[80%]">
          <p class="text-white">${escapeHtml(text)}</p>
        </div>
      </div>
      <div class="flex-shrink-0">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center text-white font-bold">
          Me
        </div>
      </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
  }

  // Add AI message to chat
  function addAIMessage(text) {
    const messageDiv = document.createElement("div");
    messageDiv.className = "flex items-start space-x-3";
    messageDiv.innerHTML = `
      <div class="flex-shrink-0">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-orange-400 to-pink-400 flex items-center justify-center text-white font-bold">
          AI
        </div>
      </div>
      <div class="flex-1">
        <div class="bg-white rounded-2xl rounded-tl-sm p-4 shadow-sm border border-gray-100">
          <p class="text-gray-800">${escapeHtml(text)
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\n/g, "<br>")}</p>
        </div>
      </div>
    `;
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
  }

  // Add typing indicator
  function addTypingIndicator() {
    const typingDiv = document.createElement("div");
    typingDiv.id = "typing-indicator";
    typingDiv.className = "flex items-start space-x-3";
    typingDiv.innerHTML = `
      <div class="flex-shrink-0">
        <div class="w-10 h-10 rounded-full bg-gradient-to-br from-orange-400 to-pink-400 flex items-center justify-center text-white font-bold">
          AI
        </div>
      </div>
      <div class="flex-1">
        <div class="bg-white rounded-2xl rounded-tl-sm p-4 shadow-sm border border-gray-100">
          <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    `;
    chatMessages.appendChild(typingDiv);
    scrollToBottom();
  }

  // Remove typing indicator
  function removeTypingIndicator() {
    const typingDiv = document.getElementById("typing-indicator");
    if (typingDiv) {
      typingDiv.remove();
    }
  }

  // Send message to AI
  async function sendMessage() {
    const query = userInput.value.trim();
    if (!query) return;

    addUserMessage(query);
    userInput.value = "";
    sendButton.disabled = true;
    addTypingIndicator();

    try {
      const response = await fetch("/api/chatbot", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: query }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("API Error:", errorData);
        throw new Error(
          `HTTP error! status: ${response.status}, details: ${errorData.detail || errorData.error}`,
        );
      }

      const data = await response.json();
      addAIMessage(data.response);
    } catch (error) {
      console.error("Error sending message:", error);
      const errMsg = (typeof translations !== 'undefined' && translations['toast.fetch_failed']) || "Sorry, an error occurred while processing your message.";
      addAIMessage(errMsg);
    } finally {
      removeTypingIndicator();
      sendButton.disabled = false;
      userInput.focus();
    }
  }

  // Event Listeners for Dictionary Widget
  if (krdictToggle) {
    krdictToggle.addEventListener("click", () => {
      if (!krdictWindow) return;
      const willOpen = krdictWindow.classList.contains("hidden");
      if (willOpen) openKrdictWindow();
      else closeKrdictWindow();
    });
  }

  if (krdictClose) {
    krdictClose.addEventListener("click", closeKrdictWindow);
  }

  if (krdictForm) {
    krdictForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const query = (krdictQuery?.value || "").trim();
      if (!query) {
        const alertMsg = (typeof translations !== 'undefined' && translations['toast.fill_all']) || "Please enter a search word.";
        setKrdictStatus(alertMsg);
        return;
      }
      saveKrdictWidgetPreferences();
      if (krdictSubmit) krdictSubmit.disabled = true;
      await fetchKrdictResults(query);
    });
  }

  if (krdictPart)
    krdictPart.addEventListener("change", saveKrdictWidgetPreferences);
  if (krdictMethod)
    krdictMethod.addEventListener("change", saveKrdictWidgetPreferences);
  if (krdictNum)
    krdictNum.addEventListener("change", saveKrdictWidgetPreferences);

  loadKrdictWidgetPreferences();

  // Close dictionary window when clicking outside
  document.addEventListener("click", (e) => {
    if (!krdictWindow || krdictWindow.classList.contains("hidden")) return;
    if (
      krdictWindow.contains(e.target) ||
      (krdictToggle && krdictToggle.contains(e.target))
    ) {
      return;
    }
    closeKrdictWindow();
  });

  // Close dictionary window with Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      closeKrdictWindow();
    }
  });

  // Event Listeners for Chatbot
  if (chatbotToggle) {
    chatbotToggle.addEventListener("click", () => {
      if (!chatbotWindow) return;
      const willOpen = chatbotWindow.classList.contains("hidden");
      if (willOpen) {
        chatbotWindow.classList.remove("hidden");
        setTimeout(() => userInput?.focus(), 0);
      } else {
        chatbotWindow.classList.add("hidden");
      }
    });
  }

  if (chatbotClose) {
    chatbotClose.addEventListener("click", () => {
      if (chatbotWindow) {
        chatbotWindow.classList.add("hidden");
      }
    });
  }

  if (sendButton) {
    sendButton.addEventListener("click", sendMessage);
  }

  if (userInput) {
    userInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        sendMessage();
      }
    });
  }

  suggestionButtons.forEach((button) => {
    button.addEventListener("click", () => {
      userInput.value = button.textContent.trim();
      sendMessage();
    });
  });

  // Close chatbot window when clicking outside (but not on chatbot-toggle itself)
  document.addEventListener("click", (e) => {
    if (!chatbotWindow || chatbotWindow.classList.contains("hidden")) return;
    if (
      chatbotWindow.contains(e.target) ||
      (chatbotToggle && chatbotToggle.contains(e.target))
    ) {
      return;
    }
    chatbotWindow.classList.add("hidden");
  });

  // Close chatbot window with Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      if (chatbotWindow) {
        chatbotWindow.classList.add("hidden");
      }
    }
  });
});
