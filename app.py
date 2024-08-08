from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from routes import register_routes
from services.llm_service import LLMService
from services.file_service import FileService

def create_app():
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    CORS(app)
    load_dotenv()

    # Initialize services
    llm_service = LLMService()
    file_service = FileService()

    # Register routes
    register_routes(app, llm_service, file_service)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)