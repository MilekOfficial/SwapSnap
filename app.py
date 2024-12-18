import json
import os
import random
from datetime import datetime
from io import BytesIO
from urllib.parse import urljoin

from flask import Flask, jsonify, render_template, request, send_from_directory, session, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from PIL import Image


load_dotenv()  # Load environment variables from .env file

app = Flask("SwapSnap")
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-replace-in-production')

# Configure upload paths and URLs
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Base URL for the application
BASE_URL = os.getenv('BASE_URL', 'http://localhost:8000')

# File to store reactions (in the persistent storage)
EMOJIS_FILE = os.path.join(UPLOAD_FOLDER, 'emojis.json')

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Image size limits
MAX_SIZE = (1920, 1080)  # Maximum image size

# Allowed emojis for reactions
EMOJI_REACTIONS = ['👍', '❤️', '😂', '😱', '😡']

def get_full_url(path):
    """Generate full URL for a given path"""
    return urljoin(BASE_URL, path)

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

def optimize_image(image_file):
    """Optimize and resize image for web."""
    try:
        img = Image.open(image_file)
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
        
        # Auto-rotate image based on EXIF data
        try:
            img = Image.open(image_file)
            if hasattr(img, '_getexif'):
                exif = img._getexif()
                if exif:
                    orientation = exif.get(274)  # 274 is the orientation tag
                    if orientation:
                        rotate_values = {3: 180, 6: 270, 8: 90}
                        if orientation in rotate_values:
                            img = img.rotate(rotate_values[orientation], expand=True)
        except:
            pass  # If EXIF handling fails, continue with the original image
        
        # Resize if larger than MAX_SIZE
        if img.size[0] > MAX_SIZE[0] or img.size[1] > MAX_SIZE[1]:
            img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
        
        # Save optimized image
        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        
        return output
    except Exception as e:
        print(f"Error processing image: {e}")
        return None

@app.route('/')
def index():
    """Home page."""
    # Initialize a unique session ID for the user
    if 'user_id' not in session:
        session['user_id'] = str(datetime.now().timestamp())
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    """Upload and optimize a photo."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        # Generate a unique filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        original_filename = secure_filename(file.filename)
        base_filename = os.path.splitext(original_filename)[0]
        filename = f"{timestamp}_{base_filename}.jpg"
        
        # Process and optimize image
        optimized_image = optimize_image(file)
        if not optimized_image:
            return jsonify({'error': 'Error processing image'}), 400
        
        # Save optimized image
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        with open(filepath, 'wb') as f:
            f.write(optimized_image.getvalue())
        
        # Initialize reactions for the new photo
        reactions = load_reactions()
        reactions[filename] = {'reactions': {emoji: [] for emoji in EMOJI_REACTIONS}}
        save_reactions(reactions)
        
        photo_url = get_full_url(f'/uploads/{filename}')
        return jsonify({
            'success': True,
            'filename': filename,
            'photo_url': photo_url
        })
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/random_photo', methods=['GET'])
def random_photo():
    """Endpoint to get a random photo."""
    photos = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
    if not photos:
        return jsonify({'error': 'No photos available'}), 400

    last_shown_photo = session.get('last_shown_photo')
    available_photos = [p for p in photos if p != last_shown_photo]

    if not available_photos:
        available_photos = photos  # If all photos shown, reset

    chosen_photo = random.choice(available_photos)
    session['last_shown_photo'] = chosen_photo
    photo_url = get_full_url(f'/uploads/{chosen_photo}')

    reactions = load_reactions()
    current_reactions = reactions.get(chosen_photo, {'reactions': {}})
    formatted_reactions = [
        {'user_id': user, 'emoji': emoji}
        for emoji, users in current_reactions.get('reactions', {}).items()
        for user in users
    ]

    return jsonify({
        'photo_url': photo_url,
        'reactions': formatted_reactions
    }), 200

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
        reactions[photo_url]['reactions'][emoji].append(user_id)

        save_reactions(reactions)

        current_reactions = reactions[photo_url]['reactions']
        formatted_reactions = [{'user_id': user, 'emoji': emoji} for emoji, users in current_reactions.items() for user in users]
        return jsonify({'message': 'Reaction added successfully!', 'reactions': formatted_reactions}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/health')
def health_check():
    """Health check endpoint for Render."""
    try:
        # Check if we can access the upload directory
        os.listdir(UPLOAD_FOLDER)
        # Check if we can access the reactions file
        load_reactions()
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'upload_folder': 'accessible',
            'reactions_file': 'accessible'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

if __name__ == '__main__':
    # Use environment variables for host and port
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=False, host='0.0.0.0', port=port)