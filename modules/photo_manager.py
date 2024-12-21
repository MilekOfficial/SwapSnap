import os
import random
from datetime import datetime
from flask import Blueprint, jsonify, current_app, session, request
import logging
import json

photo_bp = Blueprint('photo', __name__, url_prefix='/api')
logger = logging.getLogger(__name__)

def get_metadata():
    """Get all photo metadata from the JSON file."""
    try:
        metadata_file = os.path.join(current_app.config['UPLOAD_FOLDER'], 'metadata.json')
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error reading metadata: {str(e)}")
        return {}

def get_all_photos():
    """Get all photos from the metadata."""
    try:
        metadata = get_metadata()
        return sorted(
            [
                {
                    'filename': filename,
                    **photo_data
                }
                for filename, photo_data in metadata.items()
            ],
            key=lambda x: x['timestamp'],
            reverse=True
        )
    except Exception as e:
        logger.error(f"Error getting photos: {str(e)}")
        return []

def save_photo_metadata(photo_data):
    """Save photo metadata to the JSON file."""
    try:
        metadata_file = os.path.join(current_app.config['UPLOAD_FOLDER'], 'metadata.json')
        metadata = get_metadata()
        
        # Add the new photo
        metadata[photo_data['filename']] = photo_data
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(metadata_file), exist_ok=True)
        
        # Save to file
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
            
        return True
    except Exception as e:
        logger.error(f"Error saving photo metadata: {str(e)}")
        return False

@photo_bp.route('/photos', methods=['GET'])
def get_photos():
    """API endpoint to get all photos."""
    try:
        photos = get_all_photos()
        if not photos:
            return jsonify({
                'success': False,
                'error': 'No photos found'
            }), 404
            
        return jsonify({
            'success': True,
            'photos': photos
        }), 200
    except Exception as e:
        logger.error(f"Error getting photos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get photos'
        }), 500

@photo_bp.route('/photos/random', methods=['GET'])
def random_photo():
    """Get a random photo, avoiding the last shown photo if possible."""
    try:
        photos = get_all_photos()
        if not photos:
            return jsonify({
                'success': False,
                'error': 'No photos found'
            }), 404

        # Get the last shown photo from session
        last_shown = session.get('last_shown_photo')
        available_photos = [p for p in photos if p['filename'] != last_shown]
        
        # If we've shown all photos or there's only one photo, reset and show any
        if not available_photos:
            available_photos = photos
            
        # Get a random photo
        photo = random.choice(available_photos)
        
        # Store this photo as the last shown
        session['last_shown_photo'] = photo['filename']
        
        return jsonify({
            'success': True,
            'photo': photo
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting random photo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get random photo'
        }), 500
