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
        self.current_llm = 'claude'  # or 'chatgpt'
        logger.info(f"Initial LLM set to: {self.current_llm}")
        logger.debug(f"Claude API Key present: {'Yes' if self.claude_api_key else 'No'}")
        logger.debug(f"OpenAI API Key present: {'Yes' if self.openai_api_key else 'No'}")

    def switch_llm(self, llm_name: str):
        logger.info(f"Attempting to switch LLM to: {llm_name}")
        if llm_name in ['claude', 'chatgpt']:
            self.current_llm = llm_name
            logger.info(f"Successfully switched LLM to: {self.current_llm}")
        else:
            logger.error(f"Unsupported LLM: {llm_name}")
            raise ValueError(f"Unsupported LLM: {llm_name}")

    def call_claude(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> Optional[str]:
        logger.info("Calling Claude API")
        headers = {
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01',
            'x-api-key': self.claude_api_key,
        }
        payload = {
            'model': 'claude-3-sonnet-20240229',
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

    def call_chatgpt(self, messages: List[Dict[str, str]], model: str = 'gpt-3.5-turbo') -> Optional[str]:
        logger.info("Calling ChatGPT API")
        headers = {
            'Authorization': f'Bearer {self.openai_api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': model,
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

    def call_llm(self, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        logger.info(f"Calling LLM: {self.current_llm}")
        if self.current_llm == 'claude':
            logger.info("Delegating to call_claude method")
            return self.call_claude(messages, **kwargs)
        elif self.current_llm == 'chatgpt':
            logger.info("Delegating to call_chatgpt method")
            return self.call_chatgpt(messages, **kwargs)
        else:
            logger.error(f"Unknown LLM: {self.current_llm}")
            return None