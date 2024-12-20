import os
from flask import Flask, render_template, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_minify import Minify
from dotenv import load_dotenv
import logging

from modules.auth import auth_bp, login_manager
from modules.image_handler import image_bp
from modules.reactions import reactions_bp
from modules.photo_manager import photo_bp

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

load_dotenv()

# Initialize Flask app
app = Flask("SwapSnap", static_folder='static')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key-replace-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

# Initialize Flask extensions
Minify(app=app, html=True, js=True, cssless=True)
login_manager.init_app(app)
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(image_bp)
app.register_blueprint(reactions_bp)
app.register_blueprint(photo_bp)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded files."""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/health')
@limiter.exempt
def health_check():
    """Health check endpoint for monitoring."""
    try:
        return {'status': 'healthy'}, 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {'status': 'unhealthy', 'error': str(e)}, 500

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {str(error)}")
    return render_template('500.html'), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=False, host='0.0.0.0', port=port)