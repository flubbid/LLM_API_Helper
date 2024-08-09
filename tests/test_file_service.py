import pytest
from services.file_service import FileService
import base64
import io
from PIL import Image
import csv
import json

@pytest.fixture
def file_service():
    return FileService()

def test_process_image(file_service):
    # Create a small test image
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    img_base64 = base64.b64encode(img_byte_arr).decode('utf-8')

    processed_image = file_service.process_image(img_base64)
    assert processed_image is not None
    assert isinstance(processed_image, str)
    
    # Test that the processed image can be decoded back to an image
    processed_img_data = base64.b64decode(processed_image)
    processed_img = Image.open(io.BytesIO(processed_img_data))
    assert processed_img.size == (100, 100)

def test_process_csv(file_service):
    csv_data = "Name,Age\nAlice,30\nBob,25"
    csv_base64 = base64.b64encode(csv_data.encode('utf-8')).decode('utf-8')

    processed_csv = file_service.process_csv(csv_base64)
    assert processed_csv is not None
    assert isinstance(processed_csv, list)
    assert len(processed_csv) == 3  # header + 2 data rows
    assert processed_csv[0] == ['Name', 'Age']
    assert processed_csv[1] == ['Alice', '30']
    assert processed_csv[2] == ['Bob', '25']

def test_process_text_file(file_service):
    text_data = "This is a test file.\nIt has multiple lines."
    text_base64 = base64.b64encode(text_data.encode('utf-8')).decode('utf-8')

    processed_text = file_service.process_text_file(text_base64)
    assert processed_text is not None
    assert isinstance(processed_text, str)
    assert processed_text == text_data

def test_process_file_image(file_service):
    img = Image.new('RGB', (100, 100), color = 'red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    img_base64 = base64.b64encode(img_byte_arr).decode('utf-8')

    file_data = {'type': 'image', 'data': img_base64, 'name': 'test.png'}
    processed_file = file_service.process_file(file_data)

    assert processed_file is not None
    assert processed_file['type'] == 'image'
    assert 'source' in processed_file
    assert processed_file['source']['type'] == 'base64'
    assert processed_file['source']['media_type'] == 'image/jpeg'
    assert isinstance(processed_file['source']['data'], str)

def test_process_file_csv(file_service):
    csv_data = "Name,Age\nAlice,30\nBob,25"
    csv_base64 = base64.b64encode(csv_data.encode('utf-8')).decode('utf-8')

    file_data = {'type': 'csv', 'data': csv_base64, 'name': 'test.csv'}
    processed_file = file_service.process_file(file_data)

    assert processed_file is not None
    assert processed_file['type'] == 'text'
    assert 'CSV Preview of test.csv' in processed_file['text']
    assert 'Alice' in processed_file['text']
    assert 'Bob' in processed_file['text']

def test_process_file_code(file_service):
    code_data = "def hello_world():\n    print('Hello, World!')"
    code_base64 = base64.b64encode(code_data.encode('utf-8')).decode('utf-8')

    file_data = {'type': 'code', 'data': code_base64, 'name': 'test.py'}
    processed_file = file_service.process_file(file_data)

    assert processed_file is not None
    assert processed_file['type'] == 'text'
    assert 'Content preview of test.py' in processed_file['text']
    assert 'def hello_world():' in processed_file['text']

def test_process_file_unknown_type(file_service):
    unknown_data = "Some unknown data"
    unknown_base64 = base64.b64encode(unknown_data.encode('utf-8')).decode('utf-8')

    file_data = {'type': 'unknown', 'data': unknown_base64, 'name': 'test.unknown'}
    processed_file = file_service.process_file(file_data)

    assert processed_file is None

def test_process_large_file(file_service):
    large_data = 'a' * 3000  # Create a string larger than the 2000 character limit
    large_base64 = base64.b64encode(large_data.encode('utf-8')).decode('utf-8')

    file_data = {'type': 'code', 'data': large_base64, 'name': 'large_file.txt'}
    processed_file = file_service.process_file(file_data)

    assert processed_file is not None
    assert processed_file['type'] == 'text'
    assert len(processed_file['text']) <= 2000 + len('Content preview of large_file.txt:\n')

def test_process_invalid_base64(file_service):
    invalid_base64 = 'This is not valid base64!'

    file_data = {'type': 'code', 'data': invalid_base64, 'name': 'invalid.txt'}
    processed_file = file_service.process_file(file_data)

    assert processed_file is None