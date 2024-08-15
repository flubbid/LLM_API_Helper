import os
import requests
from typing import List, Dict, Optional
import logging
import base64
import time
import json

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        logger.info("Initializing LLMService")
        self.claude_api_key = os.getenv('CLAUDE_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.claude_api_url = 'https://api.anthropic.com/v1/messages'
        self.openai_chat_url = 'https://api.openai.com/v1/chat/completions'
        self.openai_files_url = 'https://api.openai.com/v1/files'
        self.openai_assistants_url = 'https://api.openai.com/v1/assistants'
        self.openai_threads_url = 'https://api.openai.com/v1/threads'
        self.available_models = [
            'gpt-4-turbo',
            'gpt-3.5-turbo',
            'claude-3-sonnet-20240229'
        ]
        self.current_model = 'claude-3-sonnet-20240229'
        self.default_max_tokens = 4096
        self.openai_assistant_id = None
        self.openai_thread_id = None
        logger.info(f"Initial model set to: {self.current_model}")
        logger.debug(f"Claude API Key present: {'Yes' if self.claude_api_key else 'No'}")
        logger.debug(f"OpenAI API Key present: {'Yes' if self.openai_api_key else 'No'}")

    def set_model(self, model: str):
        logger.info(f"Attempting to set model to: {model}")
        if model in self.available_models:
            self.current_model = model
            logger.info(f"Model successfully set to: {self.current_model}")
            if model.startswith('gpt'):
                self._create_or_get_assistant()
                self._create_or_get_thread()
        else:
            logger.error(f"Unsupported model: {model}")
            raise ValueError(f"Unsupported model: {model}")

    def create_assistant(self, name, instructions):
        headers = {
            'Authorization': f'Bearer {self.openai_api_key}',
            'Content-Type': 'application/json',
            'OpenAI-Beta': 'assistants=v1'
        }
        data = {
            'model': self.current_model,
            'name': name,
            'instructions': instructions,
            'tools': [{'type': 'retrieval'}],
            'file_ids': []
        }
        try:
            logger.info(f"Creating new assistant with name: {name}")
            response = requests.post(self.openai_assistants_url, headers=headers, json=data)
            response.raise_for_status()
            assistant_data = response.json()
            assistant_id = assistant_data['id']
            logger.info(f"Created new OpenAI Assistant with ID: {assistant_id}")
            return assistant_id
        except requests.RequestException as e:
            logger.error(f"Error creating OpenAI Assistant: {e}", exc_info=True)
            if e.response is not None:
                logger.error(f"Response content: {e.response.content}")
            raise

    def _create_or_get_assistant(self):
        if not self.openai_assistant_id:
            logger.info("Creating or retrieving default assistant")
            self.openai_assistant_id = self.create_assistant(
                "Default Assistant",
                "You are a helpful assistant that can provide information and answer questions. ALWAYS respond in markdown format."
            )
        return self.openai_assistant_id

    def _create_or_get_thread(self):
        if not self.openai_thread_id:
            try:
                headers = {
                    'Authorization': f'Bearer {self.openai_api_key}',
                    'Content-Type': 'application/json',
                    'OpenAI-Beta': 'assistants=v1'
                }
                response = requests.post(self.openai_threads_url, headers=headers, json={})
                response.raise_for_status()
                self.openai_thread_id = response.json()['id']
                logger.info(f"Created new thread with ID: {self.openai_thread_id}")
            except requests.RequestException as e:
                logger.error(f"Error creating thread: {str(e)}")
                raise
        return self.openai_thread_id

    def call_llm(self, messages: List[Dict[str, str]], files: List[Dict] = None, assistant_id: str = None, max_tokens: int = None) -> Optional[str]:
        try:
            logger.info(f"Calling LLM with model: {self.current_model}")
            logger.debug(f"Messages: {messages}")
            logger.debug(f"Files: {files}")
            logger.debug(f"Max tokens: {max_tokens}")
            if assistant_id or self.current_model.startswith('gpt'):
                return self.call_openai_assistant(messages, files, assistant_id)
            elif self.current_model.startswith('claude'):
                return self.call_claude(messages, files, max_tokens)
            else:
                logger.error(f"Unknown model type: {self.current_model}")
                raise ValueError(f"Unknown model type: {self.current_model}")
        except Exception as e:
            logger.error(f"Error during LLM call: {e}", exc_info=True)
            raise

    def call_claude(self, messages: List[Dict[str, str]], files: List[Dict] = None, max_tokens: int = None) -> Optional[str]:
        headers = {
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01',
            'x-api-key': self.claude_api_key,
        }
        payload = {
            'model': self.current_model,
            'max_tokens': max_tokens or self.default_max_tokens,
            'messages': messages
        }
        
        try:
            logger.info(f"Sending request to Claude API with payload: {payload}")
            response = requests.post(self.claude_api_url, json=payload, headers=headers)
            response.raise_for_status()
            logger.info("Successfully received response from Claude API")
            response_data = response.json()
            
            if 'content' in response_data and response_data['content']:
                return response_data['content'][0]['text']
            else:
                logger.error(f"Unexpected response structure from Claude API: {response_data}")
                return "I apologize, but I encountered an unexpected response. Please try again."
        except requests.RequestException as e:
            logger.error(f"Error calling Claude API: {e}", exc_info=True)
            return "I'm sorry, but I experienced an error while processing your request. Please try again later."
        except (KeyError, IndexError) as e:
            logger.error(f"Error parsing Claude API response: {e}", exc_info=True)
            return "I apologize, but I had trouble understanding the response. Could you please rephrase your question?"

    def call_openai_assistant(self, messages, files=None, assistant_id=None):
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json',
                'OpenAI-Beta': 'assistants=v1'
            }

            if not assistant_id:
                assistant_id = self._create_or_get_assistant()

            thread_id = self._create_or_get_thread()

            new_message = messages[-1]
            message_data = {
                'role': new_message['role'],
                'content': new_message['content']
            }
            if files:
                message_data['file_ids'] = self.upload_files_to_openai(files)
            
            logger.info(f"Sending message to OpenAI thread")
            logger.debug(f"OpenAI message data: {json.dumps(message_data, indent=2)}")
            
            message_url = f"{self.openai_threads_url}/{thread_id}/messages"
            response = requests.post(message_url, headers=headers, json=message_data)
            response.raise_for_status()

            run_url = f"{self.openai_threads_url}/{thread_id}/runs"
            run_data = {'assistant_id': assistant_id}
            
            logger.info(f"Running OpenAI assistant")
            logger.debug(f"OpenAI run data: {json.dumps(run_data, indent=2)}")
            
            response = requests.post(run_url, headers=headers, json=run_data)
            response.raise_for_status()
            run_id = response.json()['id']

            while True:
                status_url = f"{run_url}/{run_id}"
                response = requests.get(status_url, headers=headers)
                response.raise_for_status()
                status = response.json()['status']
                logger.info(f"OpenAI run status: {status}")
                if status == 'completed':
                    break
                elif status in ['failed', 'cancelled', 'expired']:
                    logger.error(f"OpenAI Assistant run failed with status: {status}")
                    return None
                time.sleep(1)

            messages_url = f"{self.openai_threads_url}/{thread_id}/messages"
            response = requests.get(messages_url, headers=headers)
            response.raise_for_status()
            assistant_message = response.json()['data'][0]['content'][0]['text']['value']
            
            logger.info("Successfully received response from OpenAI Assistant")
            logger.debug(f"OpenAI Assistant response: {assistant_message}")

            return assistant_message

        except requests.RequestException as e:
            logger.error(f"Error in OpenAI API call: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error in call_openai_assistant: {str(e)}", exc_info=True)
            raise

    def upload_files_to_openai(self, files: List[Dict]) -> List[str]:
        file_ids = []
        for file in files:
            if 'source' in file and 'data' in file['source']:
                file_data = base64.b64decode(file['source']['data'])
            elif 'text' in file:
                file_data = file['text'].encode('utf-8')
            else:
                logger.warning(f"Skipping file upload for {file.get('name', 'unnamed file')}: No valid data found")
                continue

            files_data = {
                'file': (file['name'], file_data, file.get('type', 'application/octet-stream'))
            }
            data = {
                'purpose': 'assistants'
            }
            try:
                logger.info(f"Uploading file to OpenAI: {file['name']}")
                logger.debug(f"File upload data: {json.dumps(data, indent=2)}")
                response = requests.post(
                    self.openai_files_url,
                    headers={'Authorization': f'Bearer {self.openai_api_key}'},
                    files=files_data,
                    data=data
                )
                response.raise_for_status()
                file_id = response.json()['id']
                file_ids.append(file_id)
                logger.info(f"Successfully uploaded file to OpenAI with ID: {file_id}")
            except requests.RequestException as e:
                logger.error(f"Failed to upload file to OpenAI: {e}", exc_info=True)
        return file_ids