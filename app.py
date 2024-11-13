from flask import Flask, render_template, request, jsonify, send_from_directory, session
import os
import json
import random
from datetime import datetime
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)

# Secret key for session management
app.secret_key = 'your_secret_key_here'

# Setup paths and constants
UPLOAD_FOLDER = 'static/uploads'
EMOJIS_FILE = 'emojis.json'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
EMOJI_REACTIONS = ['👍', '❤️', '😂', '😱', '😡']

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper functions for managing reactions
def load_reactions():
    """Load reactions from the emojis.json file."""
    if os.path.exists(EMOJIS_FILE):
        with open(EMOJIS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_reactions(reactions):
    """Save reactions to the emojis.json file."""
    with open(EMOJIS_FILE, 'w') as f:
        json.dump(reactions, f)

# Serve uploaded images from the static folder
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/')
def index():
    # Initialize a unique session ID for the user
    if 'user_id' not in session:
        session['user_id'] = str(datetime.now().timestamp())
    return render_template('index.html')

# Endpoint to upload a photo
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return jsonify({'message': 'File uploaded successfully!', 'photo_url': f'/uploads/{filename}'}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400

# Endpoint to get a random photo
@app.route('/random_photo', methods=['GET'])
def random_photo():
    # Scan the entire uploads folder for photos
    all_photos = [f'/uploads/{f}' for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith(tuple(ALLOWED_EXTENSIONS))]
    if not all_photos:
        return jsonify({'error': 'No photos uploaded yet'}), 400
    
    # Get the last shown photo from session
    last_shown_photo = session.get('last_shown_photo')

    # Filter out the last shown photo
    available_photos = [photo for photo in all_photos if photo != last_shown_photo]
    if not available_photos:
        return jsonify({'error': 'No more new photos available'}), 400

    # Select a random photo
    random_photo_url = random.choice(available_photos)
    session['last_shown_photo'] = random_photo_url

    # Load current reactions
    reactions = load_reactions()
    current_reactions = reactions.get(random_photo_url, {})

    # Format reactions
    formatted_reactions = [{'user_id': user, 'emoji': emoji} for user, emoji in current_reactions.items()]

    return jsonify({'photo_url': random_photo_url, 'reactions': formatted_reactions}), 200

# Endpoint to react to a photo
@app.route('/react', methods=['POST'])
def react():
    try:
        # Get request data
        data = request.get_json()
        photo_url = data.get('photo_url')
        emoji = data.get('emoji')

        if not photo_url or not emoji:
            return jsonify({'error': 'Both photo_url and emoji are required'}), 400

        if emoji not in EMOJI_REACTIONS:
            return jsonify({'error': f'Invalid emoji. Valid emojis are: {", ".join(EMOJI_REACTIONS)}'}), 400

        # Load reactions
        reactions = load_reactions()

        # Get user ID
        user_id = session.get('user_id', str(datetime.now().timestamp()))
        session['user_id'] = user_id

        # Add or update reaction
        if photo_url not in reactions:
            reactions[photo_url] = {}
        reactions[photo_url][user_id] = emoji

        # Save updated reactions
        save_reactions(reactions)

        # Format and return updated reactions
        current_reactions = reactions[photo_url]
        formatted_reactions = [{'user_id': uid, 'emoji': e} for uid, e in current_reactions.items()]
        return jsonify({'message': 'Reaction added successfully!', 'reactions': formatted_reactions}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
