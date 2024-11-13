from flask import Flask, render_template, request, jsonify, send_from_directory, session
import os
import random
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Secret key for session management (required for sessions to work)
app.secret_key = 'your_secret_key_here'

# Setup paths for image uploads
UPLOAD_FOLDER = 'static/uploads'
EMOJI_REACTIONS = ['👍', '❤️', '😂', '😱', '😡']

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory storage for reactions (could be replaced with a database for production)
reactions = {}

# Serve uploaded images from the static folder
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to upload a photo
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Save the file
    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    return jsonify({'message': 'File uploaded successfully!', 'photo_url': f'/uploads/{filename}'}), 200

# Endpoint to get a random photo
@app.route('/random_photo', methods=['GET'])
def random_photo():
    # Scan the entire uploads folder for photos
    all_photos = [os.path.join(UPLOAD_FOLDER, f) for f in os.listdir(UPLOAD_FOLDER) if f.lower().endswith(('png', 'jpg', 'jpeg', 'gif', 'bmp'))]

    if not all_photos:
        return jsonify({'error': 'No photos uploaded yet'}), 400
    
    # Get the last shown photo from session
    last_shown_photo = session.get('last_shown_photo')

    # Filter out the last shown photo to avoid duplicates
    available_photos = [photo for photo in all_photos if photo != last_shown_photo]
    
    if not available_photos:
        return jsonify({'error': 'No more new photos available'}), 400
    
    # Select a random photo from the available ones
    random_photo_path = random.choice(available_photos)
    
    # Store the current photo in session
    session['last_shown_photo'] = random_photo_path

    # Fetch current reactions (if any)
    current_reactions = reactions.get(random_photo_path, {})

    # Format reactions as a list of emojis for display
    formatted_reactions = []
    for user_id, emoji in current_reactions.items():
        formatted_reactions.append({'user_id': user_id, 'emoji': emoji})

    return jsonify({'photo_url': random_photo_path, 'reactions': formatted_reactions}), 200

# Endpoint to react to a photo
@app.route('/react', methods=['POST'])
def react():
    try:
        # Get the request data
        data = request.get_json()
        photo_url = data.get('photo_url')
        emoji = data.get('emoji')

        # Check if both photo_url and emoji are provided
        if not photo_url or not emoji:
            return jsonify({'error': 'Both photo_url and emoji are required'}), 400

        # Validate the emoji
        if emoji not in EMOJI_REACTIONS:
            return jsonify({'error': f'Invalid emoji. Valid emojis are: {", ".join(EMOJI_REACTIONS)}'}), 400

        # Check if the photo exists in the filesystem
        photo_path = os.path.join(UPLOAD_FOLDER, photo_url[1:])  # Remove initial "/" to get the correct file path
        if not os.path.exists(photo_path):
            return jsonify({'error': 'Photo not found'}), 400

        # Get the user ID from the session (this is unique for each user)
        user_id = session.get('user_id')

        # If no user_id is set, assign one (or you could implement login/authentication for real applications)
        if not user_id:
            session['user_id'] = str(datetime.now().timestamp())  # Using timestamp as a unique user ID for demo

        user_id = session['user_id']

        # Initialize reactions for the photo if they don't exist
        if photo_url not in reactions:
            reactions[photo_url] = {}

        # Replace the user's old reaction with the new one
        reactions[photo_url][user_id] = emoji

        # After reaction, return the updated reactions for the photo
        current_reactions = reactions[photo_url]

        # Format reactions to return
        formatted_reactions = [{'user_id': user_id, 'emoji': emoji} for user_id, emoji in current_reactions.items()]

        return jsonify({'message': 'Reaction added successfully!', 'reactions': formatted_reactions}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
