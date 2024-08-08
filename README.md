# LLM API UI Helper

LLM API UI Helper is a versatile web-based interface for interacting with various Language Model APIs, including Claude and potentially others. This application supports text-based conversations, file uploads, and offers features like conversation export and dark mode.

This is currently under development. I am mainly just creating this to make using the APIs have a similar experience to the Chat GPT UI, to be able to avoid the monthly subscription fee, while still being able to utilize most of its features.

--Currently Only Supports Claude AI--

## Features

- Interactive chat interface
- Support for multiple LLM APIs (currently Claude, with potential for expansion)
- File upload and processing capability
- Dark mode
- Conversation export
- Syntax highlighting for code snippets
- Responsive design

## Technology Stack

- Backend: Python with Flask
- Frontend: HTML, CSS, JavaScript
- AI Integration: Anthropic's Claude API (with potential for other LLMs)

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.7+
- pip (Python package manager)
- An API key for Claude (or other LLMs you plan to use)

## Installation

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/LLM_Helper.git
   cd LLM_Helper
   ```

2. Create a virtual environment and activate it:

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required packages:

   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory and add your API keys:
   ```
   CLAUDE_API_KEY=your_claude_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here  # If using OpenAI
   ```

## Usage

1. Start the Flask server:

   ```
   python app.py
   ```

2. Open a web browser and navigate to `http://localhost:5000`

3. Start interacting with the LLM API through the UI!

## Project Structure

```
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
