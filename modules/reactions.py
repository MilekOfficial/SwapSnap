from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
import json
import os
import logging

reactions_bp = Blueprint('reactions', __name__)
logger = logging.getLogger(__name__)

REACTIONS_FILE = 'reactions.json'

def load_reactions():
    try:
        if os.path.exists(REACTIONS_FILE):
            with open(REACTIONS_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading reactions: {str(e)}")
        return {}

def save_reactions(reactions):
    try:
        with open(REACTIONS_FILE, 'w') as f:
            json.dump(reactions, f)
    except Exception as e:
        logger.error(f"Error saving reactions: {str(e)}")

@reactions_bp.route('/api/reaction', methods=['POST'])
@login_required
def add_reaction():
    try:
        data = request.get_json()
        if not data or 'photo' not in data or 'reaction' not in data:
            return jsonify({'error': 'Missing required fields'}), 400

        photo = data['photo']
        reaction = data['reaction']
        user_id = current_user.id

        reactions = load_reactions()
        
        if photo not in reactions:
            reactions[photo] = {'reactions': {}}
            
        if user_id in reactions[photo]['reactions']:
            old_reaction = reactions[photo]['reactions'][user_id]
            reactions[photo][old_reaction] = reactions[photo].get(old_reaction, 0) - 1
            
        reactions[photo]['reactions'][user_id] = reaction
        reactions[photo][reaction] = reactions[photo].get(reaction, 0) + 1
        
        save_reactions(reactions)
        
        return jsonify({
            'success': True,
            'reactions': reactions[photo]
        }), 200
        
    except Exception as e:
        logger.error(f"Error in add_reaction: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500
