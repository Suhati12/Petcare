import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.pet import Pet
from models.vaccination import Vaccination
from models.deworming import Deworming
from models.medication import Medication
from models.grooming import Grooming
from models.vet_visit import VetVisit
from services.qr_generator import generate_pet_qr_code

pets_bp = Blueprint('pets', __name__, url_prefix='/pets')

def get_user_pet_or_404(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.user_id != current_user.id:
        abort(403)  # Unauthorized access prevention
    return pet

@pets_bp.route('/')
@login_required
def list_pets():
    species_filter = request.args.get('species', '')
    gender_filter = request.args.get('gender', '')
    search_q = request.args.get('q', '').strip()

    query = Pet.query.filter_by(user_id=current_user.id)

    if species_filter:
        query = query.filter_by(species=species_filter)
    if gender_filter:
        query = query.filter_by(gender=gender_filter)
    if search_q:
        query = query.filter(Pet.name.ilike(f'%{search_q}%') | Pet.breed.ilike(f'%{search_q}%'))

    pets = query.order_by(Pet.created_at.desc()).all()
    return render_template('pets/list.html', pets=pets, species_filter=species_filter, gender_filter=gender_filter, search_q=search_q)

@pets_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_pet():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        species = request.form.get('species', '').strip()
        breed = request.form.get('breed', '').strip()
        gender = request.form.get('gender', '').strip()
        dob_str = request.form.get('dob')
        weight_str = request.form.get('weight')
        color = request.form.get('color', '').strip()
        microchip_id = request.form.get('microchip_id', '').strip()
        allergies = request.form.get('allergies', '').strip()
        medical_conditions = request.form.get('medical_conditions', '').strip()
        emergency_notes = request.form.get('emergency_notes', '').strip()

        if not name or not species or not gender:
            flash('Pet Name, Species, and Gender are required.', 'danger')
            return render_template('pets/form.html', pet=None)

        dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
        weight = float(weight_str) if weight_str else None

        # Check unique microchip ID if provided
        if microchip_id:
            existing = Pet.query.filter_by(microchip_id=microchip_id).first()
            if existing:
                flash('A pet with this Microchip ID already exists in the system.', 'warning')
                return render_template('pets/form.html', pet=None)

        # Photo upload
        photo_filename = 'default_pet.png'
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                filename = secure_filename(f"{current_user.id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
                upload_dir = current_app.config['PET_UPLOADS']
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                photo_filename = filename

        pet = Pet(
            user_id=current_user.id,
            name=name,
            species=species,
            breed=breed,
            gender=gender,
            dob=dob,
            weight=weight,
            color=color,
            microchip_id=microchip_id if microchip_id else None,
            photo=photo_filename,
            allergies=allergies,
            medical_conditions=medical_conditions,
            emergency_notes=emergency_notes
        )
        db.session.add(pet)
        db.session.commit()

        flash(f'Pet "{pet.name}" added successfully!', 'success')
        return redirect(url_for('pets.view_pet', pet_id=pet.id))

    return render_template('pets/form.html', pet=None)

@pets_bp.route('/<int:pet_id>')
@login_required
def view_pet(pet_id):
    pet = get_user_pet_or_404(pet_id)

    vaccinations = Vaccination.query.filter_by(pet_id=pet.id).order_by(Vaccination.next_due_date.asc()).all()
    dewormings = Deworming.query.filter_by(pet_id=pet.id).order_by(Deworming.next_due_date.asc()).all()
    medications = Medication.query.filter_by(pet_id=pet.id).order_by(Medication.start_date.desc()).all()
    groomings = Grooming.query.filter_by(pet_id=pet.id).order_by(Grooming.next_due_date.asc()).all()
    vet_visits = VetVisit.query.filter_by(pet_id=pet.id).order_by(VetVisit.visit_date.desc()).all()

    return render_template(
        'pets/detail.html',
        pet=pet,
        vaccinations=vaccinations,
        dewormings=dewormings,
        medications=medications,
        groomings=groomings,
        vet_visits=vet_visits
    )

@pets_bp.route('/<int:pet_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_pet(pet_id):
    pet = get_user_pet_or_404(pet_id)

    if request.method == 'POST':
        pet.name = request.form.get('name', '').strip()
        pet.species = request.form.get('species', '').strip()
        pet.breed = request.form.get('breed', '').strip()
        pet.gender = request.form.get('gender', '').strip()
        dob_str = request.form.get('dob')
        weight_str = request.form.get('weight')
        pet.color = request.form.get('color', '').strip()
        microchip = request.form.get('microchip_id', '').strip()
        pet.allergies = request.form.get('allergies', '').strip()
        pet.medical_conditions = request.form.get('medical_conditions', '').strip()
        pet.emergency_notes = request.form.get('emergency_notes', '').strip()

        pet.dob = datetime.strptime(dob_str, '%Y-%m-%d').date() if dob_str else None
        pet.weight = float(weight_str) if weight_str else None
        pet.microchip_id = microchip if microchip else None

        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '':
                filename = secure_filename(f"{current_user.id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
                upload_dir = current_app.config['PET_UPLOADS']
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                pet.photo = filename

        db.session.commit()
        flash(f'Pet "{pet.name}" updated successfully!', 'success')
        return redirect(url_for('pets.view_pet', pet_id=pet.id))

    return render_template('pets/form.html', pet=pet)

@pets_bp.route('/<int:pet_id>/delete', methods=['POST'])
@login_required
def delete_pet(pet_id):
    pet = get_user_pet_or_404(pet_id)
    pet_name = pet.name
    db.session.delete(pet)
    db.session.commit()
    flash(f'Pet "{pet_name}" deleted.', 'info')
    return redirect(url_for('pets.list_pets'))

@pets_bp.route('/<int:pet_id>/qr')
@login_required
def emergency_qr(pet_id):
    pet = get_user_pet_or_404(pet_id)
    emergency_url = url_for('pets.public_emergency_profile', pet_id=pet.id, _external=True)
    qr_data_uri = generate_pet_qr_code(emergency_url)
    return render_template('pets/qr_profile.html', pet=pet, qr_data_uri=qr_data_uri, emergency_url=emergency_url)

@pets_bp.route('/public-emergency/<int:pet_id>')
def public_emergency_profile(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    # Only expose essential emergency information for finder/first responder
    return render_template('pets/public_emergency.html', pet=pet)
