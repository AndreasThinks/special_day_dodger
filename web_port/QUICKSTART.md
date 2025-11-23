# Quick Start Guide

Get Special Day Dodger running in 3 easy steps!

## Step 1: Start the Game (Choose One)

### Option A: Simple File Open (May have CORS issues)
Just double-click `index.html`

### Option B: Python Web Server (Recommended)
```bash
cd web_port
python3 -m http.server 8000
```
Then open: http://localhost:8000

### Option C: Node.js Web Server
```bash
cd web_port
npx http-server -p 8000
```
Then open: http://localhost:8000

## Step 2: (Optional) Enable Online Leaderboard

### Install Backend Dependencies
```bash
pip install flask flask-cors
```

### Start the Backend
```bash
python backend_example.py
```
The backend will run on http://localhost:5000

### Update API Configuration
Edit `js/config.js` and change:
```javascript
API_BASE_URL: 'http://localhost:5000/api'
```

Refresh the game page - you now have a working online leaderboard!

## Step 3: Play!

### Desktop Controls
- **Move:** Arrow keys or WASD
- **Shoot:** Space bar
- **Mute:** M key
- **Start:** Enter key

### Mobile/Touch Controls
- **Move:** Touch and drag
- **Shoot:** Quick tap
- **Navigate:** Tap buttons

## Next Steps

- Read the full [README.md](README.md) for deployment options
- Customize game settings in `js/config.js`
- Deploy to your Python website (Flask, Django, FastAPI)
- Set up a real database for persistent leaderboards

## Troubleshooting

**Game won't load?**
- Use Option B or C (web server required for modern browsers)

**No sound?**
- Click on the game first (browsers require user interaction)
- Press M to check if muted

**Leaderboard not working?**
- Make sure backend is running on port 5000
- Check that API_BASE_URL is set correctly in config.js
- Open browser console (F12) to see any errors

**Touch controls not responding?**
- Test on an actual touch device (not desktop)
- Make sure you're dragging, not just clicking

## Support

Check the full README.md for:
- Deployment guides
- Backend integration details
- Customization options
- Advanced troubleshooting
