from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.reminder import Reminder
from models.pet import Pet
from services.reminder_engine import run_reminder_scan

reminders_bp = Blueprint('reminders', __name__, url_prefix='/reminders')

@reminders_bp.route('/')
@login_required
def list_reminders():
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')
    pet_filter = request.args.get('pet_id', type=int)

    user_pets = Pet.query.filter_by(user_id=current_user.id).all()
    user_pet_ids = [p.id for p in user_pets]

    # First auto-rescan reminders to ensure dynamic dates match
    run_reminder_scan()

    query = Reminder.query.filter_by(user_id=current_user.id)

    if category_filter:
        query = query.filter_by(category=category_filter)
    if pet_filter and pet_filter in user_pet_ids:
        query = query.filter_by(pet_id=pet_filter)

    reminders = query.order_by(Reminder.due_date.asc()).all()

    if status_filter:
        reminders = [r for r in reminders if r.computed_status == status_filter]

    categories = ['Vaccination', 'Deworming', 'Medication', 'Grooming', 'Vet Visit', 'General']
    statuses = ['Overdue', 'Due Today', 'Due Tomorrow', 'Due Soon', 'Upcoming', 'Completed']

    return render_template(
        'reminders/list.html',
        reminders=reminders,
        user_pets=user_pets,
        selected_cat=category_filter,
        selected_status=status_filter,
        selected_pet=pet_filter,
        categories=categories,
        statuses=statuses
    )

@reminders_bp.route('/<int:rem_id>/complete', methods=['POST'])
@login_required
def mark_completed(rem_id):
    reminder = Reminder.query.get_or_404(rem_id)
    if reminder.user_id != current_user.id:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('reminders.list_reminders'))

    reminder.status = 'Completed'
    db.session.commit()
    flash(f'Reminder "{reminder.title}" marked as Completed!', 'success')
    return redirect(url_for('reminders.list_reminders'))

@reminders_bp.route('/trigger-check', methods=['POST', 'GET'])
@login_required
def trigger_check():
    res = run_reminder_scan()
    flash(f"Smart Reminder Engine Executed! Processed {res['processed_records']} records, dispatched {res['notifications_created']} alerts.", 'success')
    return redirect(url_for('reminders.list_reminders'))
