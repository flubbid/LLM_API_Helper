import pytest
from unittest.mock import patch, MagicMock
from services.llm_service import LLMService
import os
import requests

@pytest.fixture
def llm_service():
    # Set up environment variables for testing
    os.environ['CLAUDE_API_KEY'] = 'test_claude_key'
    os.environ['OPENAI_API_KEY'] = 'test_openai_key'
    return LLMService()

def test_init(llm_service):
    assert llm_service.claude_api_key == 'test_claude_key'
    assert llm_service.openai_api_key == 'test_openai_key'
    assert llm_service.claude_api_url == 'https://api.anthropic.com/v1/messages'
    assert llm_service.openai_api_url == 'https://api.openai.com/v1/chat/completions'
    assert llm_service.current_model == 'claude-3-sonnet-20240229'

def test_switch_llm(llm_service):
    llm_service.switch_llm('gpt-4')
    assert llm_service.current_model == 'gpt-4'

    with pytest.raises(ValueError):
        llm_service.switch_llm('invalid-model')

def test_set_model(llm_service):
    llm_service.set_model('gpt-3.5-turbo')
    assert llm_service.current_model == 'gpt-3.5-turbo'

    with pytest.raises(ValueError):
        llm_service.set_model('invalid-model')

@patch('services.llm_service.LLMService.call_claude')
@patch('services.llm_service.LLMService.call_chatgpt')
def test_call_llm(mock_call_chatgpt, mock_call_claude, llm_service):
    messages = [{'role': 'user', 'content': 'Test message'}]

    # Test Claude model
    llm_service.current_model = 'claude-3-sonnet-20240229'
    mock_call_claude.return_value = 'Claude response'
    assert llm_service.call_llm(messages) == 'Claude response'
    mock_call_claude.assert_called_once_with(messages)

    # Test GPT model
    llm_service.current_model = 'gpt-4'
    mock_call_chatgpt.return_value = 'GPT response'
    assert llm_service.call_llm(messages) == 'GPT response'
    mock_call_chatgpt.assert_called_once_with(messages)

    # Test unknown model
    llm_service.current_model = 'unknown-model'
    assert llm_service.call_llm(messages) is None

@patch('services.llm_service.requests.post')
def test_call_claude_success(mock_post, llm_service):
    mock_response = MagicMock()
    mock_response.json.return_value = {'content': [{'text': 'Claude test response'}]}
    mock_post.return_value = mock_response

    messages = [{'role': 'user', 'content': 'Test message'}]
    result = llm_service.call_claude(messages)

    assert result == 'Claude test response'
    mock_post.assert_called_once_with(
        llm_service.claude_api_url,
        json={
            'model': 'claude-3-sonnet-20240229',
            'max_tokens': 1000,
            'messages': messages
        },
        headers={
            'Content-Type': 'application/json',
            'anthropic-version': '2023-06-01',
            'x-api-key': 'test_claude_key',
        }
    )

@patch('services.llm_service.requests.post')
def test_call_claude_error(mock_post, llm_service):
    mock_post.side_effect = requests.RequestException("API error")

    messages = [{'role': 'user', 'content': 'Test message'}]
    result = llm_service.call_claude(messages)

    assert result is None
    mock_post.assert_called_once()

@patch('services.llm_service.requests.post')
def test_call_chatgpt_success(mock_post, llm_service):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        'choices': [{'message': {'content': 'GPT test response'}}]
    }
    mock_post.return_value = mock_response

    messages = [{'role': 'user', 'content': 'Test message'}]
    result = llm_service.call_chatgpt(messages)

    assert result == 'GPT test response'
    mock_post.assert_called_once_with(
        llm_service.openai_api_url,
        headers={
            'Authorization': 'Bearer test_openai_key',
            'Content-Type': 'application/json'
        },
        json={
            'model': 'claude-3-sonnet-20240229',
            'messages': messages
        }
    )

@patch('services.llm_service.requests.post')
def test_call_chatgpt_error(mock_post, llm_service):
    mock_post.side_effect = requests.RequestException("API error")

    messages = [{'role': 'user', 'content': 'Test message'}]
    result = llm_service.call_chatgpt(messages)

    assert result is None
    mock_post.assert_called_once()