from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from datetime import date
from models.pet import Pet
from models.vaccination import Vaccination
from models.deworming import Deworming
from models.medication import Medication
from models.grooming import Grooming
from models.vet_visit import VetVisit
from models.reminder import Reminder
from models.notification import Notification

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    today = date.today()

    # User pets
    pets = Pet.query.filter_by(user_id=current_user.id).all()
    pet_ids = [p.id for p in pets]

    if not pet_ids:
        return render_template(
            'main/dashboard.html',
            total_pets=0,
            vaccinations_due_soon=0,
            overdue_count=0,
            upcoming_appointments=0,
            active_medications=0,
            todays_tasks=[],
            upcoming_reminders=[],
            overdue_reminders=[],
            category_chart_data={'labels': [], 'data': []},
            status_chart_data={'completed': 0, 'pending': 0, 'overdue': 0},
            pets=[]
        )

    # 1. Stat Card Calculations
    # Vaccinations due soon (0 <= days_remaining <= 7) or overdue
    all_vaccines = Vaccination.query.filter(Vaccination.pet_id.in_(pet_ids)).all()
    vacc_due_soon = sum(1 for v in all_vaccines if 0 <= v.days_remaining <= 7)

    # Active medications
    active_meds = Medication.query.filter(Medication.pet_id.in_(pet_ids), Medication.status == 'Active').count()

    # Upcoming vet appointments
    all_vet = VetVisit.query.filter(VetVisit.pet_id.in_(pet_ids)).all()
    upcoming_vet = sum(1 for v in all_vet if v.is_upcoming)

    # Reminders query
    user_reminders = Reminder.query.filter_by(user_id=current_user.id).all()

    todays_tasks = [r for r in user_reminders if r.due_date == today and r.status != 'Completed']
    overdue_reminders = [r for r in user_reminders if r.due_date < today and r.status != 'Completed']
    upcoming_reminders = [r for r in user_reminders if r.due_date > today and r.status != 'Completed']
    
    # Sort upcoming by date
    upcoming_reminders.sort(key=lambda r: r.due_date)

    overdue_count = len(overdue_reminders)

    # 2. Chart 1: Care tasks by Category
    categories = ['Vaccination', 'Deworming', 'Medication', 'Grooming', 'Vet Visit']
    cat_counts = []
    for cat in categories:
        count = sum(1 for r in user_reminders if r.category == cat)
        cat_counts.append(count)

    category_chart_data = {
        'labels': categories,
        'data': cat_counts
    }

    # 3. Chart 2: Completed vs Pending vs Overdue
    completed_count = sum(1 for r in user_reminders if r.status == 'Completed')
    pending_count = sum(1 for r in user_reminders if r.status != 'Completed' and r.due_date >= today)
    status_chart_data = {
        'completed': completed_count,
        'pending': pending_count,
        'overdue': overdue_count
    }

    return render_template(
        'main/dashboard.html',
        total_pets=len(pets),
        vaccinations_due_soon=vacc_due_soon,
        overdue_count=overdue_count,
        upcoming_appointments=upcoming_vet,
        active_medications=active_meds,
        todays_tasks=todays_tasks,
        upcoming_reminders=upcoming_reminders[:10],
        overdue_reminders=overdue_reminders,
        category_chart_data=category_chart_data,
        status_chart_data=status_chart_data,
        pets=pets
    )

@main_bp.route('/search')
@login_required
def search():
    query = request.args.get('q', '').strip()
    if not query:
        return render_template('main/search_results.html', query='', pets=[], vaccines=[], medications=[], vet_visits=[])

    user_pet_ids = [p.id for p in Pet.query.filter_by(user_id=current_user.id).all()]

    matched_pets = Pet.query.filter(
        Pet.user_id == current_user.id,
        (Pet.name.ilike(f'%{query}%')) | (Pet.breed.ilike(f'%{query}%')) | (Pet.species.ilike(f'%{query}%'))
    ).all()

    matched_vaccines = Vaccination.query.filter(
        Vaccination.pet_id.in_(user_pet_ids),
        (Vaccination.vaccine_name.ilike(f'%{query}%')) | (Vaccination.veterinarian.ilike(f'%{query}%'))
    ).all()

    matched_meds = Medication.query.filter(
        Medication.pet_id.in_(user_pet_ids),
        (Medication.medicine_name.ilike(f'%{query}%')) | (Medication.purpose.ilike(f'%{query}%'))
    ).all()

    matched_visits = VetVisit.query.filter(
        VetVisit.pet_id.in_(user_pet_ids),
        (VetVisit.reason.ilike(f'%{query}%')) | (VetVisit.vet_name.ilike(f'%{query}%')) | (VetVisit.diagnosis.ilike(f'%{query}%'))
    ).all()

    return render_template(
        'main/search_results.html',
        query=query,
        pets=matched_pets,
        vaccines=matched_vaccines,
        medications=matched_meds,
        vet_visits=matched_visits
    )
