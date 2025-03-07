from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import db, Consultant, User, ExpertiseCategory, ConsultantExpertise, Role, user_roles, List, ListItem
from functools import wraps
import json
import os
from ..utils import user_has_role as utils_user_has_role, get_user_roles
from datetime import datetime, date

consultants_bp = Blueprint('consultants', __name__, url_prefix='/consultants')

# Helper function to check if user has a specific role
def user_has_role(user, role_name):
    """Check if a user has a specific role."""
    return utils_user_has_role(user, role_name)

# Custom decorator for manager-only routes
def manager_required(f):
    """
    Decorator for routes that require manager privileges.
    Redirects to consultants list if user is not a manager or admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (user_has_role(current_user, 'Admin') or user_has_role(current_user, 'Manager') or current_user.username == 'admin'):
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

def ensure_consultant_entries():
    """
    Ensure that every user with the Consultant role has a corresponding entry in the consultants table.
    This helps maintain consistency between the role assignments and the consultant records.
    """
    # Get the Consultant role
    consultant_role = Role.query.filter_by(name='Consultant').first()
    if not consultant_role:
        return
    
    # Get all users with the Consultant role
    consultant_users = db.session.query(User).join(user_roles).filter(user_roles.c.role_id == consultant_role.id).all()
    
    # For each user with the Consultant role, check if they have a consultant entry
    for user in consultant_users:
        # Check if the user already has a consultant entry
        existing_consultant = Consultant.query.filter_by(user_id=user.id).first()
        if not existing_consultant:
            # Create a new consultant entry for the user
            new_consultant = Consultant(
                user_id=user.id,
                status='Active',
                availability_days_per_month=0
            )
            db.session.add(new_consultant)
    
    # Commit the changes
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error ensuring consultant entries: {e}")

def ensure_consultant_status_list():
    """
    Ensure that the 'Consultant Status' list exists in the database.
    This helps maintain consistency in the application.
    """
    # Check if the list already exists
    status_list = List.query.filter_by(name='Consultant Status').first()
    if not status_list:
        try:
            # Create the list
            status_list = List(name='Consultant Status', description='Status options for consultants')
            db.session.add(status_list)
            db.session.flush()  # This assigns the ID without committing the transaction
            
            # Add default status options
            statuses = ['Active', 'Inactive', 'On Leave']
            for i, status in enumerate(statuses):
                item = ListItem(value=status, display_order=i+1, list_id=status_list.id)
                db.session.add(item)
            
            # Commit all changes
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error creating Consultant Status list: {e}")
            # Provide fallback behavior
            return None
    
    return status_list

@consultants_bp.route('/')
@login_required
def list_consultants():
    """
    Display a list of all consultants.
    """
    # Ensure consultant entries for users with Consultant role
    ensure_consultant_entries()
    
    # Ensure the Consultant Status list exists
    status_list = ensure_consultant_status_list()
    
    # Get search parameters
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    expertise_filter = request.args.get('expertise', '')
    
    # Base query
    query = Consultant.query.join(User)
    
    # Apply filters
    if search:
        query = query.filter(
            db.or_(
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%')
            )
        )
    
    if status_filter:
        query = query.filter(Consultant.status == status_filter)
    
    if expertise_filter:
        # Filter by expertise category
        query = query.join(ConsultantExpertise).filter(
            ConsultantExpertise.category_id == expertise_filter
        )
    
    # Get all consultants
    consultants = query.all()
    
    # Get all expertise categories for filter dropdown
    categories = ExpertiseCategory.query.all()
    
    # Get all statuses for filter dropdown
    if status_list:
        statuses = status_list.items
    else:
        # Fallback to default statuses if the list doesn't exist
        statuses = [
            {'value': 'Active'},
            {'value': 'Inactive'},
            {'value': 'On Leave'}
        ]
    
    # Get user roles for permission checks
    user_roles = [role.name for role in current_user.roles]
    
    return render_template('consultants/list.html', 
                          consultants=consultants, 
                          categories=categories,
                          statuses=statuses,
                          user_roles=user_roles)

@consultants_bp.route('/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_consultant():
    """
    Handle consultant creation.
    
    GET: Display consultant creation form
    POST: Process consultant creation form submission
    """
    # Get users for dropdown - exclude users who are already consultants
    users = User.query.outerjoin(Consultant).filter(Consultant.id == None).all()
    
    # Get expertise categories
    categories = ExpertiseCategory.query.all()
    
    # Get consultant statuses from settings
    status_list = ensure_consultant_status_list()
    if status_list:
        statuses = status_list.items
    else:
        # Fallback to default statuses if the list doesn't exist
        statuses = [
            {'value': 'Active'},
            {'value': 'Inactive'},
            {'value': 'On Leave'}
        ]
    
    if request.method == 'POST':
        # Get form data
        user_id = request.form.get('user_id')
        availability_days = request.form.get('availability_days')
        status = request.form.get('status')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        notes = request.form.get('notes')
        calendar_name = request.form.get('calendar_name')
        
        # Validate form data
        if not user_id:
            flash('User selection is required.', 'danger')
            return redirect(url_for('consultants.create_consultant'))
        
        # Convert date strings to Python date objects
        start_date = None
        if start_date_str and start_date_str.strip():
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid start date format. Please use YYYY-MM-DD.', 'danger')
                return redirect(url_for('consultants.create_consultant'))
        
        end_date = None
        if end_date_str and end_date_str.strip():
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid end date format. Please use YYYY-MM-DD.', 'danger')
                return redirect(url_for('consultants.create_consultant'))
        
        # Create new consultant
        new_consultant = Consultant(
            user_id=user_id,
            availability_days_per_month=int(availability_days) if availability_days else 0,
            status=status,
            start_date=start_date,
            end_date=end_date,
            notes=notes if notes and notes.lower() != 'none' else None,
            calendar_name=calendar_name if calendar_name and calendar_name.lower() != 'none' else None
        )
        
        # Add consultant to database
        db.session.add(new_consultant)
        
        # Ensure the user has the Consultant role
        user = User.query.get(user_id)
        consultant_role = Role.query.filter_by(name='Consultant').first()
        if user and consultant_role and consultant_role not in user.roles:
            user.roles.append(consultant_role)
        
        try:
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
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating consultant: {str(e)}', 'danger')
            return redirect(url_for('consultants.create_consultant'))
    
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
    
    # Get users for dropdown - include current consultant's user and users who are not consultants
    users = User.query.outerjoin(Consultant).filter(
        db.or_(
            Consultant.id == None,
            User.id == consultant.user_id
        )
    ).all()
    
    # Get expertise categories
    categories = ExpertiseCategory.query.all()
    
    # Get consultant statuses from settings
    status_list = ensure_consultant_status_list()
    if status_list:
        statuses = status_list.items
    else:
        # Fallback to default statuses if the list doesn't exist
        statuses = [
            {'value': 'Active'},
            {'value': 'Inactive'},
            {'value': 'On Leave'}
        ]
    
    if request.method == 'POST':
        # Get form data
        user_id = request.form.get('user_id')
        availability_days = request.form.get('availability_days')
        status = request.form.get('status')
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        notes = request.form.get('notes')
        calendar_name = request.form.get('calendar_name')
        
        # Validate form data
        if not user_id:
            flash('User selection is required.', 'danger')
            return redirect(url_for('consultants.edit_consultant', consultant_id=consultant_id))
        
        # Convert date strings to Python date objects
        start_date = None
        if start_date_str and start_date_str.strip():
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid start date format. Please use YYYY-MM-DD.', 'danger')
                return redirect(url_for('consultants.edit_consultant', consultant_id=consultant_id))
        
        end_date = None
        if end_date_str and end_date_str.strip():
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid end date format. Please use YYYY-MM-DD.', 'danger')
                return redirect(url_for('consultants.edit_consultant', consultant_id=consultant_id))
        
        # Update consultant
        consultant.user_id = user_id
        consultant.availability_days_per_month = int(availability_days) if availability_days else 0
        consultant.status = status
        consultant.start_date = start_date
        consultant.end_date = end_date
        consultant.notes = notes if notes and notes.lower() != 'none' else None
        consultant.calendar_name = calendar_name if calendar_name and calendar_name.lower() != 'none' else None
        
        # Ensure the user has the Consultant role
        user = User.query.get(user_id)
        consultant_role = Role.query.filter_by(name='Consultant').first()
        if user and consultant_role and consultant_role not in user.roles:
            user.roles.append(consultant_role)
        
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
        
        try:
            db.session.commit()
            flash('Consultant updated successfully.', 'success')
            return redirect(url_for('consultants.view_consultant', consultant_id=consultant.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating consultant: {str(e)}', 'danger')
            return redirect(url_for('consultants.edit_consultant', consultant_id=consultant_id))
    
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
    
    # Store user_id before deleting consultant
    user_id = consultant.user_id
    
    # Delete consultant
    db.session.delete(consultant)
    
    # Check if the user should keep the Consultant role
    # If they have other consultant entries, keep the role
    user = User.query.get(user_id)
    consultant_role = Role.query.filter_by(name='Consultant').first()
    
    if user and consultant_role:
        # Check if the user has other consultant entries
        other_consultants = Consultant.query.filter_by(user_id=user_id).count()
        
        # If this was the only consultant entry for this user, remove the Consultant role
        if other_consultants == 0 and consultant_role in user.roles:
            user.roles.remove(consultant_role)
    
    db.session.commit()
    
    flash('Consultant deleted successfully.', 'success')
    return redirect(url_for('consultants.list_consultants')) 