import json
import os
import random
from datetime import datetime
from io import BytesIO
import logging

from flask import Flask, jsonify, render_template, request, send_from_directory, session, url_for
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()  # Load environment variables from .env file

app = Flask("SwapSnap", static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-replace-in-production')

# Configure upload paths
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')  # Move uploads to static folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# File to store reactions (in the persistent storage)
EMOJIS_FILE = os.path.join(UPLOAD_FOLDER, 'emojis.json')

# Get base URL from environment or use default
BASE_URL = os.getenv('BASE_URL', 'https://swapsnap.studyshare.pl')

def get_full_url(path):
    """Generate a full URL for a given path."""
    if path.startswith('/'):
        path = path[1:]
    return f"{BASE_URL}/{path}"

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Image size limits
MAX_SIZE = (1920, 1080)  # Maximum image size

# Allowed emojis for reactions
EMOJI_REACTIONS = ['👍', '❤️', '😂', '😱', '😡']

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
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image_file):
    """Process and optimize the uploaded image."""
    try:
        # Open the image
        img = Image.open(image_file)
        
        # Convert RGBA to RGB if necessary
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')

        # Resize if too large (maintaining aspect ratio)
        max_size = (1920, 1080)
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Save to BytesIO
        output = BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        output.seek(0)
        return output
    except UnidentifiedImageError as e:
        logger.error(f"Error processing image: {str(e)}")
        raise ValueError("Invalid image file")
    except Exception as e:
        logger.error(f"Unexpected error processing image: {str(e)}")
        raise ValueError("Error processing image")

@app.route('/')
def index():
    """Home page."""
    # Initialize a unique session ID for the user
    if 'user_id' not in session:
        session['user_id'] = str(datetime.now().timestamp())
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle file upload."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400

        try:
            # Process the image
            processed_image = process_image(file)
            
            # Generate secure filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            original_filename = secure_filename(file.filename)
            base_filename = os.path.splitext(original_filename)[0]
            filename = f"{timestamp}_{base_filename}.jpg"
            
            # Save the processed image
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            with open(filepath, 'wb') as f:
                f.write(processed_image.getvalue())

            # Initialize reactions for this image
            reactions = load_reactions()
            reactions[filename] = {'reactions': {emoji: [] for emoji in EMOJI_REACTIONS}}
            save_reactions(reactions)
            
            photo_url = get_full_url(f'static/uploads/{filename}')
            return jsonify({
                'success': True,
                'filename': filename,
                'photo_url': photo_url
            }), 200

        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return jsonify({'error': 'Error saving file'}), 500

    except Exception as e:
        logger.error(f"Unexpected error in upload: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

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
    
    # Generate full URL using the BASE_URL
    photo_url = get_full_url(f'static/uploads/{chosen_photo}')

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