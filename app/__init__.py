from flask import Flask, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
import os
from datetime import datetime
from markupsafe import Markup

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
        
        # Use Flask's instance_path to correctly reference the instance directory
        db_path = os.path.join(app.instance_path, 'app.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
        
        # Ensure the instance directory exists
        os.makedirs(app.instance_path, exist_ok=True)
        
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
    
    # Register custom filters
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        if not text:
            return ""
        return Markup(text.replace('\n', '<br>'))
    
    # Register blueprints
    from .routes import auth_bp, admin_bp, clients_bp, projects_bp, consultants_bp, catalog_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(clients_bp)
    app.register_blueprint(projects_bp)
    app.register_blueprint(consultants_bp)
    app.register_blueprint(catalog_bp)
    
    # Add health check endpoint for Render
    @app.route('/health')
    def health_check():
        return jsonify({"status": "healthy"}), 200
    
    # Add a root route that redirects to the dashboard
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('auth.login'))
    
    return app
