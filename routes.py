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
        data = request.json
        message = data['message']
        files = data.get('files', [])
        
        response = conversation_service.process_message(message, files)
        return jsonify(response)

    @app.route('/export_chat', methods=['GET'])
    def export_chat():
        chat_export = conversation_service.export_chat()
        return jsonify({"export": chat_export})
    
    @app.route('/switch_llm', methods=['POST'])
    def switch_llm():
        data = request.json
        llm_name = data.get('llm')
        try:
            llm_service.switch_llm(llm_name)
            return jsonify({"message": f"Switched to {llm_name}"})
        except ValueError as e:
            return jsonify({"error": str(e)}), 400