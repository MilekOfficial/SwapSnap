from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
import os
import logging
from io import BytesIO

image_bp = Blueprint('image', __name__)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_WIDTH = 1920
MAX_HEIGHT = 1080
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_image(image_file):
    try:
        img = Image.open(image_file)
        
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        
        # Resize if needed while maintaining aspect ratio
        if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
            ratio = min(MAX_WIDTH/img.width, MAX_HEIGHT/img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Save with optimization
        output = BytesIO()
        img.save(output, format=img.format, optimize=True, quality=85)
        output.seek(0)
        return output
        
    except UnidentifiedImageError as e:
        logger.error(f"Error processing image: {str(e)}")
        return None

@image_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
        
    if file.content_length and file.content_length > MAX_FILE_SIZE:
        return jsonify({'error': 'File too large'}), 400
        
    try:
        filename = secure_filename(file.filename)
        processed_image = process_image(file)
        
        if processed_image is None:
            return jsonify({'error': 'Error processing image'}), 400
            
        # Save the processed image
        upload_path = os.path.join('uploads', filename)
        with open(upload_path, 'wb') as f:
            f.write(processed_image.getvalue())
            
        return jsonify({'success': True, 'filename': filename}), 200
        
    except Exception as e:
        logger.error(f"Error in upload_file: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
