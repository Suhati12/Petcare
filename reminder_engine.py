from datetime import date, datetime
from models import db
from models.pet import Pet
from models.vaccination import Vaccination
from models.deworming import Deworming
from models.medication import Medication
from models.grooming import Grooming
from models.vet_visit import VetVisit
from models.reminder import Reminder
from services.notification_service import create_notification

def run_reminder_scan():
    """
    Scans all pet care records across the system, calculates dynamic due dates,
    synchronizes Reminder records, and generates notifications for overdue/due soon items.
    """
    processed_count = 0
    notifications_created = 0
    today = date.today()

    pets = Pet.query.all()
    for pet in pets:
        owner_id = pet.user_id

        # 1. Check Vaccinations
        vaccinations = Vaccination.query.filter_by(pet_id=pet.id).all()
        for v in vaccinations:
            title = f"Vaccination: {v.vaccine_name}"
            reminder = Reminder.query.filter_by(
                user_id=owner_id, pet_id=pet.id, category='Vaccination', reference_id=v.id
            ).first()
            if not reminder:
                reminder = Reminder(
                    user_id=owner_id,
                    pet_id=pet.id,
                    title=title,
                    category='Vaccination',
                    due_date=v.next_due_date,
                    reference_id=v.id
                )
                db.session.add(reminder)
            else:
                reminder.due_date = v.next_due_date
                reminder.title = title

            # Calculate status
            days = (v.next_due_date - today).days
            status_str = _compute_status(days)
            reminder.status = status_str
            processed_count += 1

            # Dispatch Notification if needed
            if days <= 7:
                msg = _build_message(pet.name, f"vaccination ({v.vaccine_name})", days)
                create_notification(owner_id, pet.id, title, msg, 'Vaccination')
                notifications_created += 1

        # 2. Check Dewormings
        dewormings = Deworming.query.filter_by(pet_id=pet.id).all()
        for d in dewormings:
            title = f"Deworming: {d.medicine}"
            reminder = Reminder.query.filter_by(
                user_id=owner_id, pet_id=pet.id, category='Deworming', reference_id=d.id
            ).first()
            if not reminder:
                reminder = Reminder(
                    user_id=owner_id,
                    pet_id=pet.id,
                    title=title,
                    category='Deworming',
                    due_date=d.next_due_date,
                    reference_id=d.id
                )
                db.session.add(reminder)
            else:
                reminder.due_date = d.next_due_date
                reminder.title = title

            days = (d.next_due_date - today).days
            reminder.status = _compute_status(days)
            processed_count += 1

            if days <= 7:
                msg = _build_message(pet.name, f"deworming ({d.medicine})", days)
                create_notification(owner_id, pet.id, title, msg, 'Deworming')
                notifications_created += 1

        # 3. Check Medications (Active ones)
        medications = Medication.query.filter_by(pet_id=pet.id, status='Active').all()
        for m in medications:
            title = f"Medication: {m.medicine_name}"
            reminder = Reminder.query.filter_by(
                user_id=owner_id, pet_id=pet.id, category='Medication', reference_id=m.id
            ).first()
            if not reminder:
                reminder = Reminder(
                    user_id=owner_id,
                    pet_id=pet.id,
                    title=title,
                    category='Medication',
                    due_date=m.end_date,
                    reference_id=m.id
                )
                db.session.add(reminder)
            else:
                reminder.due_date = m.end_date
                reminder.title = title

            days = (m.end_date - today).days
            reminder.status = _compute_status(days)
            processed_count += 1

            if days <= 7:
                msg = f"{pet.name}'s medication schedule for {m.medicine_name} ({m.dosage}, {m.frequency}) ends in {days} day(s)." if days > 0 else f"{pet.name}'s medication {m.medicine_name} is ending today/overdue!"
                create_notification(owner_id, pet.id, title, msg, 'Medication')
                notifications_created += 1

        # 4. Check Groomings
        groomings = Grooming.query.filter_by(pet_id=pet.id).all()
        for g in groomings:
            title = f"Grooming: {g.care_type}"
            reminder = Reminder.query.filter_by(
                user_id=owner_id, pet_id=pet.id, category='Grooming', reference_id=g.id
            ).first()
            if not reminder:
                reminder = Reminder(
                    user_id=owner_id,
                    pet_id=pet.id,
                    title=title,
                    category='Grooming',
                    due_date=g.next_due_date,
                    reference_id=g.id
                )
                db.session.add(reminder)
            else:
                reminder.due_date = g.next_due_date
                reminder.title = title

            days = (g.next_due_date - today).days
            reminder.status = _compute_status(days)
            processed_count += 1

            if days <= 7:
                msg = _build_message(pet.name, f"grooming session ({g.care_type})", days)
                create_notification(owner_id, pet.id, title, msg, 'Grooming')
                notifications_created += 1

        # 5. Check Vet Visits (Upcoming or Follow-ups)
        vet_visits = VetVisit.query.filter_by(pet_id=pet.id).all()
        for v in vet_visits:
            # Check visit date if upcoming
            target_date = v.visit_date if v.visit_date >= today else v.follow_up_date
            if target_date:
                title = f"Vet Visit: {v.reason}"
                reminder = Reminder.query.filter_by(
                    user_id=owner_id, pet_id=pet.id, category='Vet Visit', reference_id=v.id
                ).first()
                if not reminder:
                    reminder = Reminder(
                        user_id=owner_id,
                        pet_id=pet.id,
                        title=title,
                        category='Vet Visit',
                        due_date=target_date,
                        reference_id=v.id
                    )
                    db.session.add(reminder)
                else:
                    reminder.due_date = target_date
                    reminder.title = title

                days = (target_date - today).days
                reminder.status = _compute_status(days)
                processed_count += 1

                if days <= 7:
                    msg = _build_message(pet.name, f"veterinary appointment ({v.reason})", days)
                    create_notification(owner_id, pet.id, title, msg, 'Vet Visit')
                    notifications_created += 1

    db.session.commit()
    return {
        'processed_records': processed_count,
        'notifications_created': notifications_created,
        'timestamp': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    }

def _compute_status(days):
    if days < 0:
        return 'Overdue'
    elif days == 0:
        return 'Due Today'
    elif days == 1:
        return 'Due Tomorrow'
    elif days <= 7:
        return 'Due Soon'
    return 'Upcoming'

def _build_message(pet_name, task_desc, days):
    if days < 0:
        return f"{pet_name}'s {task_desc} is OVERDUE by {abs(days)} day(s)!"
    elif days == 0:
        return f"{pet_name}'s {task_desc} is DUE TODAY!"
    elif days == 1:
        return f"{pet_name}'s {task_desc} is due TOMORROW."
    else:
        return f"{pet_name}'s {task_desc} is due in {days} days."
