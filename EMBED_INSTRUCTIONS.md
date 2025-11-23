# How to Embed Special Day Dodger in Your Website

## Overview
The Special Day Dodger game has been successfully converted to run in web browsers using Pygbag. The game runs using WebAssembly and can be embedded in any website.

## What Was Built
The build process created these files in `build/web/`:
- `index.html` - The main game page
- `special_day_dodger.apk` - The packaged game assets (despite the .apk extension, this is for web)
- `favicon.png` - Game icon

## Deployment Options

### Option 1: Direct Hosting
Upload the entire `build/web/` directory to your web server and link to `index.html`.

### Option 2: Iframe Embed
Embed the game in your existing website using an iframe:

```html
<iframe
    src="https://yourwebsite.com/path/to/build/web/index.html"
    width="800"
    height="600"
    style="border: none;"
    allowfullscreen>
</iframe>
```

### Option 3: Custom Integration
Copy the contents of `build/web/` to your website and customize the `index.html` file to match your site's styling.

## Example HTML Page

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Play Special Day Dodger</title>
    <style>
        body {
            margin: 0;
            padding: 20px;
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        h1 {
            color: #333;
        }
        .game-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        iframe {
            display: block;
            border: 2px solid #333;
            border-radius: 5px;
        }
    </style>
</head>
<body>
    <h1>Special Day Dodger</h1>
    <div class="game-container">
        <iframe
            src="build/web/index.html"
            width="800"
            height="600"
            allowfullscreen>
        </iframe>
    </div>
    <p>Help Andreas dodge wedding responsibilities! Use arrow keys to move and spacebar to shoot.</p>
</body>
</html>
```

## Important Notes

### Audio Limitation
The web version currently runs **without audio** because:
- Web browsers require OGG format audio files
- The original game uses MP3 files
- To add audio in the future, convert the MP3 files in `/audio/` to OGG format

### Leaderboard Storage
- Desktop version: Saves to `leaderboard.json` file
- Web version: Saves to browser's localStorage (persists between sessions on the same browser)

### Browser Compatibility
The game requires a modern browser with WebAssembly support:
- Chrome/Edge 57+
- Firefox 52+
- Safari 11+

## Testing Locally

To test the web build locally, you need to serve it with a web server (not just open the file):

```bash
# Using Python
cd build/web
python -m http.server 8000

# Then visit: http://localhost:8000
```

## Next Steps (Optional)

### To Add Audio:
1. Convert MP3 files to OGG format:
   ```bash
   ffmpeg -i audio/whistle_tune.mp3 audio/whistle_tune.ogg
   ffmpeg -i audio/special_day.mp3 audio/special_day.ogg
   ```
2. Rebuild with `pygbag --build main.py`

### To Customize:
- Edit `build/web/index.html` to change colors, add your branding, etc.
- Modify canvas size by changing SCREEN_WIDTH and SCREEN_HEIGHT in main.py and rebuilding

## File Size
The complete build is approximately 12MB due to the Pygame + Python WebAssembly runtime and game assets (images, fonts).
