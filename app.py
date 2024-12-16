import json
import os
import random
from datetime import datetime

from flask import Flask, jsonify, render_template, request, send_from_directory, session
from werkzeug.utils import secure_filename

test = os.getenv('powi')
print(test)

# Initialize Flask app
app = Flask("SwapSnap")
app.secret_key = 'Hey'  # Change to a secure secret key

# Directory for uploaded files
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# File to store reactions
EMOJIS_FILE = 'emojis.json'

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Allowed emojis for reactions
EMOJI_REACTIONS = ['👍', '❤️', '😂', '😱', '😡']

# Helper functions for managing reactions
def load_reactions():
    """Load reactions from the emojis.json file."""
    try:
        with open(EMOJIS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_reactions(reactions):
    """Save reactions to the emojis.json file."""
    with open(EMOJIS_FILE, 'w') as f:
        json.dump(reactions, f)

def allowed_file(filename):
    """Check if a file is allowed based on its extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Home page."""
    # Initialize a unique session ID for the user
    if 'user_id' not in session:
        session['user_id'] = str(datetime.now().timestamp())
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Endpoint to upload a photo."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        return jsonify({'message': 'File uploaded successfully!', 'photo_url': f'/uploads/{filename}'}), 200
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/random_photo', methods=['GET'])
def random_photo():
    """Endpoint to get a random photo."""
    all_photos = [f'/uploads/{f}' for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
    if not all_photos:
        return jsonify({'error': 'No photos available'}), 400

    last_shown_photo = session.get('last_shown_photo', None)
    available_photos = [photo for photo in all_photos if photo != last_shown_photo]

    if not available_photos:
        return jsonify({'error': 'No new photos available'}), 400

    random_photo_url = random.choice(available_photos)
    session['last_shown_photo'] = random_photo_url

    reactions = load_reactions()
    current_reactions = reactions.get(random_photo_url, {})
    formatted_reactions = [{'user_id': user, 'emoji': emoji} for user, emoji in current_reactions.items()]

    return jsonify({'photo_url': random_photo_url, 'reactions': formatted_reactions}), 200

@app.route('/react', methods=['POST'])
def react():
    """Endpoint to react to a photo."""
    try:
        data = request.get_json()
        photo_url = data.get('photo_url')
        emoji = data.get('emoji')

        if not photo_url or not emoji:
            return jsonify({'error': 'Both photo_url and emoji are required'}), 400

        if emoji not in EMOJI_REACTIONS:
            return jsonify({'error': f'Invalid emoji. Valid emojis are: {", ".join(EMOJI_REACTIONS)}'}), 400

        reactions = load_reactions()
        user_id = session.get('user_id', str(datetime.now().timestamp()))
        session['user_id'] = user_id

        if photo_url not in reactions:
            reactions[photo_url] = {}
        reactions[photo_url][user_id] = emoji

        save_reactions(reactions)

        current_reactions = reactions[photo_url]
        formatted_reactions = [{'user_id': uid, 'emoji': e} for uid, e in current_reactions.items()]
        return jsonify({'message': 'Reaction added successfully!', 'reactions': formatted_reactions}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions# File to store reactions