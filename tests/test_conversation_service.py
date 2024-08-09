import pytest
from services.conversation_service import ConversationService
from unittest.mock import MagicMock, patch

@pytest.fixture
def conversation_service():
    llm_service = MagicMock()
    file_service = MagicMock()
    return ConversationService(llm_service, file_service)

def test_init(conversation_service):
    assert conversation_service.llm_service is not None
    assert conversation_service.file_service is not None
    assert conversation_service.conversation_history == []

def test_new_conversation(conversation_service):
    # First, add some dummy conversation history
    conversation_service.conversation_history = [{"role": "user", "content": "Hello"}]
    
    result = conversation_service.new_conversation()
    
    assert result == {"message": "New conversation started"}
    assert conversation_service.conversation_history == []

def test_process_message_without_files(conversation_service):
    conversation_service.llm_service.call_llm.return_value = "LLM response"
    
    result = conversation_service.process_message("Test message", [])
    
    assert result == "LLM response"
    assert len(conversation_service.conversation_history) == 2
    assert conversation_service.conversation_history[0] == {
        "role": "user", 
        "content": [{"type": "text", "text": "Test message"}]
    }
    assert conversation_service.conversation_history[1] == {
        "role": "assistant", 
        "content": [{"type": "text", "text": "LLM response"}]
    }

def test_process_message_with_files(conversation_service):
    conversation_service.llm_service.call_llm.return_value = "LLM response with files"
    conversation_service.file_service.process_file.return_value = {"type": "image", "data": "processed_image_data"}
    
    files = [{"type": "image", "data": "raw_image_data"}]
    result = conversation_service.process_message("Test message with image", files)
    
    assert result == "LLM response with files"
    assert len(conversation_service.conversation_history) == 2
    assert conversation_service.conversation_history[0] == {
        "role": "user", 
        "content": [
            {"type": "text", "text": "Test message with image"},
            {"type": "image", "data": "processed_image_data"}
        ]
    }

def test_process_message_llm_failure(conversation_service):
    conversation_service.llm_service.call_llm.return_value = None
    
    result = conversation_service.process_message("Test message", [])
    
    assert result == {'error': 'Failed to get response from LLM'}
    assert len(conversation_service.conversation_history) == 1

def test_process_message_with_dict_response(conversation_service):
    conversation_service.llm_service.call_llm.return_value = {"content": "LLM response as dict"}
    
    result = conversation_service.process_message("Test message", [])
    
    assert result == "LLM response as dict"
    assert conversation_service.conversation_history[1] == {
        "role": "assistant", 
        "content": [{"type": "text", "text": "LLM response as dict"}]
    }

def test_export_chat(conversation_service):
    conversation_service.conversation_history = [
        {"role": "user", "content": [{"type": "text", "text": "Hello"}]},
        {"role": "assistant", "content": [{"type": "text", "text": "Hi there!"}]},
        {"role": "user", "content": [{"type": "image", "data": "image_data"}]},
        {"role": "assistant", "content": [{"type": "text", "text": "I see an image."}]}
    ]
    
    result = conversation_service.export_chat()
    
    expected_result = "User:\nHello\n\nAssistant:\nHi there!\n\nUser:\n[Image uploaded]\n\nAssistant:\nI see an image.\n\n"
    assert result == expected_result

def test_process_message_with_non_string_response(conversation_service):
    conversation_service.llm_service.call_llm.return_value = 12345  # Non-string response
    
    result = conversation_service.process_message("Test message", [])
    
    assert result == "12345"
    assert conversation_service.conversation_history[1] == {
        "role": "assistant", 
        "content": [{"type": "text", "text": "12345"}]
    }

@patch('services.conversation_service.print')  # Mock the print function
def test_process_message_logging(mock_print, conversation_service):
    conversation_service.llm_service.call_llm.return_value = "LLM response"
    
    conversation_service.process_message("Test message", [])
    
    mock_print.assert_any_call("Processing message: Test message")
    mock_print.assert_any_call("LLM response: LLM response")