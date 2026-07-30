# Quick Start Guide

## Installation & Setup (5 minutes)

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Start the server
```bash
python server.py
```

You'll see:
```
 * Running on http://0.0.0.0:5000
```

### 3. Access from your computer
Open your browser and go to:
```
http://localhost:5000
```

### 4. Access from mobile device
Find your computer's IP address:

**Linux/Mac:**
```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

**Windows:**
```bash
ipconfig
```

Look for something like `192.168.x.x` or `10.x.x.x`

Then on your mobile device, open:
```
http://<YOUR_IP>:5000
```

Example: `http://192.168.1.100:5000`

---

## Using the Interface

### Upload Problems
1. Click **"Choose File"** to select documents/code files
2. Click **"Take Photo"** to capture images from your camera
3. Drag & drop files onto the interface
4. Click **"Upload Problem"** to submit

### View Submissions
1. Click **"View All Submissions"** link at the bottom
2. Filter by status (All, Pending, Processed, Failed)
3. Click **Refresh** to update the list
4. Submissions auto-update every 5 seconds

---

## API Endpoints (Advanced)

### Upload via curl
```bash
curl -F "file=@problem.json" http://localhost:5000/upload
```

### Check status
```bash
curl http://localhost:5000/status/problem.json
```

### List all submissions
```bash
curl http://localhost:5000/list
```

### Health check
```bash
curl http://localhost:5000/health
```

---

## Troubleshooting

### Can't access from mobile?
- ✓ Check firewall allows port 5000
- ✓ Use correct IP (not localhost)
- ✓ Both devices on same network
- ✓ Restart the server

### Port 5000 already in use?
Change port in `server.py`:
```python
app.run(host='0.0.0.0', port=8000)  # Change 5000 to 8000
```

### File upload fails?
- ✓ Check file type is allowed
- ✓ File size < 50MB
- ✓ Server is running

---

## Next: Add Validation Logic

Once you're comfortable with the upload interface, add your validation logic:

1. Create validators in `validators/` folder
2. Create test cases in `tests/` folder
3. Implement processing pipeline
4. Add database integration

See main README.md for more details.
