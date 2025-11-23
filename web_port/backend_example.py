"""
Example Flask Backend for Special Day Dodger
Provides leaderboard API endpoints for the web game

Installation:
    pip install flask flask-cors

Usage:
    python backend_example.py

Then update js/config.js to set:
    API_BASE_URL: 'http://localhost:5000/api'
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# In-memory leaderboard (replace with database in production)
LEADERBOARD_FILE = 'leaderboard.json'

def load_leaderboard():
    """Load leaderboard from file"""
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, 'r') as f:
            return json.load(f)
    return []

def save_leaderboard(data):
    """Save leaderboard to file"""
    with open(LEADERBOARD_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    """API information"""
    return jsonify({
        'name': 'Special Day Dodger API',
        'version': '1.0',
        'endpoints': {
            'GET /api/leaderboard': 'Get top 5 scores',
            'POST /api/score': 'Submit a new score'
        }
    })

@app.route('/api/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get the top 5 scores"""
    leaderboard = load_leaderboard()
    # Sort by score descending and return top 5
    sorted_board = sorted(leaderboard, key=lambda x: x['score'], reverse=True)[:5]
    return jsonify(sorted_board)

@app.route('/api/score', methods=['POST'])
def submit_score():
    """Submit a new score to the leaderboard"""
    try:
        data = request.json

        # Validate input
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        name = data.get('name', '').upper()
        score = data.get('score', 0)

        # Validate name (3 characters)
        if not name or len(name) != 3:
            return jsonify({'success': False, 'message': 'Name must be 3 characters'}), 400

        # Validate score
        if not isinstance(score, int) or score < 0:
            return jsonify({'success': False, 'message': 'Invalid score'}), 400

        # Load current leaderboard
        leaderboard = load_leaderboard()

        # Add new score
        new_entry = {
            'name': name,
            'score': score,
            'timestamp': data.get('timestamp', int(datetime.now().timestamp() * 1000)),
            'submitted_at': datetime.now().isoformat()
        }

        leaderboard.append(new_entry)

        # Sort and keep top 100 (or whatever limit you want)
        leaderboard = sorted(leaderboard, key=lambda x: x['score'], reverse=True)[:100]

        # Save to file
        save_leaderboard(leaderboard)

        # Check if score made it to top 5
        top_5 = leaderboard[:5]
        made_top_5 = new_entry in top_5

        return jsonify({
            'success': True,
            'message': 'Score submitted successfully',
            'rank': leaderboard.index(new_entry) + 1,
            'top_5': made_top_5
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get leaderboard statistics"""
    leaderboard = load_leaderboard()

    if not leaderboard:
        return jsonify({
            'total_scores': 0,
            'highest_score': 0,
            'average_score': 0
        })

    scores = [entry['score'] for entry in leaderboard]

    return jsonify({
        'total_scores': len(leaderboard),
        'highest_score': max(scores),
        'average_score': sum(scores) / len(scores),
        'unique_players': len(set(entry['name'] for entry in leaderboard))
    })

if __name__ == '__main__':
    print("=" * 60)
    print("Special Day Dodger - Backend Server")
    print("=" * 60)
    print("\nServer starting on http://localhost:5000")
    print("\nAvailable endpoints:")
    print("  GET  / - API information")
    print("  GET  /api/leaderboard - Top 5 scores")
    print("  POST /api/score - Submit new score")
    print("  GET  /api/stats - Leaderboard statistics")
    print("\nDon't forget to update js/config.js with:")
    print("  API_BASE_URL: 'http://localhost:5000/api'")
    print("\n" + "=" * 60 + "\n")

    app.run(host='0.0.0.0', port=5000, debug=True)
