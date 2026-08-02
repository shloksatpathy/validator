# Quick Deploy Guide - Backend to Render

## ⚡ 5-Minute Deployment

### Prerequisites
- GitHub account
- Code pushed to GitHub repository
- Render account (https://render.com)

### Deploy in 3 Steps

#### Step 1: Push Code
```bash
cd /home/shlok/Desktop/validator
git add .
git commit -m "Ready for Render deployment"
git push origin main
```

#### Step 2: Create Service on Render
1. Go to https://dashboard.render.com
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Set these values:
   - **Name**: `academic-validator-backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0 server:app`

#### Step 3: Set Environment Variables
Add in Render Dashboard:
```
GEMINI_API_KEY = (paste from .env)
FRONTEND_URL = https://validator-ixxm.onrender.com
FLASK_ENV = production
```

**Click "Create Web Service" and wait for deployment (2-3 minutes)**

### Verify Deployment

```bash
# Your backend URL will be shown on Render Dashboard
# Example: https://academic-validator-backend-xyz.onrender.com

# Test it
curl https://academic-validator-backend-xyz.onrender.com/health
```

Expected response:
```json
{"status": "ok", "timestamp": "2026-08-02..."}
```

### Verify Frontend Connection

1. Visit https://validator-ixxm.onrender.com
2. Open DevTools (F12) → Network tab
3. Upload a test file
4. Check that API calls go to your backend URL

---

## What's Deployed

✅ Flask API Server
✅ File Upload Handler
✅ Gemini API Integration
✅ CORS Configuration
✅ Production Gunicorn Server

---

## Troubleshooting

### Build Failed
- Check logs on Render Dashboard
- Ensure `requirements.txt` has all dependencies
- Verify Python version compatibility

### Deployment Stalled
- Click "Redeploy" on Render Dashboard
- Check service status
- Review build logs

### CORS Errors
- Verify `FRONTEND_URL` is set correctly
- Restart the service after updating env vars

### API Returns 404
- Backend service must be running
- Check correct backend URL in browser DevTools

---

## Environment Variables Explained

| Variable | Value | Purpose |
|----------|-------|---------|
| `GEMINI_API_KEY` | Your API key | Enable AI processing |
| `FRONTEND_URL` | Frontend URL | Allow CORS from frontend |
| `FLASK_ENV` | `production` | Disable debug mode |

---

## After Deployment

1. ✅ Test file upload on https://validator-ixxm.onrender.com
2. ✅ Check processing works (Gemini integration)
3. ✅ Verify submissions dashboard
4. ✅ Test file deletion and download

---

## Backend URL Format

Render will give you a URL like:
```
https://academic-validator-backend-xxxxx.onrender.com
```

**Frontend automatically uses this URL if it matches the expected pattern.**

If the URL doesn't match, update in:
- `index.html` - Search for `API_BASE_URL`
- `submissions.html` - Search for `API_BASE_URL`

---

## File Structure Deployed to Render

```
/app
├── server.py              ← Main Flask app
├── requirements.txt       ← Dependencies
├── index.html            ← Upload page
├── submissions.html      ← Dashboard
├── input/
│   ├── pending/          ← Uploaded files
│   ├── processed/        ← Processed files
│   └── failed/           ← Failed files
└── prompts/              ← AI processing prompts
```

---

## Monitoring

After deployment, monitor on Render Dashboard:
- **Logs**: Real-time server logs
- **Metrics**: CPU, memory, network usage
- **Deploys**: Deployment history
- **Status**: Service uptime

---

## Next Steps

1. Deploy backend to Render (this guide)
2. Verify frontend connects to backend
3. Test complete upload → process → view workflow
4. Monitor logs for issues
5. Scale if needed (upgrade Render plan)

---

**You're ready! Deploy now! 🚀**

For detailed help, see `RENDER_DEPLOYMENT.md`
