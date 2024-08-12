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
  const assistantModeCheckbox = document.getElementById("assistant-mode");
  const assistantModal = document.getElementById("assistant-modal");
  const createAssistantBtn = document.getElementById("create-assistant");
  const closeAssistantModalBtn = document.getElementById(
    "close-assistant-modal"
  );

  let selectedFiles = [];
  let isAssistantMode = false;
  let currentAssistantId = null;

  console.log("Initializing app.js");

  initializeModelSelect();

  async function initializeModelSelect() {
    console.log("Initializing model select");
    try {
      const response = await fetch("/get_available_models");
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const models = await response.json();

      // Clear existing options
      modelSelect.innerHTML = "";

      // Add new options
      models.forEach((model) => {
        const option = document.createElement("option");
        option.value = model;
        option.textContent = model;
        modelSelect.appendChild(option);
      });

      console.log("Model select initialized with available models");
    } catch (error) {
      console.error("Error initializing model select:", error);
    }
  }

  function handleFileUpload(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        resolve({
          name: file.name,
          type: file.type.startsWith("image/")
            ? "image"
            : file.type === "text/csv"
            ? "csv"
            : "code",
          data: e.target.result.split(",")[1],
        });
      };
      reader.onerror = (error) => reject(error);
      reader.readAsDataURL(file);
    });
  }

  async function createAssistant(name, instructions) {
    try {
      const response = await fetch("/create_assistant", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name, instructions }),
      });

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      const data = await response.json();
      currentAssistantId = data.assistantId;
      displayMessage("system", `Assistant "${name}" created successfully.`);
      assistantModal.style.display = "none";
    } catch (error) {
      console.error("Error creating assistant:", error);
      displayMessage("system", `Failed to create assistant: ${error.message}`);
    }
  }

  function displayMessage(role, content) {
    console.log(`Displaying ${role} message:`, content);
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", `${role}-message`);

    // Parse Markdown content
    const parsedContent = marked.parse(content);

    // Set inner HTML of message div
    messageDiv.innerHTML = parsedContent;

    if (chatContainer) {
      chatContainer.appendChild(messageDiv);
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Apply syntax highlighting to code blocks
    messageDiv.querySelectorAll("pre code").forEach((block) => {
      hljs.highlightElement(block);
    });
  }

  async function sendMessage(message) {
    console.log("Sending message:", message);
    try {
      console.log("Selected model:", modelSelect.value);
      const fileData = await Promise.all(
        selectedFiles.map((file) => handleFileUpload(file))
      );
      const payload = {
        message,
        files: fileData,
        model: modelSelect.value,
      };

      if (isAssistantMode && currentAssistantId) {
        payload.assistantId = currentAssistantId;
      }

      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      console.log("Response status:", response.status);

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }

      function updateDropZoneText() {
        console.log("Updating drop zone text");
        if (dropZone) {
          const dropZoneText = dropZone.querySelector("p");
          if (dropZoneText) {
            dropZoneText.textContent =
              selectedFiles.length > 0
                ? `${selectedFiles.length} file(s) selected`
                : "Drag & drop files here or click to select";
          }
        }
      }

      const data = await response.json();
      console.log("Received data:", data);
      displayMessage("assistant", data.message || data);
      selectedFiles = [];
      updateFileList();
      updateDropZoneText();
    } catch (error) {
      console.error("Error in sendMessage:", error);
      displayMessage("assistant", `Sorry, an error occurred: ${error.message}`);
    }
  }

  function handleFiles(files) {
    console.log("Handling file upload", files);
    Array.from(files).forEach((file) => {
      if (
        !selectedFiles.some((existingFile) => existingFile.name === file.name)
      ) {
        selectedFiles.push(file);
      }
      updateDropZoneText();
      updateFileList();
    });
  }

  function updateFileList() {
    console.log("Updating file list", selectedFiles);
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
    console.log(`Removing file at index ${index}`);
    selectedFiles.splice(index, 1);
    updateFileList();
    updateDropZoneText();
  }

  // Add event listeners only if the elements exist
  if (sendBtn) {
    sendBtn.addEventListener("click", () => {
      const message = userInput.value.trim();
      if (message || selectedFiles.length > 0) {
        displayMessage("user", message);
        sendMessage(message);
        userInput.value = "";
      }
    });
  }

  if (userInput) {
    userInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendBtn.click();
      }
    });
  }
  if (clearHistoryBtn)
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

  if (exportChatBtn)
    exportChatBtn.addEventListener("click", () => {
      // ... (export chat functionality)
    });

  if (darkModeToggle)
    darkModeToggle.addEventListener("click", () => {
      document.body.classList.toggle("dark-mode");
    });

  if (dropZone) {
    dropZone.addEventListener("dragover", (e) => {
      e.preventDefault();
      dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => {
      dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", (e) => {
      e.preventDefault();
      dropZone.classList.remove("dragover");
      handleFiles(e.dataTransfer.files);
    });

    dropZone.addEventListener("click", () => {
      fileUpload.click();
    });
  }

  if (fileUpload)
    fileUpload.addEventListener("change", (event) => {
      handleFiles(event.target.files);
    });

  if (userInput)
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

  assistantModeCheckbox.addEventListener("change", (e) => {
    isAssistantMode = e.target.checked;
    if (isAssistantMode && !currentAssistantId) {
      assistantModal.style.display = "block";
    }
  });

  createAssistantBtn.addEventListener("click", () => {
    const name = document.getElementById("assistant-name").value;
    const instructions = document.getElementById(
      "assistant-instructions"
    ).value;
    if (name && instructions) {
      createAssistant(name, instructions);
    } else {
      displayMessage(
        "system",
        "Please provide a name and instructions for the assistant."
      );
    }
  });

  closeAssistantModalBtn.addEventListener("click", () => {
    assistantModal.style.display = "none";
  });

  // Initial message
  displayMessage("assistant", "Hello! How can I assist you today?");
});

// Make removeFile available globally
window.removeFile = removeFile;
