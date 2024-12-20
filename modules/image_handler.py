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
import humanize
import random

image_bp = Blueprint('image', __name__)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_WIDTH = 1920
MAX_HEIGHT = 1080
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_image_details(img, file_size):
    """Get image details including dimensions, size, and format."""
    return {
        'width': img.width,
        'height': img.height,
        'format': img.format.lower() if img.format else 'unknown',
        'size': humanize.naturalsize(file_size),
        'aspect_ratio': f"{img.width}:{img.height}"
    }

def fetch_imgbb_images():
    """Fetch all images from ImgBB account."""
    try:
        imgbb_key = os.getenv('IMGBB_API_KEY')
        if not imgbb_key:
            logger.error("IMGBB_API_KEY not found in environment variables")
            return None

        # Fetch images from ImgBB
        url = f"https://api.imgbb.com/1/account/images?key={imgbb_key}&page=1"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        if data.get('status') == 200 and 'data' in data:
            images = []
            for img in data['data'].get('images', []):
                try:
                    image_data = {
                        'url': img['url'],
                        'thumbnail': img.get('thumb', {}).get('url') or img['url'],
                        'filename': img.get('title', 'Untitled'),
                        'delete_url': img.get('delete_url', ''),
                        'timestamp': datetime.fromtimestamp(int(img.get('time', 0))).isoformat(),
                        'details': {
                            'processed': {
                                'width': int(img.get('width', 0)),
                                'height': int(img.get('height', 0)),
                                'size': humanize.naturalsize(int(img.get('size', 0))),
                                'format': img.get('extension', '').lower()
                            }
                        }
                    }
                    images.append(image_data)
                except (KeyError, ValueError) as e:
                    logger.error(f"Error processing image data: {str(e)}")
                    continue
            return images
        logger.error(f"Invalid response from ImgBB: {data}")
        return None

    except requests.exceptions.RequestException as e:
        logger.error(f"Request error fetching images from imgbb: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error fetching images from imgbb: {str(e)}")
        return None

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
                'thumbnail': data['data']['thumb']['url'],
                'size': data['data']['size'],
                'width': data['data']['width'],
                'height': data['data']['height']
            }
        return None

    except Exception as e:
        logger.error(f"Error uploading to imgbb: {str(e)}")
        return None

def process_image(image_file):
    try:
        # Get original file size
        image_file.seek(0, os.SEEK_END)
        original_size = image_file.tell()
        image_file.seek(0)

        img = Image.open(image_file)
        original_format = img.format
        
        # Get original image details
        original_details = get_image_details(img, original_size)
        
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[3])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if needed while maintaining aspect ratio
        resized = False
        if img.width > MAX_WIDTH or img.height > MAX_HEIGHT:
            ratio = min(MAX_WIDTH/img.width, MAX_HEIGHT/img.height)
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            resized = True
        
        # Save with optimization
        output = BytesIO()
        save_format = 'JPEG' if original_format not in ['PNG', 'GIF'] else original_format
        
        if save_format == 'JPEG':
            img.save(output, format=save_format, optimize=True, quality=85)
        elif save_format == 'PNG':
            img.save(output, format=save_format, optimize=True)
        else:
            img.save(output, format=save_format)
            
        output.seek(0)
        
        # Get processed file size
        processed_size = output.getbuffer().nbytes
        
        # Get processed image details
        processed_details = get_image_details(img, processed_size)
        processed_details['resized'] = resized
        processed_details['compression_ratio'] = f"{(1 - processed_size/original_size) * 100:.1f}%"
        
        return output, original_details, processed_details
        
    except UnidentifiedImageError as e:
        logger.error(f"Error processing image: {str(e)}")
        return None, None, None
    except Exception as e:
        logger.error(f"Unexpected error processing image: {str(e)}")
        return None, None, None

@image_bp.route('/api/photos/random', methods=['GET'])
def get_random_photo():
    """Get a random photo from ImgBB."""
    try:
        images = fetch_imgbb_images()
        if not images:
            return jsonify({'error': 'No images found'}), 404

        photo = random.choice(images)
        return jsonify({
            'success': True,
            'photo': photo
        })

    except Exception as e:
        logger.error(f"Error getting random photo: {str(e)}")
        return jsonify({'error': 'Failed to get random photo'}), 500

@image_bp.route('/api/photos', methods=['GET'])
def get_all_photos():
    """Get all photos from ImgBB."""
    try:
        images = fetch_imgbb_images()
        if not images:
            return jsonify({'error': 'No images found'}), 404

        return jsonify({
            'success': True,
            'photos': images
        })

    except Exception as e:
        logger.error(f"Error getting photos: {str(e)}")
        return jsonify({'error': 'Failed to get photos'}), 500

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
            
        try:
            # Get file size without reading entire file into memory
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)
            
            if file_size > MAX_FILE_SIZE:
                return jsonify({'error': f'File too large. Maximum size is {humanize.naturalsize(MAX_FILE_SIZE)}'}), 400
            
            # Process the image
            processed_image, original_details, processed_details = process_image(file)
            if processed_image is None:
                return jsonify({'error': 'Error processing image'}), 400
            
            # Upload to imgbb
            upload_result = upload_to_imgbb(processed_image)
            if not upload_result:
                return jsonify({'error': 'Error uploading to image host'}), 500

            # Create response data
            response_data = {
                'success': True,
                'url': upload_result['url'],
                'thumbnail': upload_result['thumbnail'],
                'filename': secure_filename(file.filename),
                'timestamp': datetime.now().isoformat(),
                'details': {
                    'original': original_details,
                    'processed': {
                        'width': upload_result['width'],
                        'height': upload_result['height'],
                        'size': humanize.naturalsize(upload_result['size']),
                        'format': os.path.splitext(file.filename)[1][1:].lower()
                    }
                }
            }

            # Save metadata
            try:
                metadata_file = os.path.join(current_app.config['UPLOAD_FOLDER'], 'metadata.json')
                metadata = {}
                
                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                    except json.JSONDecodeError:
                        logger.warning("Invalid metadata file, creating new one")
                
                metadata[response_data['filename']] = response_data
                
                os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
                    
            except Exception as e:
                logger.error(f"Error saving metadata: {str(e)}")
                # Continue even if metadata save fails
            
            return jsonify(response_data), 200
            
        except Exception as e:
            logger.error(f"Error processing upload: {str(e)}")
            return jsonify({'error': 'Error processing upload'}), 500
            
    except Exception as e:
        logger.error(f"Unexpected error in upload: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred'}), 500
