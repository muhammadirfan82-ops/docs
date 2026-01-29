from flask import Flask
from flask_login import LoginManager
from app.config import Config
from app.models import db

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Silakan login untuk mengakses halaman ini.'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register blueprints
    from app.views.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from app.views.admin import admin_bp
    app.register_blueprint(admin_bp)
    
    from app.views.attendance import attendance_bp
    app.register_blueprint(attendance_bp)
    
    from app.views.reports import reports_bp
    app.register_blueprint(reports_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
        
        # Create default super admin if not exists
        from app.models.user import User
        if not User.query.filter_by(role='super_admin').first():
            super_admin = User(
                username='superadmin',
                email='superadmin@example.com',
                role='super_admin'
            )
            super_admin.set_password('password')
            db.session.add(super_admin)
            db.session.commit()
    
    return app