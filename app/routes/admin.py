from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from ..models import db, User, Role, Project, Client, Consultant, List, ListItem
from werkzeug.security import generate_password_hash
from functools import wraps
import json
import os
from ..utils import user_has_role, user_has_any_role, get_user_roles, setup_logger
import logging
import traceback

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Initialize logger
logger = setup_logger('admin', level=logging.DEBUG)

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
        logger.error(f"Error loading settings: {e}")
        return {}

# Helper function to save settings
def save_settings(settings):
    """Save settings to JSON file"""
    settings_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'settings.json')
    try:
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=4)
        logger.info("Settings saved successfully")
        return True
    except Exception as e:
        logger.error(f"Error saving settings: {e}")
        return False

# Custom decorator for admin-only routes
def admin_required(f):
    """
    Decorator to restrict access to admin users only.
    Uses the robust role-checking function from utils.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is admin using the utility function
        if not current_user.is_authenticated or not (user_has_role(current_user, 'Admin') or current_user.username == 'admin'):
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Display the admin dashboard with role-based content.
    Different user roles see different dashboard content.
    Uses the robust role-checking functions from utils.
    """
    # Initialize counts
    project_count = 0
    client_count = 0
    user_count = 0
    consultant_count = 0
    
    # Get user roles using the utility function
    user_roles = get_user_roles(current_user)
    
    # Check if user is admin or manager
    is_admin_or_manager = user_has_any_role(current_user, ['Admin', 'Manager']) or current_user.username == 'admin'
    is_project_manager = user_has_role(current_user, 'Project Manager')
    
    # Get counts based on user role
    if is_admin_or_manager:
        # Admins and Managers see all projects, clients, and users
        project_count = Project.query.count()
        client_count = Client.query.count()
        user_count = User.query.count()
        
        # Count users with Consultant role instead of entries in consultants table
        consultant_role = Role.query.filter_by(name='Consultant').first()
        if consultant_role:
            consultant_count = User.query.join(User.roles).filter(Role.id == consultant_role.id).count()
        else:
            consultant_count = 0
    elif is_project_manager:
        # Project Managers see their assigned projects
        project_count = Project.query.filter_by(manager_id=current_user.id).count()
        # Get clients with projects managed by this user
        client_ids = db.session.query(Project.client_id).filter_by(manager_id=current_user.id).distinct()
        client_count = Client.query.filter(Client.id.in_(client_ids)).count()
        user_count = 0
        
        # Count users with Consultant role instead of entries in consultants table
        consultant_role = Role.query.filter_by(name='Consultant').first()
        if consultant_role:
            consultant_count = User.query.join(User.roles).filter(Role.id == consultant_role.id).count()
        else:
            consultant_count = 0
    else:  # Consultant
        # Get consultant record for current user
        consultant = Consultant.query.filter_by(user_id=current_user.id).first()
        if consultant:
            # This would need to be updated when project assignments are implemented
            # For now, just show 0 counts
            project_count = 0
            client_count = 0
        user_count = 0
        consultant_count = 0
    
    return render_template('admin/dashboard.html', 
                          project_count=project_count,
                          client_count=client_count,
                          user_count=user_count,
                          consultant_count=consultant_count,
                          user_roles=user_roles)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """
    Display a list of all users.
    """
    # Get pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Number of items per page
    
    # Get filter parameters
    search = request.args.get('search', '')
    role_filter = request.args.get('role_filter', '')
    status_filter = request.args.get('status_filter', '')
    
    # Build query
    query = User.query
    
    # Apply filters if provided
    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%')) |
            (User.first_name.ilike(f'%{search}%')) |
            (User.last_name.ilike(f'%{search}%'))
        )
    
    if role_filter:
        # Filter by role using the many-to-many relationship
        query = query.join(User.roles).filter(Role.id == role_filter)
    
    if status_filter:
        is_active = status_filter == 'active'
        query = query.filter(User.is_active == is_active)
    
    # Get total count for pagination
    total_users = query.count()
    
    # Apply pagination
    users_list = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Get all roles for the filter dropdown
    roles = Role.query.all()
    
    # Calculate total pages
    total_pages = (total_users + per_page - 1) // per_page  # Ceiling division
    
    return render_template(
        'admin/users.html',
        users=users_list.items,
        page=page,
        total_pages=total_pages,
        total_users=total_users,
        has_prev=users_list.has_prev,
        has_next=users_list.has_next,
        roles=roles
    )

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_user(user_id=None):
    """
    Handle user creation and editing.
    If user_id is provided, edit existing user.
    If user_id is None, create new user.
    """
    user = User.query.get_or_404(user_id) if user_id else None
    
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    if request.method == 'POST':
        try:
            # Get form data - handle both form submissions and JSON data
            if is_ajax:
                data = request.json
                username = data.get('username')
                email = data.get('email')
                first_name = data.get('first_name')
                last_name = data.get('last_name')
                password = data.get('password')
                role_names = data.get('roles', [])
                is_active = data.get('is_active', True)
            else:
                username = request.form.get('username')
                email = request.form.get('email')
                first_name = request.form.get('first_name')
                last_name = request.form.get('last_name')
                password = request.form.get('password')
                role_names = request.form.getlist('roles[]')
                is_active = True if request.form.get('is_active') else False
            
            # Log the request data (excluding password)
            log_data = {
                'username': username,
                'email': email,
                'first_name': first_name,
                'last_name': last_name,
                'role_names': role_names,
                'is_active': is_active,
                'user_id': user_id,
                'is_ajax': is_ajax
            }
            logger.info(f"User update/create request: {log_data}")
            
            # Validate form data
            if not username or not email or not role_names:
                message = 'All required fields must be filled.'
                logger.warning(f"Validation error: {message}")
                if is_ajax:
                    return jsonify({'success': False, 'message': message})
                flash(message, 'danger')
                return redirect(url_for('admin.manage_user', user_id=user_id) if user_id else url_for('admin.manage_user'))
            
            # Check if username exists (excluding current user if editing)
            existing_user = User.query.filter_by(username=username).first()
            if existing_user and (not user or existing_user.id != user.id):
                message = 'Username already exists.'
                logger.warning(f"Validation error: {message} - {username}")
                if is_ajax:
                    return jsonify({'success': False, 'message': message})
                flash(message, 'danger')
                return redirect(url_for('admin.manage_user', user_id=user_id) if user_id else url_for('admin.manage_user'))
            
            # Check if email exists (excluding current user if editing)
            existing_user = User.query.filter_by(email=email).first()
            if existing_user and (not user or existing_user.id != user.id):
                message = 'Email already exists.'
                logger.warning(f"Validation error: {message} - {email}")
                if is_ajax:
                    return jsonify({'success': False, 'message': message})
                flash(message, 'danger')
                return redirect(url_for('admin.manage_user', user_id=user_id) if user_id else url_for('admin.manage_user'))
            
            if user:
                # Update existing user
                user.username = username
                user.email = email
                user.first_name = first_name
                user.last_name = last_name
                user.is_active = is_active
                
                # Update password if provided
                if password and password.strip():
                    user.password_hash = generate_password_hash(password)
                
                # Check if user is losing Consultant role
                consultant_role = Role.query.filter_by(name='Consultant').first()
                had_consultant_role = consultant_role in user.roles
                will_have_consultant_role = 'Consultant' in role_names
                
                # Update roles
                user.roles = []
                for role_name in role_names:
                    role = Role.query.filter_by(name=role_name).first()
                    if role:
                        user.roles.append(role)
                
                # If user lost Consultant role, remove their consultant entry
                if had_consultant_role and not will_have_consultant_role:
                    consultant = Consultant.query.filter_by(user_id=user.id).first()
                    if consultant:
                        db.session.delete(consultant)
                        
                logger.info(f"Updating existing user: {user.id} - {user.username}")
            else:
                # Create new user
                if not password:
                    message = 'Password is required for new users.'
                    logger.warning(f"Validation error: {message}")
                    if is_ajax:
                        return jsonify({'success': False, 'message': message})
                    flash(message, 'danger')
                    return redirect(url_for('admin.manage_user'))
                
                user = User(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password_hash=generate_password_hash(password),
                    is_active=True
                )
                
                # Add roles to the user
                for role_name in role_names:
                    role = Role.query.filter_by(name=role_name).first()
                    if role:
                        user.roles.append(role)
                
                db.session.add(user)
                logger.info(f"Creating new user: {username}")
            
            db.session.commit()
            
            message = f'User {"updated" if user_id else "created"} successfully.'
            logger.info(message)
            if is_ajax:
                return jsonify({'success': True, 'message': message, 'user_id': user.id})
            
            flash(message, 'success')
            return redirect(url_for('admin.users'))
            
        except Exception as e:
            db.session.rollback()
            error_details = traceback.format_exc()
            message = f'Error {"updating" if user_id else "creating"} user: {str(e)}'
            logger.error(f"{message}\n{error_details}")
            
            if is_ajax:
                return jsonify({'success': False, 'message': message, 'error_details': str(e)})
            
            flash(message, 'danger')
            return redirect(url_for('admin.manage_user', user_id=user_id) if user_id else url_for('admin.manage_user'))
    
    # GET request - render form
    roles = Role.query.all()
    return render_template('admin/user_form.html', user=user, roles=roles)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """
    Handle user deletion.
    """
    # Check if this is an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Log the delete request
    logger.info(f"Delete user request: user_id={user_id}, by={current_user.username}")
    
    # Prevent deleting self
    if user_id == current_user.id:
        message = 'You cannot delete your own account.'
        logger.warning(f"Delete user validation error: {message}")
        if is_ajax:
            return jsonify({'success': False, 'message': message})
        flash(message, 'danger')
        return redirect(url_for('admin.users'))
    
    try:
        user = User.query.get_or_404(user_id)
        username = user.username  # Store for logging
        db.session.delete(user)
        db.session.commit()
        
        message = f'User {username} deleted successfully.'
        logger.info(message)
        if is_ajax:
            return jsonify({'success': True, 'message': message})
        
        flash(message, 'success')
        return redirect(url_for('admin.users'))
    except Exception as e:
        db.session.rollback()
        error_details = traceback.format_exc()
        message = f'Error deleting user: {str(e)}'
        logger.error(f"{message}\n{error_details}")
        
        if is_ajax:
            return jsonify({'success': False, 'message': message, 'error_details': str(e)})
        
        flash(message, 'danger')
        return redirect(url_for('admin.users'))

