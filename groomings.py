from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db
from models.pet import Pet
from models.grooming import Grooming
from services.reminder_engine import run_reminder_scan

groomings_bp = Blueprint('groomings', __name__, url_prefix='/groomings')

def get_user_pets():
    return Pet.query.filter_by(user_id=current_user.id).all()

def verify_pet_ownership(pet_id):
    pet = Pet.query.get(pet_id)
    if not pet or pet.user_id != current_user.id:
        abort(403)
    return pet

@groomings_bp.route('/')
@login_required
def list_groomings():
    pet_filter = request.args.get('pet_id', type=int)
    care_filter = request.args.get('care_type', '')

    user_pets = get_user_pets()
    user_pet_ids = [p.id for p in user_pets]

    query = Grooming.query.filter(Grooming.pet_id.in_(user_pet_ids))
    if pet_filter and pet_filter in user_pet_ids:
        query = query.filter_by(pet_id=pet_filter)
    if care_filter:
        query = query.filter_by(care_type=care_filter)

    records = query.order_by(Grooming.next_due_date.asc()).all()
    care_types = ['Bath', 'Nail trimming', 'Hair trimming', 'Ear cleaning', 'Dental cleaning', 'Other']
    return render_template('groomings/list.html', records=records, user_pets=user_pets, selected_pet=pet_filter, care_filter=care_filter, care_types=care_types)

@groomings_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_grooming():
    user_pets = get_user_pets()
    if not user_pets:
        flash('Please add a pet first.', 'warning')
        return redirect(url_for('pets.add_pet'))

    care_types = ['Bath', 'Nail trimming', 'Hair trimming', 'Ear cleaning', 'Dental cleaning', 'Other']

    if request.method == 'POST':
        pet_id = request.form.get('pet_id', type=int)
        care_type = request.form.get('care_type', '').strip()
        last_str = request.form.get('last_date')
        due_str = request.form.get('next_due_date')
        notes = request.form.get('notes', '').strip()

        if not pet_id or not care_type or not last_str or not due_str:
            flash('Pet, Care Type, Last Date, and Next Due Date are required.', 'danger')
            return render_template('groomings/form.html', record=None, user_pets=user_pets, care_types=care_types)

        verify_pet_ownership(pet_id)

        last_date = datetime.strptime(last_str, '%Y-%m-%d').date()
        next_due = datetime.strptime(due_str, '%Y-%m-%d').date()

        record = Grooming(
            pet_id=pet_id,
            care_type=care_type,
            last_date=last_date,
            next_due_date=next_due,
            notes=notes
        )
        db.session.add(record)
        db.session.commit()
        run_reminder_scan()

        flash('Grooming schedule added successfully!', 'success')
        return redirect(url_for('groomings.list_groomings'))

    preset_pet_id = request.args.get('pet_id', type=int)
    return render_template('groomings/form.html', record=None, user_pets=user_pets, care_types=care_types, preset_pet_id=preset_pet_id)

@groomings_bp.route('/<int:rec_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_grooming(rec_id):
    record = Grooming.query.get_or_404(rec_id)
    verify_pet_ownership(record.pet_id)
    user_pets = get_user_pets()
    care_types = ['Bath', 'Nail trimming', 'Hair trimming', 'Ear cleaning', 'Dental cleaning', 'Other']

    if request.method == 'POST':
        record.care_type = request.form.get('care_type', '').strip()
        last_str = request.form.get('last_date')
        due_str = request.form.get('next_due_date')
        record.notes = request.form.get('notes', '').strip()

        if last_str and due_str:
            record.last_date = datetime.strptime(last_str, '%Y-%m-%d').date()
            record.next_due_date = datetime.strptime(due_str, '%Y-%m-%d').date()

        db.session.commit()
        run_reminder_scan()
        flash('Grooming schedule updated!', 'success')
        return redirect(url_for('groomings.list_groomings'))

    return render_template('groomings/form.html', record=record, user_pets=user_pets, care_types=care_types)

@groomings_bp.route('/<int:rec_id>/delete', methods=['POST'])
@login_required
def delete_grooming(rec_id):
    record = Grooming.query.get_or_404(rec_id)
    verify_pet_ownership(record.pet_id)
    db.session.delete(record)
    db.session.commit()
    run_reminder_scan()
    flash('Grooming schedule deleted.', 'info')
    return redirect(url_for('groomings.list_groomings'))
