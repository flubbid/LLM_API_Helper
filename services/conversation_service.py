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
            self.llm_service._create_thread()  # Create a new thread for OpenAI if using GPT
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
                if isinstance(file, dict) and ('text' in file or 'source' in file):
                    # File is already processed
                    processed_files.append(file)
                else:
                    processed_file = self.file_service.process_file(file)
                    if processed_file:
                        logger.info(f"Processed file: {file.get('name', 'Unnamed file')} successfully")
                        processed_files.append(processed_file)
                    else:
                        logger.warning(f"Failed to process file: {file.get('name', 'Unnamed file')}")

            for file in processed_files:
                if file['type'] == 'text':
                    user_content.append({"type": "text", "text": file['text']})
                else:
                    user_content.append(file)

            self.conversation_history.append({"role": "user", "content": user_content})

            llm_messages = self._prepare_messages_for_llm()
            assistant_message = self.llm_service.call_llm(llm_messages, processed_files, assistant_id)
            logger.info(f"Received response from LLM: {assistant_message}")
            
            if assistant_message:
                if isinstance(assistant_message, dict):
                    assistant_message = self.llm_service.call_llm(llm_messages, processed_files, assistant_id)
                elif not isinstance(assistant_message, str):
                    assistant_message = str(assistant_message)
                
                self.conversation_history.append({"role": "assistant", "content": [{"type": "text", "text": assistant_message}]})
                logger.info("Message processed and added to conversation history")
                return assistant_message
            else:
                logger.error("Failed to get response from LLM")
                return {'error': 'Failed to get response from LLM'}
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return {"error": str(e)}
        
    def _prepare_messages_for_llm(self):
        try:
            logger.info("Preparing messages for LLM")
            llm_messages = []
            for message in self.conversation_history:
                content = ""
                for item in message['content']:
                    if item['type'] == 'text':
                        content += item['text'] + "\n"
                    elif item['type'] == 'image':
                        content += "[Image uploaded]\n"
                    # Add other file types as needed
                llm_messages.append({"role": message['role'], "content": content.strip()})
            logger.info("Messages prepared for LLM")
            return llm_messages
        except Exception as e:
            logger.error(f"Error preparing messages for LLM: {e}", exc_info=True)
            return []

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
