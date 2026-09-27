from flask import Blueprint, render_template, request, abort
from flask_login import login_required, current_user
from models.pet import Pet
from models.vaccination import Vaccination
from models.deworming import Deworming
from models.medication import Medication
from models.grooming import Grooming
from models.vet_visit import VetVisit

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def reports_index():
    user_pets = Pet.query.filter_by(user_id=current_user.id).all()
    selected_pet_id = request.args.get('pet_id', type=int)

    pet = None
    if selected_pet_id:
        pet = Pet.query.get(selected_pet_id)
        if pet and pet.user_id != current_user.id:
            abort(403)
    elif user_pets:
        pet = user_pets[0]

    vaccinations = Vaccination.query.filter_by(pet_id=pet.id).all() if pet else []
    dewormings = Deworming.query.filter_by(pet_id=pet.id).all() if pet else []
    medications = Medication.query.filter_by(pet_id=pet.id).all() if pet else []
    groomings = Grooming.query.filter_by(pet_id=pet.id).all() if pet else []
    vet_visits = VetVisit.query.filter_by(pet_id=pet.id).all() if pet else []

    return render_template(
        'reports/reports.html',
        user_pets=user_pets,
        selected_pet=pet,
        vaccinations=vaccinations,
        dewormings=dewormings,
        medications=medications,
        groomings=groomings,
        vet_visits=vet_visits
    )

@reports_bp.route('/pet/<int:pet_id>/print')
@login_required
def print_health_report(pet_id):
    pet = Pet.query.get_or_404(pet_id)
    if pet.user_id != current_user.id:
        abort(403)

    vaccinations = Vaccination.query.filter_by(pet_id=pet.id).order_by(Vaccination.next_due_date.asc()).all()
    dewormings = Deworming.query.filter_by(pet_id=pet.id).order_by(Deworming.next_due_date.asc()).all()
    medications = Medication.query.filter_by(pet_id=pet.id).order_by(Medication.start_date.desc()).all()
    groomings = Grooming.query.filter_by(pet_id=pet.id).order_by(Grooming.next_due_date.asc()).all()
    vet_visits = VetVisit.query.filter_by(pet_id=pet.id).order_by(VetVisit.visit_date.desc()).all()

    return render_template(
        'reports/health_report.html',
        pet=pet,
        owner=current_user,
        vaccinations=vaccinations,
        dewormings=dewormings,
        medications=medications,
        groomings=groomings,
        vet_visits=vet_visits
    )
