
import os
from flask import Flask, render_template
from flask_login import LoginManager, current_user
from config import Config
from models import db
from models.user import User
from models.notification import Notification

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload directories exist
    os.makedirs(app.config['PET_UPLOADS'], exist_ok=True)
    os.makedirs(app.config['DOC_UPLOADS'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.pets import pets_bp
    from routes.vaccinations import vaccinations_bp
    from routes.dewormings import dewormings_bp
    from routes.medications import medications_bp
    from routes.groomings import groomings_bp
    from routes.vet_visits import vet_visits_bp
    from routes.reminders import reminders_bp
    from routes.notifications import notifications_bp
    from routes.timeline import timeline_bp
    from routes.reports import reports_bp
    from routes.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(pets_bp)
    app.register_blueprint(vaccinations_bp)
    app.register_blueprint(dewormings_bp)
    app.register_blueprint(medications_bp)
    app.register_blueprint(groomings_bp)
    app.register_blueprint(vet_visits_bp)
    app.register_blueprint(reminders_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(timeline_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(api_bp)

    # Global Context Processors (e.g. Unread notifications counter)
    @app.context_processor
    def inject_global_vars():
        unread_count = 0
        if current_user.is_authenticated:
            unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return dict(unread_notifications_count=unread_count)

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500

    # Start APScheduler for Background Reminders
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from services.reminder_engine import run_reminder_scan

            scheduler = BackgroundScheduler(daemon=True)
            def scheduled_task():
                with app.app_context():
                    run_reminder_scan()

            scheduler.add_job(scheduled_task, 'interval', hours=6, id='reminder_scanner')
            scheduler.start()
        except Exception as e:
            app.logger.warning(f"Could not start APScheduler: {e}")

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='127.0.0.1', port=5000)
