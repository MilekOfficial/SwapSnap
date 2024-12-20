from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from PIL import Image, UnidentifiedImageError
import os
import logging
from io import BytesIO
from datetime import datetime
import requests
import base64
import json

image_bp = Blueprint('image', __name__)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_WIDTH = 1920
MAX_HEIGHT = 1080
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_to_imgbb(image_data):
    """Upload image to imgbb and return the URL."""
    try:
        imgbb_key = os.getenv('IMGBB_API_KEY')
        if not imgbb_key:
            logger.error("IMGBB_API_KEY not found in environment variables")
            return None

        # Convert image data to base64
        base64_image = base64.b64encode(image_data.getvalue()).decode('utf-8')

        # Upload to imgbb
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": imgbb_key,
            "image": base64_image,
        }

        response = requests.post(url, data=payload)
        response.raise_for_status()
        
        data = response.json()
        if data.get('success'):
            return {
                'url': data['data']['url'],
                'delete_url': data['data']['delete_url'],
                'thumbnail': data['data']['thumb']['url']
            }
        return None

    except Exception as e:
        logger.error(f"Error uploading to imgbb: {str(e)}")
        return None

def process_image(image_file):
    try:
        img = Image.open(image_file)
        
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if needed while maintaining aspect ratio
        if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
            ratio = min(MAX_WIDTH/img.width, MAX_HEIGHT/img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Save with optimization
        output = BytesIO()
        img.save(output, format='JPEG', optimize=True, quality=85)
        output.seek(0)
        return output
        
    except UnidentifiedImageError as e:
        logger.error(f"Error processing image: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error processing image: {str(e)}")
        return None

@image_bp.route('/upload', methods=['POST'])
def upload_file():
    try:
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
            # Process the image
            processed_image = process_image(file)
            if processed_image is None:
                return jsonify({'error': 'Error processing image'}), 400
            
            # Upload to imgbb
            upload_result = upload_to_imgbb(processed_image)
            if not upload_result:
                return jsonify({'error': 'Error uploading to image host'}), 500

            # Store the image data
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            original_filename = secure_filename(file.filename)
            base_filename = os.path.splitext(original_filename)[0]
            filename = f"{timestamp}_{base_filename}.jpg"

            # Save metadata to database or file
            image_data = {
                'filename': filename,
                'url': upload_result['url'],
                'thumbnail': upload_result['thumbnail'],
                'delete_url': upload_result['delete_url'],
                'timestamp': datetime.now().isoformat()
            }

            # Save metadata to a JSON file
            metadata_file = os.path.join(current_app.config['UPLOAD_FOLDER'], 'metadata.json')
            try:
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                else:
                    metadata = {}
                
                metadata[filename] = image_data
                
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
            except Exception as e:
                logger.error(f"Error saving metadata: {str(e)}")

            return jsonify({
                'success': True,
                'filename': filename,
                'url': upload_result['url'],
                'thumbnail': upload_result['thumbnail']
            }), 200
            
        except Exception as e:
            logger.error(f"Error saving file: {str(e)}")
            return jsonify({'error': 'Error saving file'}), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in upload: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
