# Render Deployment Guide

This guide explains how to deploy the Academic Validator backend and frontend to Render.

## Architecture

```
┌─────────────────────────────────────────────┐
│  Frontend (React/HTML)                      │
│  https://validator-ixxm.onrender.com        │
└──────────────────┬──────────────────────────┘
                   │ API Calls
                   ↓
┌─────────────────────────────────────────────┐
│  Backend (Flask API)                        │
│  https://academic-validator-backend...      │
│  - File Upload                              │
│  - Image Processing (Gemini API)            │
│  - Submission Management                    │
└─────────────────────────────────────────────┘
```

## Prerequisites

1. **Render Account**: https://render.com (sign up with GitHub)
2. **GitHub Repository**: Push this code to GitHub
3. **Gemini API Key**: From Google AI Studio
4. **Frontend Already Deployed**: https://validator-ixxm.onrender.com

## Step 1: Deploy Backend to Render

### Option A: Using Render Dashboard

1. Go to https://dashboard.render.com
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure settings:
   - **Name**: `academic-validator-backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0 server:app`
   - **Plan**: Free (or Paid if you need better performance)

5. Add Environment Variables:
   - `GEMINI_API_KEY`: Your API key from .env
   - `FRONTEND_URL`: `https://validator-ixxm.onrender.com`
   - `FLASK_ENV`: `production`

6. Click "Create Web Service" and wait for deployment

### Option B: Using render.yaml (Recommended)

The `render.yaml` file is already configured in the repository:

```bash
git push  # Push to GitHub
```

Then on Render Dashboard:
1. Click "New +" → "Web Service"
2. Select your repository
3. Render will auto-detect and use `render.yaml` configuration

## Step 2: Update Frontend to Use Backend API

The frontend automatically detects the environment and uses the correct API URL:

- **Local Development**: `http://localhost:5000`
- **Production (Render)**: Backend URL from environment

No manual changes needed - the frontend (`index.html` and `submissions.html`) includes automatic URL detection:

```javascript
const API_BASE_URL = (() => {
    if (window.location.hostname === 'localhost') {
        return 'http://localhost:5000';
    }
    // Use Render backend URL
    return window.location.origin
        .replace('validator-ixxm', 'academic-validator-backend')
        .replace('onrender.com', 'onrender.com');
})();
```

## Step 3: Configure CORS

The backend includes CORS configuration for:
- `http://localhost:3000`
- `http://localhost:5000`
- `https://validator-ixxm.onrender.com`
- Any URL from `FRONTEND_URL` environment variable

**Update CORS allowed origins in `server.py` if needed:**

```python
allowed_origins = [
    'http://localhost:3000',
    'http://localhost:5000',
    'https://validator-ixxm.onrender.com',
    FRONTEND_URL  # From environment
]
```

## Step 4: Verify Deployment

### Check Backend Status
```bash
curl https://your-backend-url.onrender.com/health
```

Expected response:
```json
{
  "status": "ok",
  "timestamp": "2026-08-02T01:47:24.044166"
}
```

### Check Frontend Connectivity
1. Visit https://validator-ixxm.onrender.com
2. Open browser DevTools (F12)
3. Go to Network tab
4. Try uploading a file
5. Verify API calls reach your backend URL

## Environment Variables on Render

Set these in Render Dashboard for your backend service:

| Variable | Value | Required |
|----------|-------|----------|
| `GEMINI_API_KEY` | Your API key | Yes |
| `FRONTEND_URL` | `https://validator-ixxm.onrender.com` | Yes |
| `FLASK_ENV` | `production` | No |
| `PORT` | (Auto-set by Render) | No |

## File Structure for Deployment

```
validator/
├── server.py              # Main Flask app
├── requirements.txt       # Python dependencies
├── render.yaml           # Render configuration
├── index.html            # Upload page
├── submissions.html      # Submissions page
├── .env.example          # Environment template
└── input/
    ├── pending/          # Uploaded files
    ├── processed/        # Processed files
    └── failed/           # Failed files
```

## Troubleshooting

### 1. CORS Errors
**Error**: `Access to XMLHttpRequest blocked by CORS policy`

**Solution**:
- Verify `FRONTEND_URL` environment variable is set correctly
- Check allowed origins in `server.py`
- Ensure Flask-CORS is installed: `pip install flask-cors`

### 2. Module Import Errors
**Error**: `ModuleNotFoundError: No module named 'flask_cors'`

**Solution**:
- Ensure `requirements.txt` includes `flask-cors`
- Rebuild on Render: Delete and redeploy

### 3. API Not Responding
**Error**: Frontend can't reach backend API

**Solution**:
- Check backend service is running on Render Dashboard
- Verify backend URL in browser DevTools Network tab
- Check `API_BASE_URL` calculation in index.html

### 4. Gemini API Errors
**Error**: `GEMINI_API_KEY not configured`

**Solution**:
- Set `GEMINI_API_KEY` in Render environment variables
- Verify API key is valid: https://aistudio.google.com/app/apikey
- Restart the service after updating environment variables

## Local Development Setup

### Start Backend Locally
```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your-key-here
python server.py
```

Backend runs on: `http://localhost:5000`

### Test API
```bash
# Health check
curl http://localhost:5000/health

# List submissions
curl http://localhost:5000/list

# Upload file
curl -X POST -F "file=@test.pdf" http://localhost:5000/upload
```

## Production Checklist

- [x] Backend deployed to Render
- [x] CORS configured for frontend URL
- [x] Gemini API key set in environment variables
- [x] Frontend updated to use correct API endpoint
- [x] Health check endpoint responding
- [x] File uploads working
- [x] File processing working
- [x] Submissions dashboard working

## API Endpoints

All endpoints are available at your Render backend URL:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/upload` | Upload files |
| GET | `/list` | List all submissions |
| GET | `/status/<filename>` | Get file status |
| POST | `/process/<filename>` | Process single file |
| POST | `/process-batch` | Batch process files |
| DELETE | `/delete/<filename>` | Delete file |
| GET | `/download/<filename>` | Download/view file |
| GET | `/health` | Health check |

## Monitoring

Check Render Dashboard for:
- Service status and uptime
- Build logs
- Runtime logs
- Deployment history
- Resource usage

## Cost Considerations

**Render Free Tier includes**:
- 100 hours/month of web service uptime
- 0.5 GB RAM
- 1 vCPU

**For production, consider upgrading to Starter ($7/month) for**:
- 24/7 uptime guarantee
- More RAM and CPU
- Custom domain support

## Rollback

To rollback to a previous deployment on Render:
1. Go to service settings
2. Click "Events" tab
3. Find previous deployment
4. Click "Redeploy"

## Questions?

Refer to:
- [Render Docs](https://render.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Google Generative AI](https://ai.google.dev/)
