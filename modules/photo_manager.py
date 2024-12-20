import os
import random
from datetime import datetime
from flask import Blueprint, jsonify, current_app, session
import logging
import json

photo_bp = Blueprint('photo', __name__)
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

@photo_bp.route('/api/photos', methods=['GET'])
def get_photos():
    """API endpoint to get all photos."""
    try:
        photos = get_all_photos()
        return jsonify({
            'success': True,
            'photos': photos
        }), 200
    except Exception as e:
        logger.error(f"Error in get_photos: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error fetching photos'
        }), 500

@photo_bp.route('/api/photos/random', methods=['GET'])
def random_photo():
    """Get a random photo, avoiding the last shown photo if possible."""
    try:
        photos = get_all_photos()
        if not photos:
            return jsonify({
                'success': False,
                'error': 'No photos available'
            }), 404

        last_shown = session.get('last_shown_photo')
        available_photos = [p for p in photos if p['filename'] != last_shown]

        if not available_photos:
            available_photos = photos  # If all photos shown, reset

        chosen_photo = random.choice(available_photos)
        session['last_shown_photo'] = chosen_photo['filename']

        return jsonify({
            'success': True,
            'photo': chosen_photo
        }), 200
    except Exception as e:
        logger.error(f"Error in random_photo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error fetching random photo'
        }), 500
