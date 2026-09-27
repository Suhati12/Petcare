from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db
from models.pet import Pet
from models.medication import Medication
from services.reminder_engine import run_reminder_scan

medications_bp = Blueprint('medications', __name__, url_prefix='/medications')

def get_user_pets():
    return Pet.query.filter_by(user_id=current_user.id).all()

def verify_pet_ownership(pet_id):
    pet = Pet.query.get(pet_id)
    if not pet or pet.user_id != current_user.id:
        abort(403)
    return pet

@medications_bp.route('/')
@login_required
def list_medications():
    pet_filter = request.args.get('pet_id', type=int)
    status_tab = request.args.get('status', 'Active')

    user_pets = get_user_pets()
    user_pet_ids = [p.id for p in user_pets]

    query = Medication.query.filter(Medication.pet_id.in_(user_pet_ids))
    if pet_filter and pet_filter in user_pet_ids:
        query = query.filter_by(pet_id=pet_filter)

    if status_tab in ['Active', 'Completed']:
        query = query.filter_by(status=status_tab)

    meds = query.order_by(Medication.start_date.desc()).all()
    return render_template('medications/list.html', medications=meds, user_pets=user_pets, selected_pet=pet_filter, active_tab=status_tab)

@medications_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_medication():
    user_pets = get_user_pets()
    if not user_pets:
        flash('Please add a pet first.', 'warning')
        return redirect(url_for('pets.add_pet'))

    if request.method == 'POST':
        pet_id = request.form.get('pet_id', type=int)
        medicine_name = request.form.get('medicine_name', '').strip()
        purpose = request.form.get('purpose', '').strip()
        start_str = request.form.get('start_date')
        end_str = request.form.get('end_date')
        frequency = request.form.get('frequency', '').strip()
        time_slot = request.form.get('time', '').strip()
        dosage = request.form.get('dosage', '').strip()
        instructions = request.form.get('instructions', '').strip()
        notes = request.form.get('notes', '').strip()

        if not pet_id or not medicine_name or not start_str or not end_str or not dosage or not frequency:
            flash('Required fields missing.', 'danger')
            return render_template('medications/form.html', medication=None, user_pets=user_pets)

        verify_pet_ownership(pet_id)

        start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_str, '%Y-%m-%d').date()

        if end_date < start_date:
            flash('End Date cannot be before Start Date.', 'danger')
            return render_template('medications/form.html', medication=None, user_pets=user_pets)

        medication = Medication(
            pet_id=pet_id,
            medicine_name=medicine_name,
            purpose=purpose,
            start_date=start_date,
            end_date=end_date,
            frequency=frequency,
            time=time_slot,
            dosage=dosage,
            instructions=instructions,
            notes=notes,
            status='Active'
        )
        db.session.add(medication)
        db.session.commit()
        run_reminder_scan()

        flash('Medication schedule added successfully!', 'success')
        return redirect(url_for('medications.list_medications'))

    preset_pet_id = request.args.get('pet_id', type=int)
    return render_template('medications/form.html', medication=None, user_pets=user_pets, preset_pet_id=preset_pet_id)

@medications_bp.route('/<int:med_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_medication(med_id):
    medication = Medication.query.get_or_404(med_id)
    verify_pet_ownership(medication.pet_id)
    user_pets = get_user_pets()

    if request.method == 'POST':
        medication.medicine_name = request.form.get('medicine_name', '').strip()
        medication.purpose = request.form.get('purpose', '').strip()
        start_str = request.form.get('start_date')
        end_str = request.form.get('end_date')
        medication.frequency = request.form.get('frequency', '').strip()
        medication.time = request.form.get('time', '').strip()
        medication.dosage = request.form.get('dosage', '').strip()
        medication.instructions = request.form.get('instructions', '').strip()
        medication.notes = request.form.get('notes', '').strip()
        medication.status = request.form.get('status', 'Active')

        if start_str and end_str:
            medication.start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            medication.end_date = datetime.strptime(end_str, '%Y-%m-%d').date()

        db.session.commit()
        run_reminder_scan()
        flash('Medication updated!', 'success')
        return redirect(url_for('medications.list_medications'))

    return render_template('medications/form.html', medication=medication, user_pets=user_pets)

@medications_bp.route('/<int:med_id>/toggle-status', methods=['POST'])
@login_required
def toggle_status(med_id):
    medication = Medication.query.get_or_404(med_id)
    verify_pet_ownership(medication.pet_id)
    medication.status = 'Completed' if medication.status == 'Active' else 'Active'
    db.session.commit()
    run_reminder_scan()
    flash(f'Medication status set to {medication.status}.', 'info')
    return redirect(url_for('medications.list_medications'))

@medications_bp.route('/<int:med_id>/delete', methods=['POST'])
@login_required
def delete_medication(med_id):
    medication = Medication.query.get_or_404(med_id)
    verify_pet_ownership(medication.pet_id)
    db.session.delete(medication)
    db.session.commit()
    run_reminder_scan()
    flash('Medication schedule deleted.', 'info')
    return redirect(url_for('medications.list_medications'))