@admin_bp.route('/import-data', methods=['GET', 'POST'])
@login_required
@admin_required
def import_data():
    """
    Import data from CSV files.
    
    GET: Display import form
    POST: Process import form submission
    """
    if request.method == 'POST':
        # TODO: Implement data import functionality
        flash('Data import functionality is not yet implemented.', 'info')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('admin/import_data.html')

@admin_bp.route('/settings')
@login_required
@admin_required
def settings():
    """
    Display and manage application settings.
    """
    # Load settings from JSON file
    settings_data = load_settings()
    
    # Get all lists from database
    lists = List.query.all()
    
    return render_template('admin/settings.html', 
                          settings=settings_data,
                          lists=lists)

@admin_bp.route('/settings/json/<setting_type>', methods=['GET', 'POST'])
@login_required
@admin_required
def settings_json(setting_type):
    """
    API endpoint for managing JSON settings.
    GET: Return settings for a specific type
    POST: Update settings for a specific type
    """
    # Load current settings
    settings = load_settings()
    
    # Handle GET request
    if request.method == 'GET':
        if setting_type in settings:
            return jsonify(settings[setting_type])
        else:
            return jsonify([])
    
    # Handle POST request
    if request.method == 'POST':
        try:
            # Get JSON data from request
            data = request.get_json()
            
            # Update settings
            settings[setting_type] = data
            
            # Save settings
            if save_settings(settings):
                return jsonify({"success": True})
            else:
                return jsonify({"success": False, "message": "Failed to save settings"}), 500
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/settings/json/export', methods=['GET'])
@login_required
@admin_required
def export_settings_json():
    """
    Export all settings as a JSON file.
    """
    # Load settings
    settings = load_settings()
    
    # Create response with JSON data
    response = jsonify(settings)
    response.headers['Content-Disposition'] = 'attachment; filename=settings.json'
    return response

