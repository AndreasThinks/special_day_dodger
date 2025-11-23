# Special Day Dodger - Web Port

A complete JavaScript port of the Special Day Dodger Pygame game, built with Phaser.js for native web deployment with mobile touch controls and collaborative leaderboards.

## Features

- ✅ **Native Web Game** - No Python dependencies, runs in any modern browser
- ✅ **Mobile Touch Controls** - Drag to move, tap to shoot
- ✅ **Responsive Design** - Automatically scales to fit any screen size
- ✅ **Collaborative Leaderboard** - API-ready for global score tracking
- ✅ **Local Storage Fallback** - Scores saved locally when offline
- ✅ **Full Audio Support** - Background music and sound effects
- ✅ **Cross-Platform** - Works on desktop, mobile, and tablets

## Project Structure

```
web_port/
├── index.html              # Main HTML file
├── css/
│   └── style.css          # Game styling
├── js/
│   ├── config.js          # Game configuration constants
│   ├── api.js             # Leaderboard API integration
│   ├── main.js            # Phaser game initialization
│   └── scenes/
│       ├── StartScene.js      # Title screen
│       ├── GameScene.js       # Main gameplay
│       └── GameOverScene.js   # Score submission & leaderboard
└── assets/
    ├── images/            # Game sprites and backgrounds
    ├── audio/             # Music and sound effects
    └── fonts/             # Custom fonts (if needed)
```

## Quick Start

### Option 1: Local Testing (Simple)

1. **Open directly in browser:**
   ```bash
   # Navigate to the web_port directory
   cd web_port

   # Open index.html in your browser
   # On macOS:
   open index.html
   # On Linux:
   xdg-open index.html
   # On Windows:
   start index.html
   ```

   **Note:** Some browsers may block loading assets when opening files directly. If you see CORS errors, use Option 2 instead.

### Option 2: Local Web Server (Recommended)

1. **Using Python:**
   ```bash
   cd web_port
   python3 -m http.server 8000
   ```
   Then open `http://localhost:8000` in your browser.

2. **Using Node.js (npx):**
   ```bash
   cd web_port
   npx http-server -p 8000
   ```
   Then open `http://localhost:8000` in your browser.

3. **Using PHP:**
   ```bash
   cd web_port
   php -S localhost:8000
   ```
   Then open `http://localhost:8000` in your browser.

## Controls

### Desktop
- **Movement:** Arrow keys or WASD
- **Shoot:** Space bar
- **Mute:** M key
- **Start/Restart:** Enter key

### Mobile/Touch
- **Movement:** Touch and drag anywhere on screen
- **Shoot:** Quick tap on screen
- **Navigate menus:** Tap buttons

## Backend Integration

The game includes a ready-to-use API client for collaborative leaderboards. To connect it to your Python backend:

### 1. Update API Endpoint

Edit `js/config.js` and change the API_BASE_URL:

```javascript
// For local development
API_BASE_URL: 'http://localhost:5000/api'

// For production
API_BASE_URL: 'https://yourwebsite.com/api'
```

### 2. Backend Requirements

Your backend needs to implement two endpoints:

#### GET `/api/leaderboard`
Returns the top 5 scores:
```json
[
  { "name": "ABC", "score": 150 },
  { "name": "XYZ", "score": 120 },
  ...
]
```

#### POST `/api/score`
Accepts a new score submission:
```json
{
  "name": "ABC",
  "score": 150,
  "timestamp": 1234567890
}
```

Returns:
```json
{
  "success": true,
  "message": "Score submitted"
}
```

### 3. Example Flask Backend

Create a simple Flask backend:

```python
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

leaderboard = []

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    return jsonify(sorted(leaderboard, key=lambda x: x['score'], reverse=True)[:5])

@app.route('/api/score', methods=['POST'])
def submit_score():
    data = request.json
    leaderboard.append(data)
    return jsonify({'success': True, 'message': 'Score submitted'})

if __name__ == '__main__':
    app.run(port=5000, debug=True)
```

Install dependencies:
```bash
pip install flask flask-cors
```

Run:
```bash
python backend.py
```

## Deployment

### Deploy to Any Python Website

1. **Copy the `web_port` folder** to your website's static files directory

2. **Serve the files** using your Python framework:

   **Flask:**
   ```python
   from flask import Flask, send_from_directory

   app = Flask(__name__)

   @app.route('/')
   def index():
       return send_from_directory('web_port', 'index.html')

   @app.route('/<path:path>')
   def serve_static(path):
       return send_from_directory('web_port', path)
   ```

   **Django:**
   Add to `urls.py`:
   ```python
   from django.views.generic import TemplateView

   urlpatterns = [
       path('game/', TemplateView.as_view(template_name='web_port/index.html')),
   ]
   ```

   **FastAPI:**
   ```python
   from fastapi import FastAPI
   from fastapi.staticfiles import StaticFiles
   from fastapi.responses import FileResponse

   app = FastAPI()

   app.mount("/static", StaticFiles(directory="web_port"), name="static")

   @app.get("/")
   async def read_index():
       return FileResponse('web_port/index.html')
   ```

3. **Configure CORS** if your API is on a different domain

### Deploy to Static Hosting

The game can also be deployed to:
- **GitHub Pages** - Free static hosting
- **Netlify** - Free tier with CI/CD
- **Vercel** - Free tier with serverless functions
- **AWS S3 + CloudFront** - Scalable static hosting

Simply upload the entire `web_port` folder.

## Customization

### Adjust Game Difficulty

Edit `js/config.js`:

```javascript
SPEED_INCREMENT: 0.005,        // Increase for harder game
INITIAL_OBSTACLE_SPEED: 2,     // Starting speed
INITIAL_SPAWN_RATE: 0.02,      // Obstacle frequency
```

### Change Colors

Edit `js/config.js`:

```javascript
COLORS: {
    WHITE: 0xFFFFFF,
    BLACK: 0x000000,
    RED: 0xFF0000,
    LIGHT_GREEN: 0x90EE90
}
```

### Modify Screen Size

Edit `js/config.js`:

```javascript
SCREEN_WIDTH: 800,   // Game width
SCREEN_HEIGHT: 600,  // Game height
```

## Offline Support

The game includes local storage fallback for the leaderboard. When the backend API is unavailable:
- Scores are saved to browser's localStorage
- Leaderboard is read from localStorage
- Works completely offline

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile Safari (iOS 13+)
- ✅ Chrome Mobile (Android 5+)

## Performance Tips

1. **Optimize images** - Use compressed PNG files
2. **Compress audio** - Consider using OGG format for smaller file sizes
3. **Enable caching** - Configure your web server to cache assets
4. **Use a CDN** - Host assets on a CDN for faster loading

## Troubleshooting

### Game doesn't load
- Check browser console for errors
- Ensure you're running from a web server (not file://)
- Check that all asset files are in the correct folders

### Audio doesn't play
- Some browsers require user interaction before playing audio
- Check that audio files are in MP3 format
- Verify the mute setting (press M to unmute)

### Touch controls don't work
- Ensure you're testing on an actual touch device
- Check that preventDefault is working in main.js

### Leaderboard not saving
- Check API_BASE_URL in config.js
- Verify backend is running and accessible
- Check browser console for CORS errors

## Development

To modify the game:

1. Edit scene files in `js/scenes/`
2. Refresh browser to see changes
3. Use browser DevTools for debugging
4. Test on both desktop and mobile

## License

Same as the original Special Day Dodger game.

## Credits

- Original Pygame version by Andreas
- Web port using Phaser.js 3.70
- All assets from the original game
