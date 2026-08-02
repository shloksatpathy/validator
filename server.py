from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import hashlib
import base64
from pathlib import Path
import google.generativeai as genai
from PIL import Image
import mimetypes
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')

# Configure CORS for both local and Render deployments
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
allowed_origins = [
    'http://localhost:3000',
    'http://localhost:5000',
    'https://validator-ixxm.onrender.com',
    FRONTEND_URL
]

CORS(app, resources={r"/*": {"origins": allowed_origins}}, supports_credentials=True)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'input', 'pending')
PROCESSED_FOLDER = os.path.join(os.path.dirname(__file__), 'input', 'processed')
FAILED_FOLDER = os.path.join(os.path.dirname(__file__), 'input', 'failed')
PROMPTS_FOLDER = os.path.join(os.path.dirname(__file__), 'prompts')
ALLOWED_EXTENSIONS = {'json', 'txt', 'py', 'cpp', 'java', 'js', 'pdf', 'md', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
MAX_FILE_SIZE = 50 * 1024 * 1024

app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(FAILED_FOLDER, exist_ok=True)

# Initialize Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    GEMINI_MODEL = genai.GenerativeModel('gemini-2.0-flash')


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def is_image(filename):
    ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return ext in IMAGE_EXTENSIONS


def load_prompt(prompt_type):
    prompt_file = os.path.join(PROMPTS_FOLDER, f'{prompt_type}.txt')
    if os.path.exists(prompt_file):
        with open(prompt_file, 'r') as f:
            return f.read()
    return None


def process_image_with_gemini(image_path, prompt):
    if not GEMINI_API_KEY:
        return {'error': 'Gemini API key not configured', 'success': False}

    try:
        img = Image.open(image_path)

        # Convert image to bytes
        import io
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format=img.format or 'PNG')
        img_data = base64.standard_b64encode(img_byte_arr.getvalue()).decode('utf-8')

        # Get image media type
        media_type = f"image/{img.format.lower()}" if img.format else "image/png"

        response = GEMINI_MODEL.generate_content([
            {
                "type": "image_data",
                "image_data": {
                    "mime_type": media_type,
                    "data": img_data,
                },
            },
            {
                "type": "text",
                "text": prompt
            }
        ])

        return {
            'success': True,
            'response': response.text,
            'model': 'gemini-2.0-flash'
        }
    except Exception as e:
        return {'error': str(e), 'success': False}


