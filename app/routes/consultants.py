from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from ..models import db, Consultant, User, ExpertiseCategory, ConsultantExpertise, Role, user_roles, List, ListItem, ProductGroup, ProductElement
from functools import wraps
import json
import os
from ..utils import user_has_role as utils_user_has_role, get_user_roles
from datetime import datetime, date
from contextlib import contextmanager

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
    
    # Get all consultants
    consultants = query.all()
    
    # Get all product groups for expertise selection
    product_groups = ProductGroup.query.all()
    
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
                          statuses=statuses,
                          product_groups=product_groups,
                          user_roles=user_roles)

@consultants_bp.route('/consultant/<int:consultant_id>', methods=['GET', 'POST'])
@consultants_bp.route('/consultant/new', methods=['GET', 'POST'])
@login_required
@manager_required
def manage_consultant(consultant_id=None):
    """
    Handle consultant creation and editing.
    If consultant_id is provided, edit existing consultant.
    If consultant_id is None, create new consultant.
    """
    # Get consultant if editing, otherwise None
    consultant = Consultant.query.get_or_404(consultant_id) if consultant_id else None
    
    # Get users for dropdown - include current consultant's user if editing
    if consultant:
        users = User.query.outerjoin(Consultant).filter(
            db.or_(Consultant.id == None, User.id == consultant.user_id)
        ).all()
    else:
        # For new consultants, only show users without consultant entries
        users = User.query.outerjoin(Consultant).filter(Consultant.id == None).all()
    
    # Get expertise categories
    categories = ExpertiseCategory.query.all()
    
    # Get consultant statuses
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
        try:
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
                return redirect(url_for('consultants.manage_consultant', consultant_id=consultant_id))
            
            # Convert date strings to Python date objects
            start_date = None
            if start_date_str and start_date_str.strip():
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid start date format. Please use YYYY-MM-DD.', 'danger')
                    return redirect(url_for('consultants.manage_consultant', consultant_id=consultant_id))
            
            end_date = None
            if end_date_str and end_date_str.strip():
                try:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid end date format. Please use YYYY-MM-DD.', 'danger')
                    return redirect(url_for('consultants.manage_consultant', consultant_id=consultant_id))
            
            # Process consultant data
            if consultant:
                # Update existing consultant
                consultant.user_id = user_id
                consultant.availability_days_per_month = int(availability_days) if availability_days else 0
                consultant.status = status
                consultant.start_date = start_date
                consultant.end_date = end_date
                consultant.notes = notes if notes and notes.lower() != 'none' else None
                consultant.calendar_name = calendar_name if calendar_name and calendar_name.lower() != 'none' else None
                
                # Remove existing expertise
                ConsultantExpertise.query.filter_by(consultant_id=consultant.id).delete()
            else:
                # Create new consultant
                consultant = Consultant(
                    user_id=user_id,
                    availability_days_per_month=int(availability_days) if availability_days else 0,
                    status=status,
                    start_date=start_date,
                    end_date=end_date,
                    notes=notes if notes and notes.lower() != 'none' else None,
                    calendar_name=calendar_name if calendar_name and calendar_name.lower() != 'none' else None
                )
                db.session.add(consultant)
                db.session.flush()  # Get ID without committing
            
            # Ensure the user has the Consultant role
            user = User.query.get(user_id)
            consultant_role = Role.query.filter_by(name='Consultant').first()
            if user and consultant_role and consultant_role not in user.roles:
                user.roles.append(consultant_role)
            
            # Process expertise
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
            
            flash(f'Consultant {"updated" if consultant_id else "created"} successfully.', 'success')
            return redirect(url_for('consultants.view_consultant', consultant_id=consultant.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error {"updating" if consultant_id else "creating"} consultant: {str(e)}', 'danger')
            return redirect(url_for('consultants.manage_consultant', consultant_id=consultant_id))
    
    return render_template('consultants/consultant_form.html', 
                          consultant=consultant, 
                          users=users, 
                          categories=categories,
                          statuses=statuses)

def safe_get_attr(obj, attr_name, default=None):
    """
    Safely get an attribute from an object, returning a default value if the attribute doesn't exist.
    This helps prevent crashes when database schema changes.
    
    Args:
        obj: The object to get the attribute from
        attr_name: The name of the attribute to get
        default: The default value to return if the attribute doesn't exist
        
    Returns:
        The attribute value or the default value
    """
    if obj is None:
        return default
    return getattr(obj, attr_name, default)

@consultants_bp.route('/view/<int:consultant_id>')
@login_required
def view_consultant(consultant_id):
    """
    Display consultant details.
    """
    try:
        # Get consultant
        consultant = Consultant.query.get_or_404(consultant_id)
        
        # Use safe attribute access
        user = safe_get_attr(consultant, 'user')
        first_name = safe_get_attr(user, 'first_name', 'Unknown')
        last_name = safe_get_attr(user, 'last_name', 'Unknown')
        email = safe_get_attr(user, 'email', 'No email')
        
        return render_template('consultants/view.html', 
                              consultant=consultant,
                              user_first_name=first_name,
                              user_last_name=last_name,
                              user_email=email)
    except Exception as e:
        app.logger.error(f"Error viewing consultant {consultant_id}: {str(e)}")
        flash(f"Error loading consultant details: {str(e)}", 'danger')
        return redirect(url_for('consultants.list_consultants'))

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

@contextmanager
def db_transaction():
    """
    Context manager for database transactions.
    Automatically commits on success and rolls back on exception.
    
    Usage:
        with db_transaction():
            # database operations
    """
    try:
        yield
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Database transaction error: {str(e)}")
        raise 

@consultants_bp.route('/expertise/update', methods=['POST'])
@login_required
@manager_required
def update_consultant_expertise():
    """
    Update consultant expertise via AJAX.
    """
    try:
        data = request.json
        consultant_id = data.get('consultant_id')
        expertise_type = data.get('expertise_type')  # 'product_group' or 'product_element'
        item_id = data.get('item_id')
        rating = data.get('rating', 0)  # Default to 0 (clear) if not provided
        notes = data.get('notes', '')
        
        if not all([consultant_id, expertise_type, item_id]):
            return jsonify({'success': False, 'message': 'Missing required parameters'}), 400
        
        # Get consultant
        consultant = Consultant.query.get_or_404(consultant_id)
        
        # Handle different expertise types
        if expertise_type == 'product_group' or expertise_type == 'product_element':
            # For product groups and elements, we'll store them in the custom_data JSON field
            if not consultant.custom_data:
                consultant.custom_data = {}
            
            if 'expertise' not in consultant.custom_data:
                consultant.custom_data['expertise'] = {}
            
            expertise_key = f"{expertise_type}_{item_id}"
            
            if int(rating) == 0:
                # Remove expertise if rating is 0
                if expertise_key in consultant.custom_data['expertise']:
                    del consultant.custom_data['expertise'][expertise_key]
            else:
                # Update or create expertise
                consultant.custom_data['expertise'][expertise_key] = {
                    'type': expertise_type,
                    'id': item_id,
                    'rating': int(rating),
                    'notes': notes
                }
        
        # Save changes
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@consultants_bp.route('/expertise/list/<int:consultant_id>', methods=['GET'])
@login_required
def list_consultant_expertise(consultant_id):
    """
    Get all expertise for a consultant in JSON format.
    """
    try:
        consultant = Consultant.query.get_or_404(consultant_id)
        expertise_list = []
        
        # Get product group and element expertise from custom_data
        if consultant.custom_data and 'expertise' in consultant.custom_data:
            for key, exp_data in consultant.custom_data['expertise'].items():
                if exp_data['type'] == 'product_group':
                    # Get product group name
                    group = ProductGroup.query.get(exp_data['id'])
                    if group:
                        expertise_list.append({
                            'type': 'product_group',
                            'id': exp_data['id'],
                            'name': group.name,
                            'rating': exp_data['rating'],
                            'notes': exp_data.get('notes', '')
                        })
                elif exp_data['type'] == 'product_element':
                    # Get product element name
                    element = ProductElement.query.get(exp_data['id'])
                    if element:
                        expertise_list.append({
                            'type': 'product_element',
                            'id': exp_data['id'],
                            'name': f"{element.label} ({element.group.name})",
                            'rating': exp_data['rating'],
                            'notes': exp_data.get('notes', '')
                        })
        
        return jsonify({
            'success': True,
            'expertise': expertise_list
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@consultants_bp.route('/update/<int:consultant_id>', methods=['POST'])
@login_required
@manager_required
def update_consultant_details(consultant_id):
    """
    Update consultant details via AJAX.
    """
    try:
        data = request.json
        status = data.get('status')
        availability_days = data.get('availability_days')
        calendar_name = data.get('calendar_name')
        notes = data.get('notes')
        
        # Get consultant
        consultant = Consultant.query.get_or_404(consultant_id)
        
        # Update consultant details
        if status:
            consultant.status = status
        
        if availability_days is not None:
            consultant.availability_days_per_month = int(availability_days)
        
        if calendar_name is not None:
            consultant.calendar_name = calendar_name if calendar_name.strip() else None
        
        if notes is not None:
            consultant.notes = notes if notes.strip() else None
        
        # Save changes
        db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500 