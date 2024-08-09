import os
import pytest
from flask import json
from app import create_app
from unittest.mock import patch, MagicMock

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_app():
    app = create_app()
    assert app is not None
    assert os.path.basename(app.static_folder) == 'static'
    assert app.static_url_path == '/static'

@patch('app.LLMService')
@patch('app.FileService')
def test_create_app_initializes_services(mock_file_service, mock_llm_service):
    create_app()
    mock_llm_service.assert_called_once()
    mock_file_service.assert_called_once()

@patch('app.register_routes')
def test_create_app_registers_routes(mock_register_routes):
    app = create_app()
    mock_register_routes.assert_called_once()

def test_index_route(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'LLM API UI Helper' in response.data

@patch('services.conversation_service.ConversationService.new_conversation')
def test_new_conversation_route(mock_new_conversation, client):
    mock_new_conversation.return_value = {"message": "New conversation started"}
    response = client.post('/new_conversation')
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "New conversation started"}

@patch('services.conversation_service.ConversationService.process_message')
def test_chat_route_success(mock_process_message, client):
    mock_process_message.return_value = "Test response from LLM"
    response = client.post('/chat', json={'message': 'Test message'})
    assert response.status_code == 200
    assert json.loads(response.data) == "Test response from LLM"
    mock_process_message.assert_called_once_with('Test message', [])

@patch('services.conversation_service.ConversationService.process_message')
def test_chat_route_with_files(mock_process_message, client):
    mock_process_message.return_value = "Test response with files"
    test_files = [{'type': 'image', 'data': 'base64encodeddata'}]
    response = client.post('/chat', json={'message': 'Test message', 'files': test_files})
    assert response.status_code == 200
    assert json.loads(response.data) == "Test response with files"
    mock_process_message.assert_called_once_with('Test message', test_files)

@patch('services.conversation_service.ConversationService.process_message')
@patch('services.llm_service.LLMService.set_model')
def test_chat_route_with_model_selection(mock_set_model, mock_process_message, client):
    mock_process_message.return_value = "Test response with model selection"
    response = client.post('/chat', json={'message': 'Test message', 'model': 'gpt-4'})
    assert response.status_code == 200
    assert json.loads(response.data) == "Test response with model selection"
    mock_set_model.assert_called_once_with('gpt-4')
    mock_process_message.assert_called_once_with('Test message', [])

@patch('services.conversation_service.ConversationService.process_message')
@patch('services.llm_service.LLMService.set_model')
def test_chat_route_with_invalid_model(mock_set_model, mock_process_message, client):
    mock_set_model.side_effect = ValueError("Invalid model")
    response = client.post('/chat', json={'message': 'Test message', 'model': 'invalid-model'})
    assert response.status_code == 400
    assert 'error' in json.loads(response.data)

@patch('services.conversation_service.ConversationService.process_message')
def test_chat_route_error(mock_process_message, client):
    mock_process_message.side_effect = Exception("Test error")
    response = client.post('/chat', json={'message': 'Test message'})
    assert response.status_code == 500
    assert 'error' in json.loads(response.data)

@patch('services.conversation_service.ConversationService.export_chat')
def test_export_chat_route(mock_export_chat, client):
    mock_export_chat.return_value = "Exported chat content"
    response = client.get('/export_chat')
    assert response.status_code == 200
    assert json.loads(response.data) == {"export": "Exported chat content"}

@patch('services.llm_service.LLMService.set_model')
def test_set_model_route_success(mock_set_model, client):
    response = client.post('/set_model', json={'model': 'gpt-4'})
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "Model set to gpt-4"}
    mock_set_model.assert_called_once_with('gpt-4')

@patch('services.llm_service.LLMService.set_model')
def test_set_model_route_error(mock_set_model, client):
    mock_set_model.side_effect = ValueError("Invalid model")
    response = client.post('/set_model', json={'model': 'invalid-model'})
    assert response.status_code == 400
    assert 'error' in json.loads(response.data)

def test_invalid_route(client):
    response = client.get('/invalid_route')
    assert response.status_code == 404