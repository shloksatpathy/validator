# Academic Validator Framework

A flexible framework for validating academic problem solutions with remote file upload capabilities.

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the server
```bash
python server.py
```

The server will start at `http://0.0.0.0:5000`

## API Endpoints

### Upload a Problem
**POST** `/upload`
- Upload a problem file to the validator
- Supported formats: `json`, `txt`, `py`, `cpp`, `java`, `js`, `pdf`, `md`
- Max file size: 50MB

```bash
curl -F "file=@problem.json" http://localhost:5000/upload
```

Response:
```json
{
  "message": "File uploaded successfully",
  "filename": "problem.json",
  "hash": "abc123...",
  "status": "pending"
}
```

### Get Status
**GET** `/status/<filename>`
- Check the status of a submitted file

```bash
curl http://localhost:5000/status/problem.json
```

### List All Submissions
**GET** `/list`
- View all submissions across all folders (pending, processed, failed)

```bash
curl http://localhost:5000/list
```

### Health Check
**GET** `/health`
- Check if the server is running

```bash
curl http://localhost:5000/health
```

## Folder Structure

```
validator/
├── input/
│   ├── pending/      # Newly uploaded problems waiting validation
│   ├── processed/    # Successfully validated problems
│   └── failed/       # Problems that failed validation
├── config/           # Configuration files
├── validators/       # Validation logic modules
├── tests/            # Test cases
└── server.py         # Flask web server
```

## Remote Access

To access from any remote device:

1. Make sure your device's firewall allows port 5000
2. Open in browser: `http://<YOUR_IP>:5000`
3. Or use with curl:
   ```bash
   curl -F "file=@problem.json" http://<YOUR_IP>:5000/upload
   ```

4. To find your IP:
   ```bash
   # Linux/Mac
   ifconfig | grep "inet "
   
   # Windows
   ipconfig
   ```

## Web Interface

### Upload Page (`/`)
- **Choose File** - Upload any document, code file, PDF, or image
- **Take Photo** - Capture photos directly from your mobile camera
- **Drag & Drop** - Drop files directly onto the interface
- **Multiple Files** - Upload multiple problems at once
- **Auto-process** - Automatically process files after upload
- **Notifications** - Get notified when processing is complete

### Submissions Page (`/submissions`)
- View all uploaded submissions
- Filter by status (Pending, Processed, Failed)
- See file details (size, upload time, hash)
- Track validation progress

## Mobile Features

- ✅ **Responsive Design** - Works perfectly on phones, tablets, and desktops
- 📷 **Camera Support** - Take photos of handwritten problems or documents
- 📱 **Touch-Friendly** - Large buttons and easy navigation for mobile
- ⚡ **Fast Uploads** - Progress tracking for file uploads
- 🔄 **Auto-Refresh** - Submissions update in real-time

## Supported File Types

- Documents: `.pdf`, `.txt`, `.md`
- Code: `.py`, `.java`, `.cpp`, `.js`
- Structured: `.json`
- Images: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`

## Next Steps

- Add validation logic in `validators/`
- Create test cases in `tests/`
- Implement problem processing pipeline
- Add database support for tracking submissions
- Set up background job processing for validation
