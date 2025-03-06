from app import db, create_app
from app.models import User, Role

def populate_roles():
    # Define roles
    roles = ['Admin', 'Manager', 'Project Manager', 'Consultant']
    
    # Check for existing roles before adding
    for role_name in roles:
        if not Role.query.filter_by(name=role_name).first():
            role = Role(name=role_name)
            db.session.add(role)
    db.session.commit()
    
    # Directly associate roles based on predefined logic
    # Example: Assign all users to 'Consultant' role for demonstration
    consultant_role = Role.query.filter_by(name='Consultant').first()
    for user in User.query.all():
        if consultant_role:
            user.roles.append(consultant_role)
    db.session.commit()

if __name__ == "__main__":
    app = create_app()

    with app.app_context():
        populate_roles()
        print("Roles populated and associated with users successfully.") 