"""
Script to create an admin user in the database.
Run this script to create an initial admin user for the application.
"""

from app import create_app
from app.models import db, User
from werkzeug.security import generate_password_hash

def create_admin_user():
    """Create an admin user in the database."""
    app = create_app()
    
    with app.app_context():
        # Check if admin user already exists
        admin = User.query.filter_by(email='admin@example.com').first()
        
        if admin:
            print("Admin user already exists.")
            return
        
        # Create new admin user
        admin = User(
            username='admin',
            email='admin@example.com',
            password_hash=generate_password_hash('admin123'),
            first_name='Admin',
            last_name='User',
            role='Admin',
            is_active=True
        )
        
        # Add to database
        db.session.add(admin)
        db.session.commit()
        
        print("Admin user created successfully.")
        print("Username: admin")
        print("Password: admin123")

if __name__ == '__main__':
    create_admin_user() 