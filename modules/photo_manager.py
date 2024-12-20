import os
import random
from datetime import datetime
from flask import Blueprint, jsonify, current_app, session
import logging

photo_bp = Blueprint('photo', __name__)
logger = logging.getLogger(__name__)

def get_all_photos():
    """Get all photos from the uploads directory."""
    try:
        upload_folder = current_app.config['UPLOAD_FOLDER']
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
        
        if not os.path.exists(upload_folder):
            logger.warning(f"Upload folder {upload_folder} does not exist")
            return []
            
        photos = [
            f for f in os.listdir(upload_folder)
            if '.' in f and f.rsplit('.', 1)[1].lower() in allowed_extensions
        ]
        return sorted(photos, key=lambda x: os.path.getctime(
            os.path.join(upload_folder, x)
        ), reverse=True)
    except Exception as e:
        logger.error(f"Error getting photos: {str(e)}")
        return []

@photo_bp.route('/api/photos', methods=['GET'])
def get_photos():
    """API endpoint to get all photos."""
    try:
        photos = get_all_photos()
        photo_urls = [
            {
                'filename': photo,
                'url': f'/uploads/{photo}',
                'timestamp': datetime.fromtimestamp(
                    os.path.getctime(
                        os.path.join(current_app.config['UPLOAD_FOLDER'], photo)
                    )
                ).isoformat()
            }
            for photo in photos
        ]
        return jsonify({
            'success': True,
            'photos': photo_urls
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
        available_photos = [p for p in photos if p != last_shown]

        if not available_photos:
            available_photos = photos  # If all photos shown, reset

        chosen_photo = random.choice(available_photos)
        session['last_shown_photo'] = chosen_photo

        # Get photo metadata
        photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], chosen_photo)
        photo_data = {
            'filename': chosen_photo,
            'url': f'/uploads/{chosen_photo}',
            'timestamp': datetime.fromtimestamp(
                os.path.getctime(photo_path)
            ).isoformat()
        }

        return jsonify({
            'success': True,
            'photo': photo_data
        }), 200
    except Exception as e:
        logger.error(f"Error in random_photo: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error fetching random photo'
        }), 500
