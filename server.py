from flask import Flask, request, jsonify, send_file, render_template_string
from werkzeug.utils import secure_filename
import os
import json
from datetime import datetime
import hashlib

app = Flask(__name__, static_folder='.', static_url_path='')

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'input', 'pending')
PROCESSED_FOLDER = os.path.join(os.path.dirname(__file__), 'input', 'processed')
FAILED_FOLDER = os.path.join(os.path.dirname(__file__), 'input', 'failed')
ALLOWED_EXTENSIONS = {'json', 'txt', 'py', 'cpp', 'java', 'js', 'pdf', 'md'}
MAX_FILE_SIZE = 50 * 1024 * 1024

app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(FAILED_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    meta_file = os.path.join(app.config['UPLOAD_FOLDER'], f'{filename}.meta.json')

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


@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()}), 200


@app.route('/')
def index():
    with open('index.html', 'r') as f:
        return f.read()


@app.route('/submissions')
def submissions():
    with open('submissions.html', 'r') as f:
        return f.read()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
