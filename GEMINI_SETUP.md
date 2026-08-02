# Gemini API Integration Setup

This guide explains how to set up and use the Gemini API for backend image processing in the Academic Validator.

## Prerequisites

- Python 3.9+
- Your Gemini API key (from Google AI Studio)

## Setup Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

The requirements now include:
- `google-generativeai` - For Gemini API integration
- `Pillow` - For image processing
- `python-dotenv` - For loading environment variables

### 2. Configure Gemini API Key

Create a `.env` file in the project root (copy from `.env.example`):

```bash
cp .env.example .env
```

Then add your Gemini API key:

```
GEMINI_API_KEY=your-actual-gemini-api-key-here
```

**Security Note:** Never commit the `.env` file to version control. It's already in `.gitignore`.

## How It Works

### Image Processing Pipeline

1. **Upload**: Users upload image files through the web interface
2. **Storage**: Images are stored in `input/pending/`
3. **Processing**: Images are processed with Gemini API using configured prompts
4. **Results**: Processing results are stored in file metadata

### Auto-Processing

When enabled via the "Auto-process after upload" checkbox:
- After successful upload, images are automatically sent to Gemini API
- Results are attached to the file metadata
- Status is updated to "processed"

### Manual Processing

Process files via API endpoints:

#### Single File Processing
```bash
curl -X POST http://localhost:5000/process/image.jpg \
  -H "Content-Type: application/json" \
  -d '{"prompt_type": "validator"}'
```

#### Batch Processing
```bash
curl -X POST http://localhost:5000/process-batch \
  -H "Content-Type: application/json" \
  -d '{
    "prompt_type": "validator",
    "files": ["image1.jpg", "image2.jpg"]
  }'
```

## Available Prompts

The system uses prompts from the `prompts/` directory:

- **validator.txt** - Validates solutions without revealing answers
- **hint1.txt** - Provides first-level hints
- **solution.txt** - Shows complete solutions (after attempts exhausted)

You can create custom prompts by adding new `.txt` files to the `prompts/` folder.

## Response Format

### Processing Success
```json
{
  "success": true,
  "filename": "image.jpg",
  "result": "Gemini API response here",
  "model": "gemini-2.0-flash"
}
```

### Processing Error
```json
{
  "error": "Error message",
  "success": false
}
```

## File Metadata

After processing, file metadata includes:
- `filename` - Original filename
- `timestamp` - Upload timestamp
- `file_size` - File size in bytes
- `hash` - SHA256 hash
- `status` - "pending" or "processed"
- `processing_result` - Gemini response (if processed)
- `processed_at` - Processing timestamp (if processed)

Example metadata file (`image.jpg.meta.json`):
```json
{
  "filename": "image.jpg",
  "timestamp": "2026-08-02T10:30:00.123456",
  "file_size": 245821,
  "hash": "abc123def456...",
  "status": "processed",
  "processing_result": "Correct. Session finished.",
  "processed_at": "2026-08-02T10:30:05.789123"
}
```

## Troubleshooting

### "Gemini API key not configured"
- Ensure `.env` file exists and contains `GEMINI_API_KEY`
- Verify the file is in the project root directory
- Restart the server after adding/changing the API key

### Image Processing Fails
- Confirm the image format is supported (PNG, JPG, JPEG, GIF, BMP, WebP)
- Check that the image file is not corrupted
- Verify your Gemini API key has appropriate quota

### "File is not an image"
- Only image files are supported for Gemini processing
- Rename the file with a proper image extension
- Supported formats: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp`

## API Endpoints

### Upload File
- **Endpoint**: `POST /upload`
- **Input**: Multipart form with file
- **Output**: JSON with filename and metadata

### Get File Status
- **Endpoint**: `GET /status/<filename>`
- **Output**: File metadata JSON

### Process Single File
- **Endpoint**: `POST /process/<filename>`
- **Input**: JSON with optional `prompt_type`
- **Output**: Processing result from Gemini

### Process Multiple Files
- **Endpoint**: `POST /process-batch`
- **Input**: JSON with `prompt_type` and `files` array
- **Output**: Array of results for each file

### List All Submissions
- **Endpoint**: `GET /list`
- **Output**: Array of all submissions across all folders

### Health Check
- **Endpoint**: `GET /health`
- **Output**: Server status

## Performance Notes

- Gemini 2.0 Flash is optimized for fast inference
- Large batches may take longer; consider processing in chunks
- The server maintains persistent connections for efficiency
- Image processing typically completes in 1-3 seconds per image

## Next Steps

1. Get your Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)
2. Create the `.env` file with your API key
3. Install dependencies with `pip install -r requirements.txt`
4. Run the server with `python server.py`
5. Try uploading and processing images with the "Auto-process" checkbox enabled

## Customization

### Add New Prompts

Create a new file in `prompts/` (e.g., `prompts/custom_prompt.txt`) and use it:

```bash
curl -X POST http://localhost:5000/process/image.jpg \
  -H "Content-Type: application/json" \
  -d '{"prompt_type": "custom_prompt"}'
```

### Modify Image Processing

Edit the `process_image_with_gemini()` function in `server.py` to:
- Change the Gemini model
- Adjust temperature or other parameters
- Add post-processing of responses

## Limitations

- Maximum file size: 50MB (configured in `server.py`)
- Processing timeout depends on Gemini API rate limits
- Batch processing is sequential (one file at a time)
