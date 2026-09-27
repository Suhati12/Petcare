from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from models import db
from models.pet import Pet
from models.reminder import Reminder
from models.notification import Notification

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/pets', methods=['GET'])
@login_required
def get_pets():
    pets = Pet.query.filter_by(user_id=current_user.id).all()
    return jsonify([p.to_dict() for p in pets])

@api_bp.route('/pets/<int:pet_id>', methods=['GET'])
@login_required
def get_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(pet.to_dict())

@api_bp.route('/pets', methods=['POST'])
@login_required
def create_pet():
    data = request.get_json() or {}
    name = data.get('name')
    species = data.get('species')
    gender = data.get('gender')

    if not name or not species or not gender:
        return jsonify({'error': 'Name, species, and gender are required.'}), 400

    pet = Pet(
        user_id=current_user.id,
        name=name,
        species=species,
        breed=data.get('breed'),
        gender=gender,
        weight=data.get('weight'),
        color=data.get('color'),
        microchip_id=data.get('microchip_id'),
        allergies=data.get('allergies'),
        medical_conditions=data.get('medical_conditions'),
        emergency_notes=data.get('emergency_notes')
    )
    db.session.add(pet)
    db.session.commit()
    return jsonify(pet.to_dict()), 210

@api_bp.route('/pets/<int:pet_id>', methods=['PUT'])
@login_required
def update_pet(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json() or {}
    if 'name' in data: pet.name = data['name']
    if 'species' in data: pet.species = data['species']
    if 'breed' in data: pet.breed = data['breed']
    if 'gender' in data: pet.gender = data['gender']
    if 'weight' in data: pet.weight = data['weight']
    if 'color' in data: pet.color = data['color']
    if 'allergies' in data: pet.allergies = data['allergies']

    db.session.commit()
    return jsonify(pet.to_dict())

@api_bp.route('/pets/<int:pet_id>', methods=['DELETE'])
@login_required
def delete_pet_api(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.user_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(pet)
    db.session.commit()
    return jsonify({'message': f'Pet {pet_id} deleted successfully.'})

@api_bp.route('/reminders', methods=['GET'])
@login_required
def get_reminders():
    reminders = Reminder.query.filter_by(user_id=current_user.id).order_by(Reminder.due_date.asc()).all()
    return jsonify([r.to_dict() for r in reminders])

@api_bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return jsonify([n.to_dict() for n in notifications])
