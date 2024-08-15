import base64
import io
from PIL import Image
import csv
import json
import logging

logger = logging.getLogger(__name__)

class FileService:
    def process_image(self, image_data):
        try:
            logger.info(f"Starting image processing. Data length: {len(image_data)}")
            encoded = image_data.split(",", 1)[1] if image_data.startswith('data:') else image_data
            logger.debug(f"Encoded image data (first 100 chars): {encoded[:100]}")
            img = Image.open(io.BytesIO(base64.b64decode(encoded))).convert('RGB')
            logger.info(f"Image opened. Size: {img.size}, Mode: {img.mode}")
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            processed_image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')
            logger.info(f"Image processed successfully. Processed data length: {len(processed_image_data)}")
            return processed_image_data
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}", exc_info=True)
            return None

    def process_csv(self, csv_data):
        try:
            logger.info(f"Starting CSV processing. Data length: {len(csv_data)}")
            csv_string = base64.b64decode(csv_data).decode('utf-8')
            logger.debug(f"Decoded CSV data (first 100 chars): {csv_string[:100]}")
            rows = list(csv.reader(csv_string.splitlines()))
            logger.info(f"CSV processed successfully with {len(rows)} rows")
            return rows[:2000]  # Limit the number of rows returned
        except Exception as e:
            logger.error(f"Error processing CSV: {str(e)}", exc_info=True)
            return None

    def process_file(self, file):
        file_type = file.get('type')
        file_name = file.get('name', 'Unnamed file')
        
        logger.info(f"Processing file: {file_name} (Type: {file_type})")
        
        file_data = file.get('data') or file.get('content') or (file.get('source', {}).get('data') if isinstance(file.get('source'), dict) else None)
        
        if not file_data:
            logger.warning(f"No data found for file: {file_name}. Attempting to process as text.")
            return self.process_as_text(file)
        
        logger.info(f"File data found. Length: {len(file_data)}")
        
        try:
            if file_type == 'image':
                processed_data = self.process_image(file_data)
                if processed_data:
                    logger.info(f"Image file processed successfully: {file_name}")
                    return {
                        'type': 'image',
                        'name': file_name,
                        'source': {
                            'type': 'base64',
                            'media_type': 'image/jpeg',
                            'data': processed_data
                        }
                    }
            elif file_type == 'csv':
                csv_preview = self.process_csv(file_data)
                if csv_preview:
                    logger.info(f"CSV file processed successfully: {file_name}")
                    return {
                        'type': 'text',
                        'name': file_name,
                        'text': f"CSV Preview of {file_name}:\n{json.dumps(csv_preview, indent=2)}"
                    }
            elif file_type in ['code', 'text'] or file_type is None:
                return self.process_as_text(file)
            else:
                logger.warning(f"Unsupported file type: {file_type}. Attempting to process as text.")
                return self.process_as_text(file)
        except Exception as e:
            logger.error(f"Error processing file: {file_name}, Type: {file_type}, Error: {str(e)}", exc_info=True)
            return None

    def process_as_text(self, file):
        file_name = file.get('name', 'Unnamed file')
        file_content = file.get('text') or file.get('content') or file.get('data') or ''
        
        logger.info(f"Processing as text: {file_name}. Content length: {len(file_content)}")
        
        if isinstance(file_content, bytes):
            file_content = file_content.decode('utf-8')
        elif isinstance(file_content, str):
            try:
                file_content = base64.b64decode(file_content).decode('utf-8')
                logger.info("Successfully decoded base64 content")
            except:
                logger.info("Content is not base64 encoded, using as-is")
        
        logger.info(f"Text file processed successfully: {file_name}. Processed length: {len(file_content[:1000000])}")
        return {
            'type': 'text',
            'name': file_name,
            'text': f"Content of {file_name}:\n{file_content[:1000000]}"  # Limit to 2000 characters
        }