import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import db, create_app
from app.models import User, Role
from sqlalchemy.exc import SQLAlchemyError

def populate_roles():
    """
    Populate roles and assign them to users.
    This function handles potential database issues and ensures roles are correctly assigned.
    """
    try:
        # Define roles
        roles = ['Admin', 'Manager', 'Project Manager', 'Consultant']
        
        # Check for existing roles before adding
        for role_name in roles:
            if not Role.query.filter_by(name=role_name).first():
                role = Role(name=role_name)
                db.session.add(role)
        db.session.commit()
        print("Roles created successfully.")
        
        # Assign admin role to user with username 'admin'
        admin_role = Role.query.filter_by(name='Admin').first()
        admin_user = User.query.filter_by(username='admin').first()
        
        if admin_role and admin_user:
            # Check if admin already has the role
            if admin_role not in admin_user.roles:
                admin_user.roles.append(admin_role)
                print(f"Admin role assigned to user '{admin_user.username}'")
        
        # Assign consultant role to all users
        consultant_role = Role.query.filter_by(name='Consultant').first()
        if consultant_role:
            for user in User.query.all():
                # Skip if user already has the role
                if consultant_role not in user.roles:
                    user.roles.append(consultant_role)
            print("Consultant role assigned to all users")
        
        db.session.commit()
        print("Roles populated and associated with users successfully.")
    except SQLAlchemyError as e:
        db.session.rollback()
        print(f"Error in populate_roles: {str(e)}")
        # If there's an issue with the many-to-many relationship, try direct SQL
        try:
            # Create roles table if it doesn't exist
            db.session.execute("""
                CREATE TABLE IF NOT EXISTS roles (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(20) NOT NULL UNIQUE,
                    description VARCHAR(100)
                )
            """)
            
            # Create user_roles table if it doesn't exist
            db.session.execute("""
                CREATE TABLE IF NOT EXISTS user_roles (
                    user_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    PRIMARY KEY (user_id, role_id),
                    FOREIGN KEY (user_id) REFERENCES users (id),
                    FOREIGN KEY (role_id) REFERENCES roles (id)
                )
            """)
            
            # Insert roles if they don't exist
            for role_name in roles:
                db.session.execute("""
                    INSERT OR IGNORE INTO roles (name) VALUES (:name)
                """, {"name": role_name})
            
            # Get admin role ID
            admin_role_id = db.session.execute("""
                SELECT id FROM roles WHERE name = 'Admin'
            """).scalar()
            
            # Get admin user ID
            admin_user_id = db.session.execute("""
                SELECT id FROM users WHERE username = 'admin'
            """).scalar()
            
            # Assign admin role to admin user
            if admin_role_id and admin_user_id:
                db.session.execute("""
                    INSERT OR IGNORE INTO user_roles (user_id, role_id) 
                    VALUES (:user_id, :role_id)
                """, {"user_id": admin_user_id, "role_id": admin_role_id})
            
            # Get consultant role ID
            consultant_role_id = db.session.execute("""
                SELECT id FROM roles WHERE name = 'Consultant'
            """).scalar()
            
            # Assign consultant role to all users
            if consultant_role_id:
                user_ids = db.session.execute("""
                    SELECT id FROM users
                """).scalars()
                
                for user_id in user_ids:
                    db.session.execute("""
                        INSERT OR IGNORE INTO user_roles (user_id, role_id) 
                        VALUES (:user_id, :role_id)
                    """, {"user_id": user_id, "role_id": consultant_role_id})
            
            db.session.commit()
            print("Roles populated using direct SQL successfully.")
        except Exception as e2:
            db.session.rollback()
            print(f"Error in direct SQL approach: {str(e2)}")

if __name__ == "__main__":
    app = create_app()
    
    # Ensure the instance directory exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    with app.app_context():
        populate_roles() 