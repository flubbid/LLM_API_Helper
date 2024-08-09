# LLM API UI Helper

LLM API UI Helper is a versatile web-based interface for interacting with various Language Model APIs, including Claude and potentially others. This application supports text-based conversations, file uploads, and offers features like conversation export and dark mode.

This is currently under development. The primary goal is to create a similar user experience to the ChatGPT UI, avoiding subscription fees while still utilizing most of its features.

## Features

- Interactive chat interface
- Support for multiple LLM APIs (currently Claude, with potential for expansion)
- File upload and processing capability
  - Supports images, CSVs, and code files
- Dark mode toggle
- Conversation export to text file
- Syntax highlighting for code snippets
- Responsive design
- Customizable font size
- Model selection from available LLMs

## Technology Stack

- **Backend:** Python with Flask
- **Frontend:** HTML, CSS, JavaScript
- **AI Integration:** Anthropic's Claude API (with potential for other LLMs)

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7+
- pip (Python package manager)
- An API key for Claude (or other LLMs you plan to use)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/LLM_Helper.git
   cd LLM_Helper
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add your API keys:

   ```bash
   CLAUDE_API_KEY=your_claude_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here  # If using OpenAI
   ```

## Usage

1. Start the Flask server:

   ```bash
   python app.py
   ```

2. Open a web browser and navigate to `http://localhost:5000`

3. Start interacting with the LLM API through the UI!

## Project Structure

```plaintext
LLM_Helper/
│
├── static/
│   ├── styles.css
│   └── app.js
├── templates/
│   └── index.html
├── services/
│   ├── conversation_service.py
│   ├── file_service.py
│   └── llm_service.py
├── .env
├── app.py
├── requirements.txt
└── README.md
```

## Routes

- `/` - Main index page, serves the frontend.
- `/new_conversation` - POST, initializes a new conversation.
- `/chat` - POST, sends a message to the selected LLM and receives a response.
- `/export_chat` - GET, exports the current conversation history.
- `/set_model` - POST, sets the model to be used by the LLM service.

## Services

- **LLMService**: Handles communication with the LLM APIs.
- **FileService**: Processes different types of files (images, CSVs, code).
- **ConversationService**: Manages conversation history and handles messages.

## Logging and Debugging

Logging is configured to provide detailed information during execution. The logs will display:

- Initialization of services.
- API requests and responses.
- Errors encountered during execution.

You can view logs in the console to help with debugging and ensuring proper functioning.

## Contributing

Contributions are welcome! Please fork the repository and create a pull request.

## License

This project is licensed under the MIT License.
