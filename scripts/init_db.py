import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, create_app
from app.models import User, Role, Consultant, ExpertiseCategory, ConsultantExpertise
from werkzeug.security import generate_password_hash
from datetime import datetime, date
from sqlalchemy.exc import SQLAlchemyError

def init_db():
    """
    Initialize the database with sample data.
    """
    try:
        # Create roles
        roles = ['Admin', 'Manager', 'Project Manager', 'Consultant']
        role_objects = {}
        
        for role_name in roles:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                role = Role(name=role_name)
                db.session.add(role)
                print(f"Created role: {role_name}")
            role_objects[role_name] = role
        
        db.session.commit()
        
        # Create admin user if it doesn't exist
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=generate_password_hash('admin'),
                first_name='Admin',
                last_name='User',
                is_active=True
            )
            db.session.add(admin_user)
            print("Created admin user")
        
        # Assign Admin role to admin user
        if role_objects['Admin'] not in admin_user.roles:
            admin_user.roles.append(role_objects['Admin'])
            print("Assigned Admin role to admin user")
        
        # Create consultant user if it doesn't exist
        consultant_user = User.query.filter_by(username='consultant').first()
        if not consultant_user:
            consultant_user = User(
                username='consultant',
                email='consultant@example.com',
                password_hash=generate_password_hash('consultant'),
                first_name='John',
                last_name='Doe',
                is_active=True
            )
            db.session.add(consultant_user)
            print("Created consultant user")
        
        # Assign Consultant role to consultant user
        if role_objects['Consultant'] not in consultant_user.roles:
            consultant_user.roles.append(role_objects['Consultant'])
            print("Assigned Consultant role to consultant user")
        
        db.session.commit()
        
        # Create expertise categories if they don't exist
        categories = ['Java', 'Python', 'JavaScript', 'DevOps', 'Database', 'Cloud']
        category_objects = {}
        
        for category_name in categories:
            category = ExpertiseCategory.query.filter_by(name=category_name).first()
            if not category:
                category = ExpertiseCategory(name=category_name)
                db.session.add(category)
                print(f"Created expertise category: {category_name}")
            category_objects[category_name] = category
        
        db.session.commit()
        
        # Create consultant if it doesn't exist
        consultant = Consultant.query.filter_by(user_id=consultant_user.id).first()
        if not consultant:
            consultant = Consultant(
                user_id=consultant_user.id,
                name='John',
                surname='Doe',
                full_name='John Doe',
                email='john.doe@example.com',
                phone_number='123-456-7890',
                availability_days_per_month=20,
                status='Active',
                start_date=date(2023, 1, 1),
                notes='Sample consultant'
            )
            db.session.add(consultant)
            print("Created consultant")
        
        db.session.commit()
        
        # Create consultant expertise if it doesn't exist
        for category_name, rating in [('Java', 5), ('Python', 4), ('JavaScript', 3)]:
            expertise = ConsultantExpertise.query.filter_by(
                consultant_id=consultant.id,
                category_id=category_objects[category_name].id
            ).first()
            
            if not expertise:
                expertise = ConsultantExpertise(
                    consultant_id=consultant.id,
                    category_id=category_objects[category_name].id,
                    rating=rating,
                    notes=f'Expertise in {category_name}'
                )
                db.session.add(expertise)
                print(f"Created expertise: {category_name} (rating: {rating})")
        
        db.session.commit()
        
        print("Database initialized successfully with sample data.")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error initializing database: {str(e)}")

if __name__ == "__main__":
    app = create_app()
    
    with app.app_context():
        init_db() 