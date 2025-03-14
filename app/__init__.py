from flask import Flask, redirect, url_for, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
import os
import logging
from datetime import datetime
from markupsafe import Markup
import traceback

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
    
    # Configure logging
    if not app.debug:
        # Set up logging to stdout for Render
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        app.logger.addHandler(stream_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Iteratio2 startup')
    
    # Load configuration
    if config_class:
        app.config.from_object(config_class)
        app.logger.info(f'Using configuration class: {config_class.__class__.__name__}')
    else:
        # Default configuration
        app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-for-development-only')
        
        # Use Flask's instance_path to correctly reference the instance directory
        db_path = os.path.join(app.instance_path, 'app.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f'sqlite:///{db_path}')
        
        # Ensure the instance directory exists
        os.makedirs(app.instance_path, exist_ok=True)
        
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.logger.info('Using default configuration')
    
    # Log configuration status
    has_secret_key = bool(app.config.get('SECRET_KEY'))
    app.logger.info(f'SECRET_KEY is {"set" if has_secret_key else "NOT SET"}')
    app.logger.info(f'SQLALCHEMY_DATABASE_URI is {"set" if app.config.get("SQLALCHEMY_DATABASE_URI") else "NOT SET"}')
    
    # Ensure SECRET_KEY is set
    if not has_secret_key:
        app.logger.error('SECRET_KEY is not set! Setting a default for now, but this is not secure for production.')
        app.config['SECRET_KEY'] = 'emergency-fallback-key-not-secure-for-production'
    
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
        try:
            return User.query.get(int(user_id))
        except Exception as e:
            app.logger.error(f"Error loading user: {str(e)}")
            return None
    
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
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        app.logger.error(f"404 error: {error}")
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f"500 error: {error}")
        app.logger.error(traceback.format_exc())
        return render_template('errors/500.html'), 500
    
    return app
