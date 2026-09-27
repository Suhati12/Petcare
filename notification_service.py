from datetime import datetime, date
from models import db
from models.notification import Notification

def create_notification(user_id, pet_id, title, message, n_type='General'):
    """
    Creates an in-app notification record if a duplicate has not been sent today.
    """
    today_start = datetime.combine(date.today(), datetime.min.time())
    
    # Check for duplicate today
    existing = Notification.query.filter(
        Notification.user_id == user_id,
        Notification.pet_id == pet_id,
        Notification.title == title,
        Notification.created_at >= today_start
    ).first()

    if not existing:
        notif = Notification(
            user_id=user_id,
            pet_id=pet_id,
            title=title,
            message=message,
            type=n_type,
            is_read=False,
            created_at=datetime.utcnow()
        )
        db.session.add(notif)
        db.session.commit()
        return notif
    return existing
