from flask import Flask, render_template, request, jsonify, session
import json
import requests
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Change to a secure secret key

# ImgBB API Key (replace with your actual API key)
IMGBB_API_KEY = "d7b117945f830b61ece628f1705dc4bc"

# Reactions file to store emoji reactions
EMOJIS_FILE = 'emojis.json'

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

@app.route('/')
def index():
    """Home page."""
    # Initialize a unique session ID for the user
    if 'user_id' not in session:
        session['user_id'] = str(datetime.now().timestamp())
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Endpoint to upload a photo to ImgBB."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Upload the image to ImgBB
    try:
        response = requests.post(
            f"https://api.imgbb.com/1/upload?key={IMGBB_API_KEY}",
            files={'image': file}
        )
        response_data = response.json()

        if response.status_code == 200 and response_data.get('success'):
            image_url = response_data['data']['url']
            return jsonify({'message': 'File uploaded successfully!', 'photo_url': image_url}), 200
        else:
            return jsonify({'error': 'ImgBB upload failed', 'details': response_data.get('error')}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/random_photo', methods=['GET'])
def random_photo():
    """Endpoint to get a random photo."""
    reactions = load_reactions()
    photo_urls = list(reactions.keys())

    if not photo_urls:
        return jsonify({'error': 'No photos available'}), 400

    last_shown_photo = session.get('last_shown_photo', None)
    available_photos = [url for url in photo_urls if url != last_shown_photo]

    if not available_photos:
        return jsonify({'error': 'No new photos available'}), 400

    # Select a random photo
    random_photo_url = random.choice(available_photos)
    session['last_shown_photo'] = random_photo_url

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
    # Use Gunicorn for production (e.g., `gunicorn -w 4 -b 0.0.0.0:8000 app:app`)
    app.run(debug=True, host='0.0.0.0', port=8000)
