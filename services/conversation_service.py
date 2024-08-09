class ConversationService:
    def __init__(self, llm_service, file_service):
        self.llm_service = llm_service
        self.file_service = file_service
        self.conversation_history = []
    
    def new_conversation(self):
        self.conversation_history = []
        return {"message": "New conversation started"}

    def process_message(self, message, files):
        print(f"Processing message: {message}")  # Add this log
        user_content = [{"type": "text", "text": message}]

        for file in files:
            processed_file = self.file_service.process_file(file)
            if processed_file:
                user_content.append(processed_file)

        self.conversation_history.append({"role": "user", "content": user_content})

        assistant_message = self.llm_service.call_llm(self.conversation_history)
        print(f"LLM response: {assistant_message}")  # Add this log
        
        if assistant_message:
            # Ensure assistant_message is a string
            if isinstance(assistant_message, dict) and 'content' in assistant_message:
                assistant_message = assistant_message['content']
            if not isinstance(assistant_message, str):
                assistant_message = str(assistant_message)
            
            self.conversation_history.append({"role": "assistant", "content": [{"type": "text", "text": assistant_message}]})
            return assistant_message
        else:
            print("Failed to get response from LLM")  # Add this log
            return {'error': 'Failed to get response from LLM'}

    def export_chat(self):
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
        return chat_export