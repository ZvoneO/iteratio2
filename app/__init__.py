from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
import os
from datetime import datetime

from .models import db

def create_app(config_class=None):
    """
    Create and configure the Flask application.
    
    Args:
        config_class: Configuration class to use
        
    Returns:
        Configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    if config_class:
        app.config.from_object(config_class)
    else:
        # Default configuration
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-development-only')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    from .models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login."""
        return User.query.get(int(user_id))
    
    # Add context processor to provide current date to all templates
    @app.context_processor
    def inject_now():
        """Add current date to all templates."""
        return {'now': datetime.utcnow()}
    
    # Register blueprints
    from .routes.admin import admin_bp
    from .routes.projects import projects_bp
    from .routes.clients import clients_bp
    from .routes.catalog import catalog_bp
    from .routes.consultants import consultants_bp
    
    app.register_blueprint(admin_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(catalog_bp)
    app.register_blueprint(consultants_bp)
    
    # Create auth blueprint for login/logout
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Create a simple index route
    @app.route('/')
    def index():
        # If user is logged in, redirect to dashboard
        if current_user.is_authenticated:
            return redirect(url_for('admin.dashboard'))
        # Otherwise redirect to login page
        return redirect(url_for('auth.login'))
    
    return app
