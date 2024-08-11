from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
from routes import register_routes
from services.llm_service import LLMService
from services.file_service import FileService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app():
    logger.info("Creating Flask app")
    app = Flask(__name__, static_folder='static', static_url_path='/static')
    CORS(app)
    
    try:
        logger.info("Loading environment variables")
        load_dotenv()
    except Exception as e:
        logger.error(f"Error loading environment variables: {e}")

    # Initialize services
    try:
        logger.info("Initializing LLM service")
        llm_service = LLMService()
        logger.info("Initializing File service")
        file_service = FileService()
    except Exception as e:
        logger.critical(f"Service initialization failed: {e}", exc_info=True)
        raise

    # Register routes
    try:
        logger.info("Registering routes")
        register_routes(app, llm_service, file_service)
    except Exception as e:
        logger.error(f"Error registering routes: {e}", exc_info=True)
        raise

    logger.info("Flask app created successfully")
    return app

if __name__ == '__main__':
    try:
        app = create_app()
        logger.info("Starting Flask app")
        app.run(debug=True)
    except Exception as e:
        logger.critical(f"Flask app failed to start: {e}", exc_info=True)
