import logging

logger = logging.getLogger(__name__)

class ConversationService:
    def __init__(self, llm_service, file_service):
        logger.info("Initializing ConversationService")
        self.llm_service = llm_service
        self.file_service = file_service
        self.conversation_history = []
        logger.info("ConversationService initialized successfully")
    
    def new_conversation(self):
        try:
            logger.info("Starting a new conversation")
            self.conversation_history = []
            self.llm_service._create_or_get_thread()  
            logger.info("New conversation started")
            return {"message": "New conversation started"}
        except Exception as e:
            logger.error(f"Error starting new conversation: {e}", exc_info=True)
            return {"error": str(e)}

    def process_message(self, message, files, assistant_id=None):
        try:
            logger.info(f"Processing message: {message}")
            user_content = [{"type": "text", "text": message}]
            processed_files = []

            for file in files:
                processed_file = self.file_service.process_file(file)
                if processed_file:
                    processed_files.append(processed_file)
                    if processed_file['type'] == 'text':
                        user_content.append({"type": "text", "text": processed_file['text']})
                    elif processed_file['type'] == 'image':
                        user_content.append({"type": "image", "image_url": processed_file['source']['data']})

            # Add only the new message to the conversation history
            self.conversation_history.append({"role": "user", "content": user_content})

            # Prepare messages for LLM, including only unique entries
            llm_messages = self._prepare_messages_for_llm()

            assistant_message = self.llm_service.call_llm(llm_messages, processed_files, assistant_id)
            
            if assistant_message:
                self.conversation_history.append({"role": "assistant", "content": [{"type": "text", "text": assistant_message}]})
                return assistant_message
            else:
                logger.error("Failed to get response from LLM")
                return {'error': 'Failed to get response from LLM'}
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {"error": str(e)}
        
    def _prepare_messages_for_llm(self):
        unique_messages = []
        seen = set()
        for message in self.conversation_history:
            message_content = message['content'][0]['text'] if message['content'] else ''
            if message_content not in seen:
                seen.add(message_content)
                unique_messages.append({"role": message['role'], "content": message_content})
        return unique_messages

    def export_chat(self):
        try:
            logger.info("Exporting chat history")
            chat_export = ""
            for message in self.conversation_history:
                role = message['role']
                content = message['content']
                chat_export += f"{role.capitalize()}:\n"
                for item in content:
                    if item['type'] == 'text':
                        chat_export += f"{item['text']}\n"
                    elif item['type'] == 'image':
                        chat_export += "[Image uploaded]\n"
                chat_export += "\n"
            logger.info("Chat history exported successfully")
            return chat_export
        except Exception as e:
            logger.error(f"Error exporting chat history: {e}", exc_info=True)
            return {"error": str(e)}
