import os
import requests
from typing import List, Dict, Optional

class LLMService:
    def __init__(self):
        self.claude_api_key = os.getenv('CLAUDE_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.claude_api_url = 'https://api.anthropic.com/v1/messages'
        self.openai_api_url = 'https://api.openai.com/v1/chat/completions'

    def call_claude(self, messages: List[Dict[str, str]], max_tokens: int = 1000) -> Optional[str]:
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
            response = requests.post(self.claude_api_url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()['content'][0]['text']
        except requests.RequestException as e:
            print(f"Error calling Claude API: {e}")
            return None

    def call_chatgpt(self, messages: List[Dict[str, str]], model: str = 'gpt-3.5-turbo') -> Optional[str]:
        headers = {
            'Authorization': f'Bearer {self.openai_api_key}',
            'Content-Type': 'application/json'
        }
        data = {
            'model': model,
            'messages': messages
        }
        try:
            response = requests.post(self.openai_api_url, headers=headers, json=data)
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        except requests.RequestException as e:
            print(f"Error calling OpenAI API: {e}")
            return None

    def call_llm(self, llm_name: str, messages: List[Dict[str, str]], **kwargs) -> Optional[str]:
        if llm_name == 'claude':
            return self.call_claude(messages, **kwargs)
        elif llm_name == 'chatgpt':
            return self.call_chatgpt(messages, **kwargs)
        else:
            raise ValueError(f"Unsupported LLM: {llm_name}")