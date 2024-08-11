import logging
from flask import request, jsonify, render_template
from services.conversation_service import ConversationService
from services.file_service import FileService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def register_routes(app, llm_service, file_service):
    conversation_service = ConversationService(llm_service, file_service)

    @app.route('/')
    def index():
        logger.info("Accessed index page")
        return render_template('index.html')

    @app.route('/get_available_models', methods=['GET'])
    def get_available_models():
        try:
            logger.info("Fetching available models")
            models = llm_service.available_models
            logger.info(f"Available models: {models}")
            return jsonify(models)
        except Exception as e:
            logger.error(f"Error fetching available models: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    @app.route('/new_conversation', methods=['POST'])
    def new_conversation():
        try:
            logger.info("Received request to start a new conversation")
            result = conversation_service.new_conversation()
            logger.info("New conversation started successfully")
            return jsonify(result), 200
        except Exception as e:
            logger.error(f"Error starting new conversation: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    @app.route('/chat', methods=['POST'])
    def chat():
        try:
            # Log the incoming request
            logger.debug("Incoming request to /chat route")
            
            data = request.json
            logger.debug(f"Request JSON data: {data}")
            
            message = data.get('message')
            files = data.get('files', [])
            model = data.get('model')
            assistant_id = data.get('assistantId')
            
            logger.info(f"Received chat message: {message}")
            logger.debug(f"Received files: {files}")
            logger.debug(f"Received model: {model}")
            logger.debug(f"Received assistant ID: {assistant_id}")

            if model:
                logger.info(f"Setting model to: {model}")
                llm_service.set_model(model)
            
            # Process files if any
            processed_files = []
            for file in files:
                logger.debug(f"Processing file: {file['name']}")
                processed_file = file_service.process_file(file)
                if processed_file:
                    processed_files.append(processed_file)
                    logger.info(f"Processed file: {file['name']} successfully")
                else:
                    logger.warning(f"Failed to process file: {file['name']}")

            # Add file contents to the message if any files were processed
            if processed_files:
                logger.debug(f"Processed files: {processed_files}")
                file_contents = "\n".join([
                    f"File: {file['name']}\nContent: {file.get('text') or file['source']['data']}"
                    for file in processed_files
                ])
                message += f"\n\nAttached files:\n{file_contents}"
                logger.info("Added file contents to the chat message")

            # Process the message through the conversation service
            logger.debug("Sending message to conversation service for processing")
            response = conversation_service.process_message(message, processed_files, assistant_id)
            logger.info(f"Chat response generated: {response}")
            
            return jsonify(response)
        
        except ValueError as e:
            logger.warning(f"Value error in chat route: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 400
        
        except Exception as e:
            logger.error(f"Error processing chat message: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    
    @app.route('/export_chat', methods=['GET'])
    def export_chat():
        try:
            logger.info("Received request to export chat")
            chat_export = conversation_service.export_chat()
            logger.info("Chat exported successfully")
            return jsonify({"export": chat_export})
        except Exception as e:
            logger.error(f"Error exporting chat: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500
    
    @app.route('/set_model', methods=['POST'])
    def set_model():
        try:
            data = request.json
            model = data.get('model')
            logger.info(f"Received request to set model to: {model}")
            llm_service.set_model(model)
            logger.info(f"Model set to: {model} successfully")
            return jsonify({"message": f"Model set to {model}"})
        except ValueError as e:
            logger.warning(f"Invalid model provided: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            logger.error(f"Error setting model: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500
        
    @app.route('/create_assistant', methods=['POST'])
    def create_assistant():
        try:
            data = request.json
            name = data.get('name')
            instructions = data.get('instructions')
            logger.info(f"Received request to create assistant with name: {name}")
            assistant_id = llm_service.create_assistant(name, instructions)
            logger.info(f"Assistant created successfully with ID: {assistant_id}")
            return jsonify({"assistantId": assistant_id})
        except Exception as e:
            logger.error(f"Error creating assistant: {e}", exc_info=True)
            return jsonify({"error": str(e)}), 500

    logger.info("All routes registered successfully")