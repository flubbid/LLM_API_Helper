import os
import requests
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        logger.info("Initializing LLMService")
        self.claude_api_key = os.getenv('CLAUDE_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.claude_api_url = 'https://api.anthropic.com/v1/messages'
        self.openai_api_url = 'https://api.openai.com/v1/chat/completions'
        self.available_models = [
            'gpt-4',
            'gpt-4-turbo',
            'gpt-3.5-turbo',
            'claude-3-sonnet-20240229'  # Current Claude model
        ]
        self.current_model = 'claude-3-sonnet-20240229'  # Default model
        logger.info(f"Initial model set to: {self.current_model}")
        logger.debug(f"Claude API Key present: {'Yes' if self.claude_api_key else 'No'}")
        logger.debug(f"OpenAI API Key present: {'Yes' if self.openai_api_key else 'No'}")
    
    def switch_llm(self, llm_name):
        return self.set_model(llm_name)

    def set_model(self, model: str):
        logger.info(f"Attempting to set model to: {model}")
        if model in self.available_models:
            self.current_model = model
            logger.info(f"Model successfully set to: {self.current_model}")
        else:
            logger.error(f"Unsupported model: {model}")
            raise ValueError(f"Unsupported model: {model}")

    def call_llm(self, messages: List[Dict[str, str]]) -> Optional[str]:
        logger.info(f"Calling LLM with model: {self.current_model}")
        if self.current_model.startswith('gpt'):
            return self.call_chatgpt(messages)
        elif self.current_model.startswith('claude'):
            return self.call_claude(messages)
        else:
            logger.error(f"Unknown model type: {self.current_model}")
            return None

    def call_claude(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> Optional[str]:
        logger.info("Calling Claude API")
        headers = {
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01',
            'x-api-key': self.claude_api_key,
        }
        payload = {
            'model': self.current_model,
            'max_tokens': max_tokens,
            'messages': messages
        }
        try:
            logger.debug(f"Sending request to Claude API with payload: {payload}")
            response = requests.post(self.claude_api_url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info("Successfully received response from Claude API")
            return response.json()['content'][0]['text']
        except requests.RequestException as e:
            logger.error(f"Error calling Claude API: {e}")
            return None

    def call_chatgpt(self, messages: List[Dict[str, str]]) -> Optional[str]:
        logger.info(f"Calling ChatGPT API with model: {self.current_model}")
        headers = {
            'Authorization': f'Bearer {self.openai_api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': self.current_model,
            'messages': messages
        }
        try:
            logger.debug(f"Sending request to ChatGPT API with data: {data}")
            response = requests.post(self.openai_api_url, headers=headers, json=data)
            response.raise_for_status()
            logger.info("Successfully received response from ChatGPT API")
            return response.json()['choices'][0]['message']['content']
        except requests.RequestException as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return None
