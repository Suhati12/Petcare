from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db
from models.pet import Pet
from models.deworming import Deworming
from services.reminder_engine import run_reminder_scan

dewormings_bp = Blueprint('dewormings', __name__, url_prefix='/dewormings')

def get_user_pets():
    return Pet.query.filter_by(user_id=current_user.id).all()

def verify_pet_ownership(pet_id):
    pet = Pet.query.get(pet_id)
    if not pet or pet.user_id != current_user.id:
        abort(403)
    return pet

@dewormings_bp.route('/')
@login_required
def list_dewormings():
    pet_filter = request.args.get('pet_id', type=int)
    user_pets = get_user_pets()
    user_pet_ids = [p.id for p in user_pets]

    query = Deworming.query.filter(Deworming.pet_id.in_(user_pet_ids))
    if pet_filter and pet_filter in user_pet_ids:
        query = query.filter_by(pet_id=pet_filter)

    records = query.order_by(Deworming.next_due_date.asc()).all()
    return render_template('dewormings/list.html', records=records, user_pets=user_pets, selected_pet=pet_filter)

@dewormings_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_deworming():
    user_pets = get_user_pets()
    if not user_pets:
        flash('Please add a pet first.', 'warning')
        return redirect(url_for('pets.add_pet'))

    if request.method == 'POST':
        pet_id = request.form.get('pet_id', type=int)
        medicine = request.form.get('medicine', '').strip()
        dose = request.form.get('dose', '').strip()
        date_str = request.form.get('deworming_date')
        due_str = request.form.get('next_due_date')
        notes = request.form.get('notes', '').strip()

        if not pet_id or not medicine or not date_str or not due_str:
            flash('Pet, Medicine, Administered Date, and Next Due Date are required.', 'danger')
            return render_template('dewormings/form.html', record=None, user_pets=user_pets)

        verify_pet_ownership(pet_id)

        dew_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        due_date = datetime.strptime(due_str, '%Y-%m-%d').date()

        record = Deworming(
            pet_id=pet_id,
            medicine=medicine,
            dose=dose,
            deworming_date=dew_date,
            next_due_date=due_date,
            notes=notes
        )
        db.session.add(record)
        db.session.commit()
        run_reminder_scan()

        flash('Deworming record added successfully!', 'success')
        return redirect(url_for('dewormings.list_dewormings'))

    preset_pet_id = request.args.get('pet_id', type=int)
    return render_template('dewormings/form.html', record=None, user_pets=user_pets, preset_pet_id=preset_pet_id)

@dewormings_bp.route('/<int:rec_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_deworming(rec_id):
    record = Deworming.query.get_or_404(rec_id)
    verify_pet_ownership(record.pet_id)
    user_pets = get_user_pets()

    if request.method == 'POST':
        record.medicine = request.form.get('medicine', '').strip()
        record.dose = request.form.get('dose', '').strip()
        date_str = request.form.get('deworming_date')
        due_str = request.form.get('next_due_date')
        record.notes = request.form.get('notes', '').strip()

        if date_str and due_str:
            record.deworming_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            record.next_due_date = datetime.strptime(due_str, '%Y-%m-%d').date()

        db.session.commit()
        run_reminder_scan()
        flash('Deworming record updated!', 'success')
        return redirect(url_for('dewormings.list_dewormings'))

    return render_template('dewormings/form.html', record=record, user_pets=user_pets)

@dewormings_bp.route('/<int:rec_id>/delete', methods=['POST'])
@login_required
def delete_deworming(rec_id):
    record = Deworming.query.get_or_404(rec_id)
    verify_pet_ownership(record.pet_id)
    db.session.delete(record)
    db.session.commit()
    run_reminder_scan()
    flash('Deworming record deleted.', 'info')
    return redirect(url_for('dewormings.list_dewormings'))
