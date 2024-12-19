import json
import os
import random
from datetime import datetime
from io import BytesIO
import logging

from flask import Flask, jsonify, render_template, request, send_from_directory, session, url_for, redirect, flash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from PIL import Image, UnidentifiedImageError
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()  # Load environment variables from .env file

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/swapsnap')

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User Model
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# Create database tables
Base.metadata.create_all(engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

app = Flask("SwapSnap", static_folder='static')
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-replace-in-production')

# Configure upload paths
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'uploads')  # Move uploads to static folder
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# File to store reactions (in the persistent storage)
REACTIONS_FILE = os.path.join(UPLOAD_FOLDER, 'reactions.json')

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
    """Load reactions from the reactions.json file."""
    try:
        if os.path.exists(REACTIONS_FILE):
            with open(REACTIONS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading reactions: {str(e)}")
        return {}

def save_reactions(reactions):
    """Save reactions to the reactions.json file."""
    try:
        with open(REACTIONS_FILE, 'w') as f:
            json.dump(reactions, f)
    except Exception as e:
        logger.error(f"Error saving reactions: {str(e)}")

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
            reactions[filename] = {'reactions': {}}
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
def add_reaction():
    """Add a reaction to a photo."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        photo_url = data.get('photo_url')
        emoji = data.get('emoji')

        if not photo_url or not emoji:
            return jsonify({'error': 'Missing photo_url or emoji'}), 400

        # Extract filename from photo_url
        filename = photo_url.split('/')[-1]

        # Load current reactions
        reactions = load_reactions()
        
        # Initialize reactions for this photo if it doesn't exist
        if filename not in reactions:
            reactions[filename] = {'reactions': {}}
        
        # Initialize emoji array if it doesn't exist
        if 'reactions' not in reactions[filename]:
            reactions[filename]['reactions'] = {}
            
        if emoji not in reactions[filename]['reactions']:
            reactions[filename]['reactions'][emoji] = []

        # Generate a simple user ID based on session
        if 'user_id' not in session:
            session['user_id'] = f"user_{random.randint(1000, 9999)}"
        user_id = session['user_id']

        # Add reaction if not already added by this user
        if user_id not in reactions[filename]['reactions'][emoji]:
            reactions[filename]['reactions'][emoji].append(user_id)
            save_reactions(reactions)

        # Format reactions for response
        formatted_reactions = [
            {'emoji': e, 'user_id': uid}
            for e, users in reactions[filename]['reactions'].items()
            for uid in users
        ]

        return jsonify({
            'success': True,
            'reactions': formatted_reactions
        }), 200

    except Exception as e:
        logger.error(f"Error adding reaction: {str(e)}")
        return jsonify({'error': 'Error adding reaction'}), 500

@app.route('/auth')
def auth():
    """Render the authentication page."""
    return render_template('auth.html')

@app.route('/register', methods=['POST'])
def register():
    """Handle user registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not all([username, email, password, confirm_password]):
            flash('All fields are required', 'error')
            return redirect(url_for('auth'))

        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('auth'))

        db = get_db()
        try:
            # Check if user already exists
            if db.query(User).filter((User.username == username) | (User.email == email)).first():
                flash('Username or email already exists', 'error')
                return redirect(url_for('auth'))

            # Create new user
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            
            db.add(new_user)
            db.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth'))
        except Exception as e:
            db.rollback()
            logger.error(f"Registration error: {str(e)}")
            flash('An error occurred during registration', 'error')
            return redirect(url_for('auth'))
        finally:
            db.close()

@app.route('/login', methods=['POST'])
def login():
    """Handle user login."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not all([email, password]):
            flash('Email and password are required', 'error')
            return redirect(url_for('auth'))

        db = get_db()
        try:
            user = db.query(User).filter_by(email=email).first()
            
            if user and user.check_password(password):
                session['user_id'] = user.id
                session['username'] = user.username
                
                # Update last login
                user.last_login = datetime.utcnow()
                db.commit()
                
                flash('Login successful!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Invalid email or password', 'error')
                return redirect(url_for('auth'))
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            flash('An error occurred during login', 'error')
            return redirect(url_for('auth'))
        finally:
            db.close()

@app.route('/logout')
def logout():
    """Handle user logout."""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('auth'))

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