@admin_bp.route('/lists/api/create', methods=['POST'])
@login_required
@admin_required
def api_create_list():
    """
    API endpoint for creating a new list.
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        name = data.get('name')
        description = data.get('description', '')
        
        # Validate data
        if not name:
            return jsonify({"success": False, "message": "List name is required"}), 400
        
        # Check if list already exists
        if List.query.filter_by(name=name).first():
            return jsonify({"success": False, "message": "A list with this name already exists"}), 400
        
        # Create new list
        new_list = List(name=name, description=description)
        db.session.add(new_list)
        db.session.commit()
        
        return jsonify({"success": True, "list_id": new_list.id})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/lists/api/<int:list_id>/items', methods=['GET', 'POST'])
@login_required
@admin_required
def api_list_items(list_id):
    """
    API endpoint for managing list items.
    GET: Return items for a specific list
    POST: Update items for a specific list
    """
    # Get list
    list_obj = List.query.get_or_404(list_id)
    
    # Handle GET request
    if request.method == 'GET':
        items = ListItem.query.filter_by(list_id=list_id).order_by(ListItem.order).all()
        items_data = [{"id": item.id, "value": item.value, "description": item.description, "order": item.order} for item in items]
        return jsonify({"success": True, "items": items_data})
    
    # Handle POST request
    if request.method == 'POST':
        try:
            # Get JSON data from request
            data = request.get_json()
            items = data.get('items', [])
            
            # Delete existing items
            ListItem.query.filter_by(list_id=list_id).delete()
            
            # Add new items
            for item in items:
                new_item = ListItem(
                    list_id=list_id,
                    value=item['value'],
                    description=item.get('description', ''),
                    order=item.get('order', 0)
                )
                db.session.add(new_item)
            
            db.session.commit()
            
            return jsonify({"success": True})
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/lists/api/<int:list_id>/delete', methods=['POST'])
@login_required
@admin_required
def api_delete_list(list_id):
    """
    API endpoint for deleting a list.
    """
    try:
        # Get list
        list_obj = List.query.get_or_404(list_id)
        
        # Delete list (cascade will delete items)
        db.session.delete(list_obj)
        db.session.commit()
        
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

# TODO: Add routes for reports and analytics
# TODO: Add routes for system settings
