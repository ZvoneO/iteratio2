from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import db, Consultant, User, ExpertiseCategory, ConsultantExpertise, Role
from functools import wraps
import json
import os

consultants_bp = Blueprint('consultants', __name__, url_prefix='/consultants')

# Helper function to check if user has a specific role
def user_has_role(user, role_name):
    """Check if a user has a specific role."""
    role = Role.query.filter_by(name=role_name).first()
    return role in user.roles

# Custom decorator for manager-only routes
def manager_required(f):
    """
    Decorator for routes that require manager privileges.
    Redirects to consultants list if user is not a manager or admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (user_has_role(current_user, 'Admin') or user_has_role(current_user, 'Manager')):
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('consultants.list_consultants'))
        return f(*args, **kwargs)
    return decorated_function

# Helper function to load settings
def load_settings():
    """Load settings from JSON file"""
    settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'settings.json')
    try:
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error loading settings: {e}")
        return {}

@consultants_bp.route('/')
@login_required
def list_consultants():
    """
    Display a list of all consultants.
    """
    # Get search parameters
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    expertise_filter = request.args.get('expertise', '')
    
    # Base query
    query = Consultant.query
    
    # Apply filters
    if search:
        query = query.filter(Consultant.full_name.ilike(f'%{search}%'))
    
    if status_filter:
        query = query.filter(Consultant.status == status_filter)
    
    if expertise_filter:
        query = query.join(ConsultantExpertise).filter(ConsultantExpertise.category_id == expertise_filter)
    
    # Get consultants
    consultants = query.all()
    
    # Get expertise categories for filter dropdown
    categories = ExpertiseCategory.query.all()
    
    # Get consultant statuses from settings for filter dropdown
    settings = load_settings()
    statuses = settings.get('consultant_statuses', [])
    
    return render_template('consultants/list.html', 
                          consultants=consultants,
                          categories=categories,
                          statuses=statuses)

@consultants_bp.route('/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_consultant():
    """
    Handle consultant creation.
    
    GET: Display consultant creation form
    POST: Process consultant creation form submission
    """
    # Get users for dropdown
    users = User.query.filter_by(role='Consultant').all()
    
    # Get expertise categories
    categories = ExpertiseCategory.query.all()
    
    # Get consultant statuses from settings
    settings = load_settings()
    statuses = settings.get('consultant_statuses', [])
    
    if request.method == 'POST':
        # Get form data
        user_id = request.form.get('user_id')
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        availability_days = request.form.get('availability_days')
        status = request.form.get('status')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        notes = request.form.get('notes')
        calendar_name = request.form.get('calendar_name')
        
        # Validate form data
        if not user_id or not name or not surname:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('consultants.create_consultant'))
        
        # Create full name
        full_name = f"{name} {surname}"
        
        # Create new consultant
        new_consultant = Consultant(
            user_id=user_id,
            name=name,
            surname=surname,
            full_name=full_name,
            email=email,
            phone_number=phone_number,
            availability_days_per_month=availability_days,
            status=status,
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None,
            notes=notes,
            calendar_name=calendar_name
        )
        
        # Add consultant to database
        db.session.add(new_consultant)
        db.session.commit()
        
        # Process expertise
        for category in categories:
            rating = request.form.get(f'expertise_{category.id}')
            if rating:
                expertise = ConsultantExpertise(
                    consultant_id=new_consultant.id,
                    category_id=category.id,
                    rating=int(rating),
                    notes=request.form.get(f'expertise_notes_{category.id}')
                )
                db.session.add(expertise)
        
        db.session.commit()
        
        flash('Consultant created successfully.', 'success')
        return redirect(url_for('consultants.list_consultants'))
    
    return render_template('consultants/create.html', 
                          users=users, 
                          categories=categories,
                          statuses=statuses)

@consultants_bp.route('/view/<int:consultant_id>')
@login_required
def view_consultant(consultant_id):
    """
    Display consultant details.
    """
    # Get consultant
    consultant = Consultant.query.get_or_404(consultant_id)
    
    return render_template('consultants/view.html', consultant=consultant)

@consultants_bp.route('/edit/<int:consultant_id>', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_consultant(consultant_id):
    """
    Handle consultant editing.
    
    GET: Display consultant edit form
    POST: Process consultant edit form submission
    """
    # Get consultant
    consultant = Consultant.query.get_or_404(consultant_id)
    
    # Get users for dropdown
    users = User.query.filter_by(role='Consultant').all()
    
    # Get expertise categories
    categories = ExpertiseCategory.query.all()
    
    # Get consultant statuses from settings
    settings = load_settings()
    statuses = settings.get('consultant_statuses', [])
    
    if request.method == 'POST':
        # Get form data
        user_id = request.form.get('user_id')
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        phone_number = request.form.get('phone_number')
        availability_days = request.form.get('availability_days')
        status = request.form.get('status')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        notes = request.form.get('notes')
        calendar_name = request.form.get('calendar_name')
        
        # Validate form data
        if not user_id or not name or not surname:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('consultants.edit_consultant', consultant_id=consultant_id))
        
        # Update consultant
        consultant.user_id = user_id
        consultant.name = name
        consultant.surname = surname
        consultant.full_name = f"{name} {surname}"
        consultant.email = email
        consultant.phone_number = phone_number
        consultant.availability_days_per_month = availability_days
        consultant.status = status
        consultant.start_date = start_date if start_date else None
        consultant.end_date = end_date if end_date else None
        consultant.notes = notes
        consultant.calendar_name = calendar_name
        
        # Update expertise
        # First, remove all existing expertise
        ConsultantExpertise.query.filter_by(consultant_id=consultant.id).delete()
        
        # Then add new expertise
        for category in categories:
            rating = request.form.get(f'expertise_{category.id}')
            if rating:
                expertise = ConsultantExpertise(
                    consultant_id=consultant.id,
                    category_id=category.id,
                    rating=int(rating),
                    notes=request.form.get(f'expertise_notes_{category.id}')
                )
                db.session.add(expertise)
        
        db.session.commit()
        
        flash('Consultant updated successfully.', 'success')
        return redirect(url_for('consultants.view_consultant', consultant_id=consultant.id))
    
    return render_template('consultants/edit.html', 
                          consultant=consultant, 
                          users=users, 
                          categories=categories,
                          statuses=statuses)

@consultants_bp.route('/delete/<int:consultant_id>', methods=['POST'])
@login_required
@manager_required
def delete_consultant(consultant_id):
    """
    Handle consultant deletion.
    """
    # Get consultant
    consultant = Consultant.query.get_or_404(consultant_id)
    
    # Delete consultant
    db.session.delete(consultant)
    db.session.commit()
    
    flash('Consultant deleted successfully.', 'success')
    return redirect(url_for('consultants.list_consultants')) 