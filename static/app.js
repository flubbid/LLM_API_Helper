document.addEventListener("DOMContentLoaded", () => {
  const elements = {
    chatContainer: document.getElementById("chat-container"),
    userInput: document.getElementById("user-input"),
    sendBtn: document.getElementById("send-btn"),
    clearHistoryBtn: document.getElementById("clear-history"),
    exportChatBtn: document.getElementById("export-chat"),
    darkModeToggle: document.getElementById("dark-mode-toggle"),
    dropZone: document.getElementById("drop-zone"),
    fileUpload: document.getElementById("file-upload"),
    settingsBtn: document.getElementById("settings-btn"),
    settingsModal: document.getElementById("settings-modal"),
    closeSettingsBtn: document.getElementById("close-settings"),
    fontSizeSlider: document.getElementById("font-size"),
    languageSelect: document.getElementById("language"),
    modelSelect: document.getElementById("model-select"),
    assistantModeCheckbox: document.getElementById("assistant-mode"),
    assistantModal: document.getElementById("assistant-modal"),
    createAssistantBtn: document.getElementById("create-assistant"),
    closeAssistantModalBtn: document.getElementById("close-assistant-modal"),
  };

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
      elements.modelSelect.innerHTML = "";

      // Add new options
      models.forEach((model) => {
        const option = document.createElement("option");
        option.value = model;
        option.textContent = model;
        elements.modelSelect.appendChild(option);
      });

      console.log("Model select initialized with available models");
    } catch (error) {
      console.error("Error initializing model select:", error);
    }
  }

  function handleFileUpload(file) {
    console.log("Handling file upload:", file.name, "Type:", file.type);
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        console.log(
          "File read successfully. Data length:",
          e.target.result.length
        );
        const fileType = file.type.startsWith("image/")
          ? "image"
          : file.type === "text/csv"
          ? "csv"
          : "code";
        console.log("Determined file type:", fileType);
        resolve({
          name: file.name,
          type: fileType,
          data: e.target.result.split(",")[1],
        });
      };
      reader.onerror = (error) => {
        console.error("Error reading file:", error);
        reject(error);
      };
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
      elements.assistantModal.style.display = "none";
    } catch (error) {
      console.error("Error creating assistant:", error);
      displayMessage("system", `Failed to create assistant: ${error.message}`);
    }
  }

  function displayMessage(role, content) {
    console.log(`Displaying ${role} message:`, content);
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message", `${role}-message`);

    // Ensure content is a string
    const contentString =
      typeof content === "object" ? JSON.stringify(content) : String(content);

    // Parse Markdown content
    const parsedContent = marked.parse(contentString);

    // Set inner HTML of message div
    messageDiv.innerHTML = parsedContent;

    if (elements.chatContainer) {
      elements.chatContainer.appendChild(messageDiv);
      elements.chatContainer.scrollTop = elements.chatContainer.scrollHeight;
    }

    // Apply syntax highlighting to code blocks
    messageDiv.querySelectorAll("pre code").forEach((block) => {
      hljs.highlightElement(block);
    });
  }

  async function sendMessage(message) {
    console.log("Sending message:", message);
    try {
      console.log("Selected model:", elements.modelSelect.value);
      const fileData = await Promise.all(
        selectedFiles.map((file) => handleFileUpload(file))
      );
      console.log("Processed file data:", fileData);
      const payload = {
        message,
        files: fileData,
        model: elements.modelSelect.value,
      };

      if (isAssistantMode && currentAssistantId) {
        payload.assistantId = currentAssistantId;
      }

      console.log(
        "Sending payload to server:",
        JSON.stringify(payload, null, 2)
      );

      const response = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      console.log("Response status:", response.status);

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      const data = await response.json();
      console.log("Received data from server:", data);
      displayMessage("assistant", data.message || data);
      selectedFiles = [];
      updateFileList();
      updateDropZoneText();
    } catch (error) {
      console.error("Error in sendMessage:", error);
      displayMessage("assistant", `Sorry, an error occurred: ${error.message}`);
    }
  }

  function updateDropZoneText() {
    if (elements.dropZone) {
      const dropZoneText = elements.dropZone.querySelector("p");
      if (dropZoneText) {
        dropZoneText.textContent =
          selectedFiles.length > 0
            ? `${selectedFiles.length} file(s) selected`
            : "Drag & drop files here or click to select";
      }
    }
  }

  function handleFiles(files) {
    console.log("Handling file upload", files);
    Array.from(files).forEach((file) => {
      console.log("Processing file:", file.name, "Type:", file.type);
      if (
        !selectedFiles.some((existingFile) => existingFile.name === file.name)
      ) {
        selectedFiles.push(file);
        console.log("File added to selectedFiles:", file.name);
      } else {
        console.log("File already exists in selectedFiles:", file.name);
      }
    });
    updateDropZoneText();
    updateFileList();
  }

  function updateFileList() {
    console.log("Updating file list", selectedFiles);
    const fileListContainer = document.getElementById("file-list");
    if (fileListContainer) {
      fileListContainer.innerHTML = "";
      selectedFiles.forEach((file, index) => {
        console.log("Adding file to list:", file.name, "Index:", index);
        const fileItem = document.createElement("div");
        fileItem.className = "file-item";
        fileItem.innerHTML = `
        <span>${file.name}</span>
        <button onclick="window.removeFile(${index})">Remove</button>
      `;
        fileListContainer.appendChild(fileItem);
      });
    } else {
      console.error("File list container not found");
    }
  }

  function removeFile(index) {
    console.log(`Removing file at index ${index}`);
    selectedFiles.splice(index, 1);
    updateFileList();
    updateDropZoneText();
  }

  // Make removeFile available globally
  window.removeFile = removeFile;

  // Event listeners
  elements.sendBtn?.addEventListener("click", () => {
    const message = elements.userInput.value.trim();
    if (message || selectedFiles.length > 0) {
      displayMessage("user", message);
      sendMessage(message);
      elements.userInput.value = "";
    }
  });

  elements.userInput?.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      elements.sendBtn?.click();
    }
  });

  elements.clearHistoryBtn?.addEventListener("click", async () => {
    try {
      const response = await fetch("/new_conversation", { method: "POST" });
      if (response.ok) {
        elements.chatContainer.innerHTML = "";
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

  elements.exportChatBtn?.addEventListener("click", () => {
    // ... (export chat functionality)
  });

  elements.darkModeToggle?.addEventListener("click", () => {
    document.body.classList.toggle("dark-mode");
  });

  elements.dropZone?.addEventListener("dragover", (e) => {
    e.preventDefault();
    elements.dropZone.classList.add("dragover");
  });

  elements.dropZone?.addEventListener("dragleave", () => {
    elements.dropZone.classList.remove("dragover");
  });

  elements.dropZone?.addEventListener("drop", (e) => {
    e.preventDefault();
    elements.dropZone.classList.remove("dragover");
    handleFiles(e.dataTransfer.files);
  });

  elements.dropZone?.addEventListener("click", () => {
    elements.fileUpload?.click();
  });

  elements.fileUpload?.addEventListener("change", (event) => {
    handleFiles(event.target.files);
  });

  elements.userInput?.addEventListener("paste", (e) => {
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
  elements.settingsBtn?.addEventListener("click", () => {
    elements.settingsModal.style.display = "block";
  });

  elements.closeSettingsBtn?.addEventListener("click", () => {
    elements.settingsModal.style.display = "none";
  });

  elements.fontSizeSlider?.addEventListener("input", (e) => {
    document.body.style.fontSize = `${e.target.value}px`;
  });

  elements.languageSelect?.addEventListener("change", (e) => {
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

  elements.assistantModeCheckbox?.addEventListener("change", (e) => {
    isAssistantMode = e.target.checked;
    if (isAssistantMode && !currentAssistantId) {
      elements.assistantModal.style.display = "block";
    }
  });

  elements.createAssistantBtn?.addEventListener("click", () => {
    const name = document.getElementById("assistant-name")?.value;
    const instructions = document.getElementById(
      "assistant-instructions"
    )?.value;
    if (name && instructions) {
      createAssistant(name, instructions);
    } else {
      displayMessage(
        "system",
        "Please provide a name and instructions for the assistant."
      );
    }
  });

  elements.closeAssistantModalBtn?.addEventListener("click", () => {
    elements.assistantModal.style.display = "none";
  });

  // Initial message
  displayMessage("assistant", "Hello! How can I assist you today?");
});