def generate_metadata(filename, file_path):
    file_size = os.path.getsize(file_path)
    with open(file_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()

    return {
        'filename': filename,
        'timestamp': datetime.utcnow().isoformat(),
        'file_size': file_size,
        'hash': file_hash,
        'status': 'pending'
    }


@app.route('/upload', methods=['POST'])
def upload_problem():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Empty filename'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': f'File type not allowed. Allowed: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    file.save(file_path)
    metadata = generate_metadata(filename, file_path)

    metadata_path = os.path.join(app.config['UPLOAD_FOLDER'], f'{filename}.meta.json')
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    return jsonify({
        'message': 'File uploaded successfully',
        'filename': filename,
        'hash': metadata['hash'],
        'status': 'pending'
    }), 201


@app.route('/status/<filename>', methods=['GET'])
def get_status(filename):
    filename = secure_filename(filename)

    for folder_path in [UPLOAD_FOLDER, PROCESSED_FOLDER, FAILED_FOLDER]:
        meta_file = os.path.join(folder_path, f'{filename}.meta.json')
        if os.path.exists(meta_file):
            with open(meta_file, 'r') as f:
                metadata = json.load(f)
            return jsonify(metadata), 200

    return jsonify({'error': 'File not found'}), 404


@app.route('/list', methods=['GET'])
def list_submissions():
    submissions = []

    for folder_name, folder_path in [('pending', UPLOAD_FOLDER),
                                      ('processed', PROCESSED_FOLDER),
                                      ('failed', FAILED_FOLDER)]:
        for file in os.listdir(folder_path):
            if file.endswith('.meta.json'):
                with open(os.path.join(folder_path, file), 'r') as f:
                    meta = json.load(f)
                    meta['folder'] = folder_name
                    submissions.append(meta)

    return jsonify(submissions), 200


@app.route('/process/<filename>', methods=['POST'])
def process_file(filename):
    filename = secure_filename(filename)
    prompt_type = request.json.get('prompt_type', 'validator') if request.json else 'validator'

    meta_file = os.path.join(app.config['UPLOAD_FOLDER'], f'{filename}.meta.json')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404

    if not is_image(filename):
        return jsonify({'error': 'File is not an image'}), 400

    prompt = load_prompt(prompt_type)
    if not prompt:
        return jsonify({'error': f'Prompt type "{prompt_type}" not found'}), 404

    result = process_image_with_gemini(file_path, prompt)

    if result.get('success'):
        # Update metadata
        if os.path.exists(meta_file):
            with open(meta_file, 'r') as f:
                metadata = json.load(f)
            metadata['status'] = 'processed'
            metadata['processing_result'] = result.get('response', '')
            metadata['processed_at'] = datetime.utcnow().isoformat()
            with open(meta_file, 'w') as f:
                json.dump(metadata, f, indent=2)

        return jsonify({
            'success': True,
            'filename': filename,
            'result': result.get('response'),
            'model': result.get('model')
        }), 200
    else:
        return jsonify({'error': result.get('error', 'Processing failed'), 'success': False}), 500


@app.route('/process-batch', methods=['POST'])
def process_batch():
    prompt_type = request.json.get('prompt_type', 'validator') if request.json else 'validator'
    files = request.json.get('files', []) if request.json else []

    if not files:
        return jsonify({'error': 'No files specified'}), 400

    results = []
    for filename in files:
        filename = secure_filename(filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        if not os.path.exists(file_path) or not is_image(filename):
            results.append({
                'filename': filename,
                'success': False,
                'error': 'File not found or not an image'
            })
            continue

        prompt = load_prompt(prompt_type)
        if not prompt:
            results.append({
                'filename': filename,
                'success': False,
                'error': f'Prompt type "{prompt_type}" not found'
            })
            continue

        result = process_image_with_gemini(file_path, prompt)
        results.append({
            'filename': filename,
            'success': result.get('success', False),
            'result': result.get('response') if result.get('success') else None,
            'error': result.get('error') if not result.get('success') else None
        })

    return jsonify({'results': results}), 200


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()}), 200


@app.route('/delete/<filename>', methods=['DELETE'])
def delete_file(filename):
    filename = secure_filename(filename)

    # Try to delete from each folder
    for folder_path in [UPLOAD_FOLDER, PROCESSED_FOLDER, FAILED_FOLDER]:
        file_path = os.path.join(folder_path, filename)
        meta_path = os.path.join(folder_path, f'{filename}.meta.json')

        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                if os.path.exists(meta_path):
                    os.remove(meta_path)
                return jsonify({'message': 'File deleted successfully', 'filename': filename}), 200
            except Exception as e:
                return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500

    return jsonify({'error': 'File not found'}), 404


@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    filename = secure_filename(filename)

    for folder_path in [UPLOAD_FOLDER, PROCESSED_FOLDER, FAILED_FOLDER]:
        file_path = os.path.join(folder_path, filename)
        if os.path.exists(file_path):
            try:
                return send_file(file_path, as_attachment=False)
            except Exception as e:
                return jsonify({'error': f'Failed to download file: {str(e)}'}), 500

    return jsonify({'error': 'File not found'}), 404


@app.route('/')
def index():
    with open('index.html', 'r') as f:
        return f.read()


@app.route('/submissions')
def submissions():
    with open('submissions.html', 'r') as f:
        return f.read()


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)
