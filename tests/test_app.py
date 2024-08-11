import os
import pytest
from flask import json
from app import create_app
from unittest.mock import patch, MagicMock
import logging

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@pytest.fixture
def client():
    logger.info("Setting up Flask test client")
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_create_app():
    logger.info("Testing app creation")
    app = create_app()
    assert app is not None
    assert os.path.basename(app.static_folder) == 'static'
    assert app.static_url_path == '/static'
    logger.info("App creation test passed")

@patch('app.LLMService')
@patch('app.FileService')
def test_create_app_initializes_services(mock_file_service, mock_llm_service):
    logger.info("Testing service initialization during app creation")
    create_app()
    mock_llm_service.assert_called_once()
    mock_file_service.assert_called_once()
    logger.info("Service initialization test passed")

@patch('app.register_routes')
def test_create_app_registers_routes(mock_register_routes):
    logger.info("Testing route registration during app creation")
    app = create_app()
    mock_register_routes.assert_called_once()
    logger.info("Route registration test passed")

def test_index_route(client):
    logger.info("Testing index route")
    response = client.get('/')
    assert response.status_code == 200
    assert b'LLM API UI Helper' in response.data
    logger.info("Index route test passed")

@patch('services.conversation_service.ConversationService.new_conversation')
def test_new_conversation_route(mock_new_conversation, client):
    logger.info("Testing new conversation route")
    mock_new_conversation.return_value = {"message": "New conversation started"}
    response = client.post('/new_conversation')
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "New conversation started"}
    logger.info("New conversation route test passed")

@patch('services.conversation_service.ConversationService.process_message')
def test_chat_route_success(mock_process_message, client):
    logger.info("Testing chat route success")
    mock_process_message.return_value = "Test response from LLM"
    response = client.post('/chat', json={'message': 'Test message'})
    assert response.status_code == 200
    assert json.loads(response.data) == "Test response from LLM"
    mock_process_message.assert_called_once_with('Test message', [])
    logger.info("Chat route success test passed")

@patch('services.conversation_service.ConversationService.process_message')
def test_chat_route_with_files(mock_process_message, client):
    logger.info("Testing chat route with files")
    mock_process_message.return_value = "Test response with files"
    test_files = [{'type': 'image', 'data': 'base64encodeddata'}]
    response = client.post('/chat', json={'message': 'Test message', 'files': test_files})
    assert response.status_code == 200
    assert json.loads(response.data) == "Test response with files"
    mock_process_message.assert_called_once_with('Test message', test_files)
    logger.info("Chat route with files test passed")

@patch('services.conversation_service.ConversationService.process_message')
@patch('services.llm_service.LLMService.set_model')
def test_chat_route_with_model_selection(mock_set_model, mock_process_message, client):
    logger.info("Testing chat route with model selection")
    mock_process_message.return_value = "Test response with model selection"
    response = client.post('/chat', json={'message': 'Test message', 'model': 'gpt-4'})
    assert response.status_code == 200
    assert json.loads(response.data) == "Test response with model selection"
    mock_set_model.assert_called_once_with('gpt-4')
    mock_process_message.assert_called_once_with('Test message', [])
    logger.info("Chat route with model selection test passed")

@patch('services.conversation_service.ConversationService.process_message')
@patch('services.llm_service.LLMService.set_model')
def test_chat_route_with_invalid_model(mock_set_model, mock_process_message, client):
    logger.info("Testing chat route with invalid model")
    mock_set_model.side_effect = ValueError("Invalid model")
    response = client.post('/chat', json={'message': 'Test message', 'model': 'invalid-model'})
    assert response.status_code == 400
    assert 'error' in json.loads(response.data)
    logger.info("Chat route with invalid model test passed")

@patch('services.conversation_service.ConversationService.process_message')
def test_chat_route_error(mock_process_message, client):
    logger.info("Testing chat route error handling")
    mock_process_message.side_effect = Exception("Test error")
    response = client.post('/chat', json={'message': 'Test message'})
    assert response.status_code == 500
    assert 'error' in json.loads(response.data)
    logger.info("Chat route error handling test passed")

@patch('services.conversation_service.ConversationService.export_chat')
def test_export_chat_route(mock_export_chat, client):
    logger.info("Testing export chat route")
    mock_export_chat.return_value = "Exported chat content"
    response = client.get('/export_chat')
    assert response.status_code == 200
    assert json.loads(response.data) == {"export": "Exported chat content"}
    logger.info("Export chat route test passed")

@patch('services.llm_service.LLMService.set_model')
def test_set_model_route_success(mock_set_model, client):
    logger.info("Testing set model route success")
    response = client.post('/set_model', json={'model': 'gpt-4'})
    assert response.status_code == 200
    assert json.loads(response.data) == {"message": "Model set to gpt-4"}
    mock_set_model.assert_called_once_with('gpt-4')
    logger.info("Set model route success test passed")

@patch('services.llm_service.LLMService.set_model')
def test_set_model_route_error(mock_set_model, client):
    logger.info("Testing set model route error handling")
    mock_set_model.side_effect = ValueError("Invalid model")
    response = client.post('/set_model', json={'model': 'invalid-model'})
    assert response.status_code == 400
    assert 'error' in json.loads(response.data)
    logger.info("Set model route error handling test passed")

def test_invalid_route(client):
    logger.info("Testing invalid route")
    response = client.get('/invalid_route')
    assert response.status_code == 404
    logger.info("Invalid route test passed")
