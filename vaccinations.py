import os
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.pet import Pet
from models.vaccination import Vaccination
from services.reminder_engine import run_reminder_scan

vaccinations_bp = Blueprint('vaccinations', __name__, url_prefix='/vaccinations')

def get_user_pets():
    return Pet.query.filter_by(user_id=current_user.id).all()

def verify_pet_ownership(pet_id):
    pet = Pet.query.get(pet_id)
    if not pet or pet.user_id != current_user.id:
        abort(403)
    return pet

@vaccinations_bp.route('/')
@login_required
def list_vaccinations():
    pet_filter = request.args.get('pet_id', type=int)
    status_filter = request.args.get('status', '')

    user_pets = get_user_pets()
    user_pet_ids = [p.id for p in user_pets]

    query = Vaccination.query.filter(Vaccination.pet_id.in_(user_pet_ids))

    if pet_filter and pet_filter in user_pet_ids:
        query = query.filter_by(pet_id=pet_filter)

    vaccinations = query.order_by(Vaccination.next_due_date.asc()).all()

    if status_filter:
        vaccinations = [v for v in vaccinations if v.status == status_filter]

    return render_template('vaccinations/list.html', vaccinations=vaccinations, user_pets=user_pets, selected_pet=pet_filter, selected_status=status_filter)

@vaccinations_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_vaccination():
    user_pets = get_user_pets()
    if not user_pets:
        flash('Please add a pet before recording a vaccination.', 'warning')
        return redirect(url_for('pets.add_pet'))

    if request.method == 'POST':
        pet_id = request.form.get('pet_id', type=int)
        vaccine_name = request.form.get('vaccine_name', '').strip()
        vaccine_type = request.form.get('vaccine_type', '').strip()
        administered_str = request.form.get('date_administered')
        due_str = request.form.get('next_due_date')
        veterinarian = request.form.get('veterinarian', '').strip()
        clinic = request.form.get('clinic', '').strip()
        dose = request.form.get('dose', '').strip()
        notes = request.form.get('notes', '').strip()

        if not pet_id or not vaccine_name or not administered_str or not due_str:
            flash('Pet, Vaccine Name, Date Administered, and Next Due Date are required.', 'danger')
            return render_template('vaccinations/form.html', vaccination=None, user_pets=user_pets)

        verify_pet_ownership(pet_id)

        admin_date = datetime.strptime(administered_str, '%Y-%m-%d').date()
        due_date = datetime.strptime(due_str, '%Y-%m-%d').date()

        if due_date < admin_date:
            flash('Next Due Date cannot be earlier than Date Administered.', 'danger')
            return render_template('vaccinations/form.html', vaccination=None, user_pets=user_pets)

        doc_filename = None
        if 'document' in request.files:
            file = request.files['document']
            if file and file.filename != '':
                filename = secure_filename(f"vac_{pet_id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
                upload_dir = current_app.config['DOC_UPLOADS']
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                doc_filename = filename

        vaccination = Vaccination(
            pet_id=pet_id,
            vaccine_name=vaccine_name,
            vaccine_type=vaccine_type,
            date_administered=admin_date,
            next_due_date=due_date,
            veterinarian=veterinarian,
            clinic=clinic,
            dose=dose,
            notes=notes,
            document_path=doc_filename
        )
        db.session.add(vaccination)
        db.session.commit()

        # Trigger smart reminder engine update
        run_reminder_scan()

        flash('Vaccination record added successfully!', 'success')
        return redirect(url_for('vaccinations.list_vaccinations'))

    # Pre-select pet if passed in query param
    preset_pet_id = request.args.get('pet_id', type=int)
    return render_template('vaccinations/form.html', vaccination=None, user_pets=user_pets, preset_pet_id=preset_pet_id)

@vaccinations_bp.route('/<int:vac_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_vaccination(vac_id):
    vaccination = Vaccination.query.get_or_404(vac_id)
    verify_pet_ownership(vaccination.pet_id)
    user_pets = get_user_pets()

    if request.method == 'POST':
        vaccination.vaccine_name = request.form.get('vaccine_name', '').strip()
        vaccination.vaccine_type = request.form.get('vaccine_type', '').strip()
        admin_str = request.form.get('date_administered')
        due_str = request.form.get('next_due_date')
        vaccination.veterinarian = request.form.get('veterinarian', '').strip()
        vaccination.clinic = request.form.get('clinic', '').strip()
        vaccination.dose = request.form.get('dose', '').strip()
        vaccination.notes = request.form.get('notes', '').strip()

        if admin_str and due_str:
            admin_date = datetime.strptime(admin_str, '%Y-%m-%d').date()
            due_date = datetime.strptime(due_str, '%Y-%m-%d').date()
            if due_date < admin_date:
                flash('Next Due Date cannot be earlier than Date Administered.', 'danger')
                return render_template('vaccinations/form.html', vaccination=vaccination, user_pets=user_pets)
            vaccination.date_administered = admin_date
            vaccination.next_due_date = due_date

        if 'document' in request.files:
            file = request.files['document']
            if file and file.filename != '':
                filename = secure_filename(f"vac_{vaccination.pet_id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
                upload_dir = current_app.config['DOC_UPLOADS']
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                vaccination.document_path = filename

        db.session.commit()
        run_reminder_scan()
        flash('Vaccination record updated!', 'success')
        return redirect(url_for('vaccinations.list_vaccinations'))

    return render_template('vaccinations/form.html', vaccination=vaccination, user_pets=user_pets)

@vaccinations_bp.route('/<int:vac_id>/delete', methods=['POST'])
@login_required
def delete_vaccination(vac_id):
    vaccination = Vaccination.query.get_or_404(vac_id)
    verify_pet_ownership(vaccination.pet_id)
    db.session.delete(vaccination)
    db.session.commit()
    run_reminder_scan()
    flash('Vaccination record deleted.', 'info')
    return redirect(url_for('vaccinations.list_vaccinations'))
