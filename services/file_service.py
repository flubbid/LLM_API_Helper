import base64
import io
from PIL import Image
import csv
import json

class FileService:
    def process_image(self, image_data):
        try:
            encoded = image_data.split(",", 1)[1] if image_data.startswith('data:') else image_data
            img = Image.open(io.BytesIO(base64.b64decode(encoded))).convert('RGB')
            buffer = io.BytesIO()
            img.save(buffer, format='JPEG')
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return None

    def process_csv(self, csv_data):
        try:
            csv_string = base64.b64decode(csv_data).decode('utf-8')
            rows = list(csv.reader(csv_string.splitlines()))
            return rows[:2000]
        except Exception as e:
            print(f"Error processing CSV: {str(e)}")
            return None

    def process_text_file(self, file_data):
        try:
            file_content = base64.b64decode(file_data).decode('utf-8')
            return file_content[:2000]
        except Exception as e:
            print(f"Error processing text file: {str(e)}")
            return None

    def process_file(self, file):
        file_type = file['type']
        file_data = file['data']
        file_name = file.get('name', 'Unnamed file')
        
        if file_type == 'image':
            processed_data = self.process_image(file_data)
            if processed_data:
                return {
                    'type': 'image',
                    'source': {
                        'type': 'base64',
                        'media_type': 'image/jpeg',
                        'data': processed_data
                    }
                }
        elif file_type == 'csv':
            csv_preview = self.process_csv(file_data)
            if csv_preview:
                return {
                    'type': 'text',
                    'text': f"CSV Preview of {file_name}:\n{json.dumps(csv_preview, indent=2)}"
                }
        elif file_type == 'code':
            file_preview = self.process_text_file(file_data)
            if file_preview:
                return {
                    'type': 'text',
                    'text': f"Content preview of {file_name}:\n{file_preview}"
                }
        return None