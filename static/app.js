document.addEventListener("DOMContentLoaded", () => {
  const chatContainer = document.getElementById("chat-container");
  const userInput = document.getElementById("user-input");
  const sendBtn = document.getElementById("send-btn");
  const clearHistoryBtn = document.getElementById("clear-history");
  const exportChatBtn = document.getElementById("export-chat");
  const darkModeToggle = document.getElementById("dark-mode-toggle");
  const dropZone = document.getElementById("drop-zone");
  const fileUpload = document.getElementById("file-upload");
  const settingsBtn = document.getElementById("settings-btn");
  const settingsModal = document.getElementById("settings-modal");
  const closeSettingsBtn = document.getElementById("close-settings");
  const fontSizeSlider = document.getElementById("font-size");
  const languageSelect = document.getElementById("language");
  const modelSelect = document.getElementById("model-select");
  initializeModelSelect();
  let selectedFiles = [];

  // File handling functions
  function handleFiles(files) {
    Array.from(files).forEach((file) => {
      if (
        !selectedFiles.some((existingFile) => existingFile.name === file.name)
      ) {
        selectedFiles.push(file);
      }
    });
    updateDropZoneText();
    updateFileList();
  }

  function updateDropZoneText() {
    const dropZoneText = dropZone.querySelector("p");
    dropZoneText.textContent =
      selectedFiles.length > 0
        ? `${selectedFiles.length} file(s) selected`
        : "Drag & drop files here or click to select";
  }

  function updateFileList() {
    const fileListContainer = document.getElementById("file-list");
    if (fileListContainer) {
      fileListContainer.innerHTML = "";
      selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement("div");
        fileItem.className = "file-item";
        fileItem.innerHTML = `
                <span>${file.name}</span>
                <button onclick="removeFile(${index})">Remove</button>
            `;
        fileListContainer.appendChild(fileItem);
      });
    }
  }

  function removeFile(index) {
    selectedFiles.splice(index, 1);
    updateFileList();
    updateDropZoneText();
  }

  // Message display and formatting
  function displayMessage(role, content) {
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", `${role}-message`);
    const timestamp = new Date().toLocaleTimeString();
    messageDiv.innerHTML = `
            <div class="message-timestamp">${timestamp}</div>
            <div class="message-content">${formatMessage(content)}</div>
        `;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    hljs.highlightAll();
  }

  function formatMessage(content) {
    return content.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
      const language = lang || "plaintext";
      const highlightedCode = hljs.highlight(code.trim(), { language }).value;
      return `
                <div class="code-block">
                    <div class="code-header">
                        <span class="code-language">${language}</span>
                        <button class="copy-code-btn" data-language="${language}">Copy ${language}</button>
                    </div>
                    <pre><code class="hljs ${language}">${highlightedCode}</code></pre>
                </div>
            `;
    });
  }

  // API communication
  async function sendMessage(message) {
    try {
      console.log("Sending message:", message); // Add this log
      console.log("Selected model:", modelSelect.value); // Add this log
      const fileData = await Promise.all(selectedFiles.map(handleFileUpload));
      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message,
          files: fileData,
          model: modelSelect.value,
        }),
      });

      console.log("Response status:", response.status); // Add this log

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      console.log("Received data:", data); // Add this log
      displayMessage("assistant", data.message || data);
      selectedFiles = [];
      updateFileList();
      updateDropZoneText();
    } catch (error) {
      console.error("Error in sendMessage:", error);
      displayMessage("assistant", `Sorry, an error occurred: ${error.message}`);
    }
  }
  function handleFileUpload(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (event) => {
        resolve({
          type: getFileType(file),
          data: event.target.result.split(",")[1],
          name: file.name,
          size: file.size,
        });
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  function getFileType(file) {
    const extension = file.name.split(".").pop().toLowerCase();
    if (file.type.startsWith("image/")) return "image";
    if (file.type === "text/csv" || extension === "csv") return "csv";
    if (["js", "py", "html", "css", "txt"].includes(extension)) return "code";
    return "unknown";
  }

  function initializeModelSelect() {
    // Set the default model (should match the default in your LLMService)
    modelSelect.value = "claude-3-sonnet-20240229";
  }

  // Event listeners
  modelSelect.addEventListener("change", async (e) => {
    const model = e.target.value;
    try {
      const response = await fetch("/set_model", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model }),
      });
      if (!response.ok) throw new Error("Failed to set model");
      const data = await response.json();
      displayMessage("assistant", data.message);
    } catch (error) {
      console.error("Error setting model:", error);
      displayMessage("assistant", `Failed to set model: ${error.message}`);
    }
  });

  // document
  //   .getElementById("model-select")
  //   .addEventListener("change", async (e) => {
  //     const llm = e.target.value;
  //     try {
  //       const response = await fetch("/switch_llm", {
  //         method: "POST",
  //         headers: { "Content-Type": "application/json" },
  //         body: JSON.stringify({ llm }),
  //       });
  //       if (!response.ok) throw new Error("Failed to switch LLM");
  //       const data = await response.json();
  //       displayMessage("assistant", data.message);
  //     } catch (error) {
  //       console.error("Error switching LLM:", error);
  //       displayMessage("assistant", `Failed to switch LLM: ${error.message}`);
  //     }
  //   });

  sendBtn.addEventListener("click", () => {
    const message = userInput.value.trim();
    if (message || selectedFiles.length > 0) {
      displayMessage("user", message);
      sendMessage(message);
      userInput.value = "";
    }
  });

  userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendBtn.click();
    }
  });

  clearHistoryBtn.addEventListener("click", async () => {
    try {
      const response = await fetch("/new_conversation", { method: "POST" });
      if (response.ok) {
        chatContainer.innerHTML = "";
        displayMessage(
          "assistant",
          "New conversation started. How can I help you?"
        );
      } else {
        throw new Error("Failed to start new conversation");
      }
    } catch (error) {
      console.error("Error:", error);
      displayMessage(
        "assistant",
        "Failed to start a new conversation. Please try again."
      );
    }
  });

  exportChatBtn.addEventListener("click", () => {
    const chatContent = Array.from(chatContainer.children)
      .map((msg) => {
        const role = msg.classList.contains("user-message")
          ? "User"
          : "Assistant";
        const content = msg.querySelector(".message-content").textContent;
        return `${role}: ${content}\n`;
      })
      .join("\n");

    const blob = new Blob([chatContent], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "chat_export.txt";
    a.click();
    URL.revokeObjectURL(url);
  });

  darkModeToggle.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    handleFiles(e.dataTransfer.files);
  });

  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
  });

  dropZone.addEventListener("click", () => {
    fileUpload.click();
  });

  fileUpload.addEventListener("change", (event) => {
    handleFiles(event.target.files);
  });

  userInput.addEventListener("paste", (e) => {
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.indexOf("image") !== -1) {
        const blob = items[i].getAsFile();
        handleFiles([blob]);
        e.preventDefault();
        break;
      }
    }
  });

  // Settings modal
  settingsBtn.addEventListener("click", () => {
    settingsModal.style.display = "block";
  });

  closeSettingsBtn.addEventListener("click", () => {
    settingsModal.style.display = "none";
  });

  fontSizeSlider.addEventListener("input", (e) => {
    document.body.style.fontSize = `${e.target.value}px`;
  });

  languageSelect.addEventListener("change", (e) => {
    // Here you would implement language change logic
    console.log(`Language changed to ${e.target.value}`);
  });

  // Copy code functionality
  document.addEventListener("click", (e) => {
    if (e.target.classList.contains("copy-code-btn")) {
      const codeBlock = e.target.closest(".code-block");
      const code = codeBlock.querySelector("code").textContent;
      navigator.clipboard.writeText(code).then(() => {
        e.target.textContent = "Copied!";
        setTimeout(() => {
          e.target.textContent = `Copy ${e.target.dataset.language}`;
        }, 2000);
      });
    }
  });

  // Initial message
  displayMessage("assistant", "Hello! How can I assist you today?");
});
