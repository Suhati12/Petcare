import os
from datetime import datetime, date
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, abort
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.pet import Pet
from models.vet_visit import VetVisit
from services.reminder_engine import run_reminder_scan

vet_visits_bp = Blueprint('vet_visits', __name__, url_prefix='/vet-visits')

def get_user_pets():
    return Pet.query.filter_by(user_id=current_user.id).all()

def verify_pet_ownership(pet_id):
    pet = Pet.query.get(pet_id)
    if not pet or pet.user_id != current_user.id:
        abort(403)
    return pet

@vet_visits_bp.route('/')
@login_required
def list_visits():
    pet_filter = request.args.get('pet_id', type=int)
    tab = request.args.get('tab', 'upcoming')

    user_pets = get_user_pets()
    user_pet_ids = [p.id for p in user_pets]

    query = VetVisit.query.filter(VetVisit.pet_id.in_(user_pet_ids))
    if pet_filter and pet_filter in user_pet_ids:
        query = query.filter_by(pet_id=pet_filter)

    today = date.today()
    if tab == 'upcoming':
        query = query.filter(VetVisit.visit_date >= today).order_by(VetVisit.visit_date.asc())
    else:
        query = query.filter(VetVisit.visit_date < today).order_by(VetVisit.visit_date.desc())

    visits = query.all()
    return render_template('vet_visits/list.html', visits=visits, user_pets=user_pets, selected_pet=pet_filter, active_tab=tab)

@vet_visits_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_visit():
    user_pets = get_user_pets()
    if not user_pets:
        flash('Please add a pet first.', 'warning')
        return redirect(url_for('pets.add_pet'))

    if request.method == 'POST':
        pet_id = request.form.get('pet_id', type=int)
        vet_name = request.form.get('vet_name', '').strip()
        clinic = request.form.get('clinic', '').strip()
        visit_str = request.form.get('visit_date')
        visit_time = request.form.get('visit_time', '').strip()
        reason = request.form.get('reason', '').strip()
        diagnosis = request.form.get('diagnosis', '').strip()
        treatment = request.form.get('treatment', '').strip()
        prescription = request.form.get('prescription', '').strip()
        notes = request.form.get('notes', '').strip()
        follow_str = request.form.get('follow_up_date')

        if not pet_id or not visit_str or not reason:
            flash('Pet, Visit Date, and Reason are required.', 'danger')
            return render_template('vet_visits/form.html', visit=None, user_pets=user_pets)

        verify_pet_ownership(pet_id)

        v_date = datetime.strptime(visit_str, '%Y-%m-%d').date()
        f_date = datetime.strptime(follow_str, '%Y-%m-%d').date() if follow_str else None

        doc_filename = None
        if 'document' in request.files:
            file = request.files['document']
            if file and file.filename != '':
                filename = secure_filename(f"vet_{pet_id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
                upload_dir = current_app.config['DOC_UPLOADS']
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                doc_filename = filename

        visit = VetVisit(
            pet_id=pet_id,
            vet_name=vet_name,
            clinic=clinic,
            visit_date=v_date,
            visit_time=visit_time,
            reason=reason,
            diagnosis=diagnosis,
            treatment=treatment,
            prescription=prescription,
            notes=notes,
            follow_up_date=f_date,
            document_path=doc_filename
        )
        db.session.add(visit)
        db.session.commit()
        run_reminder_scan()

        flash('Veterinary visit recorded successfully!', 'success')
        return redirect(url_for('vet_visits.list_visits'))

    preset_pet_id = request.args.get('pet_id', type=int)
    return render_template('vet_visits/form.html', visit=None, user_pets=user_pets, preset_pet_id=preset_pet_id)

@vet_visits_bp.route('/<int:visit_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_visit(visit_id):
    visit = VetVisit.query.get_or_404(visit_id)
    verify_pet_ownership(visit.pet_id)
    user_pets = get_user_pets()

    if request.method == 'POST':
        visit.vet_name = request.form.get('vet_name', '').strip()
        visit.clinic = request.form.get('clinic', '').strip()
        visit_str = request.form.get('visit_date')
        visit.visit_time = request.form.get('visit_time', '').strip()
        visit.reason = request.form.get('reason', '').strip()
        visit.diagnosis = request.form.get('diagnosis', '').strip()
        visit.treatment = request.form.get('treatment', '').strip()
        visit.prescription = request.form.get('prescription', '').strip()
        visit.notes = request.form.get('notes', '').strip()
        follow_str = request.form.get('follow_up_date')

        if visit_str:
            visit.visit_date = datetime.strptime(visit_str, '%Y-%m-%d').date()
        visit.follow_up_date = datetime.strptime(follow_str, '%Y-%m-%d').date() if follow_str else None

        if 'document' in request.files:
            file = request.files['document']
            if file and file.filename != '':
                filename = secure_filename(f"vet_{visit.pet_id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
                upload_dir = current_app.config['DOC_UPLOADS']
                os.makedirs(upload_dir, exist_ok=True)
                file.save(os.path.join(upload_dir, filename))
                visit.document_path = filename

        db.session.commit()
        run_reminder_scan()
        flash('Vet visit record updated!', 'success')
        return redirect(url_for('vet_visits.list_visits'))

    return render_template('vet_visits/form.html', visit=visit, user_pets=user_pets)

@vet_visits_bp.route('/<int:visit_id>/delete', methods=['POST'])
@login_required
def delete_visit(visit_id):
    visit = VetVisit.query.get_or_404(visit_id)
    verify_pet_ownership(visit.pet_id)
    db.session.delete(visit)
    db.session.commit()
    run_reminder_scan()
    flash('Vet visit record deleted.', 'info')
    return redirect(url_for('vet_visits.list_visits'))
