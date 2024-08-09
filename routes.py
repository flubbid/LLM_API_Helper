from flask import request, jsonify, render_template, send_from_directory
from services.conversation_service import ConversationService

def register_routes(app, llm_service, file_service):
    conversation_service = ConversationService(llm_service, file_service)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/new_conversation', methods=['POST'])
    def new_conversation():
        conversation_service.new_conversation()
        return jsonify({"message": "New conversation started"}), 200

    @app.route('/chat', methods=['POST'])
    def chat():
        try:
            data = request.json
            message = data['message']
            files = data.get('files', [])
            model = data.get('model')
            
            print(f"Received message: {message}")  # Add this log
            print(f"Selected model: {model}")  # Add this log
            
            if model:
                try:
                    llm_service.set_model(model)
                except ValueError as e:
                    print(f"Error setting model: {str(e)}")  # Add this log
                    return jsonify({"error": str(e)}), 400
            
            response = conversation_service.process_message(message, files)
            print(f"LLM response: {response}")  # Add this log
            return jsonify(response)
        except Exception as e:
            print(f"Error in chat route: {str(e)}")  # Add this log
            return jsonify({"error": str(e)}), 500

    @app.route('/export_chat', methods=['GET'])
    def export_chat():
        chat_export = conversation_service.export_chat()
        return jsonify({"export": chat_export})
    
    @app.route('/set_model', methods=['POST'])
    def set_model():
        data = request.json
        model = data.get('model')
        try:
            llm_service.set_model(model)
            return jsonify({"message": f"Model set to {model}"})
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
