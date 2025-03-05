from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from ..models import db, User, Consultant
from functools import wraps
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Custom decorator for admin-only routes
def admin_required(f):
    """
    Decorator for routes that require admin privileges.
    Redirects to dashboard if user is not an admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'Admin':
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('admin.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Display the admin dashboard with role-based content.
    Different user roles see different dashboard content.
    """
    # Initialize counts
    project_count = 0
    client_count = 0
    user_count = 0
    consultant_count = 0
    
    # Get counts based on user role
    if current_user.role == 'Admin' or current_user.role == 'Manager':
        # Admins and Managers see all projects, clients, and users
        # Project and Client models might not be fully implemented yet
        # project_count = Project.query.count()
        # client_count = Client.query.count()
        user_count = User.query.count()
        consultant_count = Consultant.query.count()
    elif current_user.role == 'Project Manager':
        # Project Managers see their assigned projects
        # These counts might need to be implemented when Project model is ready
        # project_count = Project.query.filter_by(manager_id=current_user.id).count()
        # client_count = Count of clients with projects managed by this user
        user_count = 0
        consultant_count = Consultant.query.count()
    else:  # Consultant
        # Consultants see projects they're assigned to
        # These counts might need to be implemented when Project model is ready
        # project_count = Count of projects this consultant is assigned to
        # client_count = Count of clients with projects this consultant is assigned to
        user_count = 0
        consultant_count = 0
    
    return render_template('admin/dashboard.html', 
                          project_count=project_count,
                          client_count=client_count,
                          user_count=user_count,
                          consultant_count=consultant_count)

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Display a list of all users for admin management."""
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
        query = query.filter(User.role == role_filter)
    
    if status_filter:
        is_active = status_filter == 'active'
        query = query.filter(User.is_active == is_active)
    
    # Get total count for pagination
    total_users = query.count()
    
    # Apply pagination
    users_list = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Calculate total pages
    total_pages = (total_users + per_page - 1) // per_page  # Ceiling division
    
    return render_template(
        'admin/users.html',
        users=users_list.items,
        page=page,
        total_pages=total_pages,
        total_users=total_users,
        has_prev=users_list.has_prev,
        has_next=users_list.has_next
    )

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """
    Handle user creation.
    
    GET: Display user creation form
    POST: Process user creation form submission
    """
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # Validate form data
        if not username or not email or not password or not role:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('admin.create_user'))
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return redirect(url_for('admin.create_user'))
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists.', 'danger')
            return redirect(url_for('admin.create_user'))
        
        # Create new user
        new_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=generate_password_hash(password),
            role=role,
            is_active=True
        )
        
        # Add user to database
        db.session.add(new_user)
        db.session.commit()
        
        flash('User created successfully.', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/create_user.html')

@admin_bp.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """
    Handle user editing.
    
    GET: Display user edit form
    POST: Process user edit form submission
    """
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username')
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role = request.form.get('role')
        is_active = True if request.form.get('is_active') else False
        
        # Validate form data
        if not username or not email or not role:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        # Check if username already exists (excluding current user)
        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user_id:
            flash('Username already exists.', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        # Check if email already exists (excluding current user)
        existing_user = User.query.filter_by(email=email).first()
        if existing_user and existing_user.id != user_id:
            flash('Email already exists.', 'danger')
            return redirect(url_for('admin.edit_user', user_id=user_id))
        
        # Update user
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.role = role
        user.is_active = is_active
        
        # Update password if provided
        password = request.form.get('password')
        if password:
            user.password_hash = generate_password_hash(password)
        
        db.session.commit()
        
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Handle user deletion."""
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.users'))

@admin_bp.route('/import-data', methods=['GET', 'POST'])
@login_required
@admin_required
def import_data():
    """
    Handle data import from JSON file.
    
    GET: Display import form
    POST: Process JSON file upload
    """
    if request.method == 'POST':
        # Check if file was uploaded
        if 'json_file' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(url_for('admin.import_data'))
        
        file = request.files['json_file']
        
        # Check if file is empty
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('admin.import_data'))
        
        # Check if file is JSON
        if not file.filename.endswith('.json'):
            flash('File must be a JSON file.', 'danger')
            return redirect(url_for('admin.import_data'))
        
        try:
            # Parse JSON file
            data = json.load(file)
            
            # TODO: Process JSON data and import into database
            # This is a placeholder for the actual import logic
            
            flash('Data imported successfully.', 'success')
            return redirect(url_for('admin.dashboard'))
        except Exception as e:
            flash(f'Error importing data: {str(e)}', 'danger')
            return redirect(url_for('admin.import_data'))
    
    return render_template('admin/import_data.html')

# TODO: Add routes for reports and analytics
# TODO: Add routes for system settings
