from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from ..models import db, User, Consultant, List, ListItem, Project, Client, Role
from functools import wraps
import json
import os

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Path for settings JSON file
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'settings.json')

# Helper function to load settings from JSON file
def load_settings():
    """Load settings from JSON file or create default if not exists"""
    if not os.path.exists(SETTINGS_FILE):
        # Create default settings
        default_settings = {
            "project_statuses": [
                {"value": "Planning", "description": "Project is in the planning phase"},
                {"value": "In Progress", "description": "Project is currently active"},
                {"value": "Completed", "description": "Project has been completed"},
                {"value": "On Hold", "description": "Project is temporarily paused"},
                {"value": "Cancelled", "description": "Project has been cancelled"}
            ],
            "consultant_statuses": [
                {"value": "Active", "description": "Consultant is currently active"},
                {"value": "Inactive", "description": "Consultant is not currently active"},
                {"value": "On Leave", "description": "Consultant is on leave"}
            ],
            "priority_levels": [
                {"value": "Low", "description": "Low priority"},
                {"value": "Medium", "description": "Medium priority"},
                {"value": "High", "description": "High priority"},
                {"value": "Critical", "description": "Critical priority"}
            ]
        }
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(SETTINGS_FILE), exist_ok=True)
        
        # Save default settings
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(default_settings, f, indent=4)
        
        return default_settings
    
    # Load settings from file
    try:
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading settings: {e}")
        return {}

# Helper function to save settings to JSON file
def save_settings(settings):
    """Save settings to JSON file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

# Custom decorator for admin-only routes
def admin_required(f):
    """
    Decorator to restrict access to admin users only.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is admin
        admin_role = Role.query.filter_by(name='Admin').first()
        if not admin_role or admin_role not in current_user.roles:
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
    """
    # Initialize counts
    project_count = 0
    client_count = 0
    user_count = 0
    consultant_count = 0
    
    # Get role objects
    admin_role = Role.query.filter_by(name='Admin').first()
    manager_role = Role.query.filter_by(name='Manager').first()
    project_manager_role = Role.query.filter_by(name='Project Manager').first()
    
    # Get counts based on user role
    if admin_role in current_user.roles or manager_role in current_user.roles:
        # Admins and Managers see all projects, clients, and users
        project_count = Project.query.count()
        client_count = Client.query.count()
        user_count = User.query.count()
        consultant_count = Consultant.query.count()
    elif project_manager_role in current_user.roles:
        # Project Managers see their assigned projects
        project_count = Project.query.filter_by(manager_id=current_user.id).count()
        # Get clients with projects managed by this user
        client_ids = db.session.query(Project.client_id).filter_by(manager_id=current_user.id).distinct()
        client_count = Client.query.filter(Client.id.in_(client_ids)).count()
        user_count = 0
        consultant_count = Consultant.query.count()
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
        role_names = request.form.getlist('roles[]')
        
        # Validate form data
        if not username or not email or not password or not role_names:
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
            is_active=True
        )
        
        # Add roles to the user
        for role_name in role_names:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                new_user.roles.append(role)
        
        # Add user to database
        db.session.add(new_user)
        db.session.commit()
        
        flash('User created successfully.', 'success')
        return redirect(url_for('admin.users'))
    
    # Get all available roles for the form
    roles = Role.query.all()
    return render_template('admin/create_user.html', roles=roles)

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
        role_names = request.form.getlist('roles[]')
        is_active = True if request.form.get('is_active') else False
        
        # Validate form data
        if not username or not email or not role_names:
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
        user.is_active = is_active
        
        # Update roles
        user.roles = []  # Clear existing roles
        for role_name in role_names:
            role = Role.query.filter_by(name=role_name).first()
            if role:
                user.roles.append(role)
        
        # Update password if provided
        password = request.form.get('password')
        if password:
            user.password_hash = generate_password_hash(password)
        
        db.session.commit()
        
        flash('User updated successfully.', 'success')
        return redirect(url_for('admin.users'))
    
    # Get all available roles for the form
    roles = Role.query.all()
    return render_template('admin/edit_user.html', user=user, roles=roles)

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
            # Get updated settings from request
            updated_settings = request.json
            
            # Update settings
            settings[setting_type] = updated_settings
            
            # Save settings
            if save_settings(settings):
                return jsonify({"success": True, "message": f"{setting_type} settings updated successfully"})
            else:
                return jsonify({"success": False, "message": "Failed to save settings"}), 500
        except Exception as e:
            return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/lists')
@login_required
@admin_required
def lists():
    """
    Display and manage lists for dropdown values.
    """
    # Get all lists
    all_lists = List.query.all()
    
    return render_template('admin/lists.html', lists=all_lists)

@admin_bp.route('/lists/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_list():
    """
    Handle list creation.
    
    GET: Display list creation form
    POST: Process list creation form submission
    """
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        
        # Validate form data
        if not name:
            flash('List name is required.', 'danger')
            return redirect(url_for('admin.create_list'))
        
        # Check if list already exists
        if List.query.filter_by(name=name).first():
            flash('A list with this name already exists.', 'danger')
            return redirect(url_for('admin.create_list'))
        
        # Create new list
        new_list = List(
            name=name,
            description=description
        )
        
        # Add list to database
        db.session.add(new_list)
        db.session.commit()
        
        flash('List created successfully.', 'success')
        return redirect(url_for('admin.lists'))
    
    return render_template('admin/lists/create.html')

@admin_bp.route('/lists/<int:list_id>/items', methods=['GET'])
@login_required
@admin_required
def list_items(list_id):
    """
    Display items for a specific list.
    """
    # Get list
    list_obj = List.query.get_or_404(list_id)
    
    # Get items
    items = ListItem.query.filter_by(list_id=list_id).order_by(ListItem.order).all()
    
    return render_template('admin/lists/items.html', list=list_obj, items=items)

@admin_bp.route('/lists/<int:list_id>/items/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_list_item(list_id):
    """
    Handle list item creation.
    
    GET: Display list item creation form
    POST: Process list item creation form submission
    """
    # Get list
    list_obj = List.query.get_or_404(list_id)
    
    if request.method == 'POST':
        # Get form data
        value = request.form.get('value')
        description = request.form.get('description')
        order = request.form.get('order')
        
        # Validate form data
        if not value:
            flash('Item value is required.', 'danger')
            return redirect(url_for('admin.create_list_item', list_id=list_id))
        
        # Create new list item
        new_item = ListItem(
            list_id=list_id,
            value=value,
            description=description,
            order=int(order) if order else None
        )
        
        # Add item to database
        db.session.add(new_item)
        db.session.commit()
        
        flash('List item created successfully.', 'success')
        return redirect(url_for('admin.list_items', list_id=list_id))
    
    return render_template('admin/lists/create_item.html', list=list_obj)

@admin_bp.route('/lists/manage/<int:list_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def manage_list(list_id=None):
    """
    Simplified list management - create, edit, and manage items all in one view.
    
    GET: Display list management form
    POST: Process list management form submission
    """
    # Get list if it exists
    list_obj = None
    items = []
    
    if list_id:
        list_obj = List.query.get_or_404(list_id)
        items = ListItem.query.filter_by(list_id=list_id).order_by(ListItem.order).all()
    
    if request.method == 'POST':
        # Get form data
        list_name = request.form.get('list_name')
        list_description = request.form.get('list_description')
        
        # Validate form data
        if not list_name:
            flash('List name is required.', 'danger')
            return redirect(url_for('admin.manage_list', list_id=list_id))
        
        # Create or update list
        if list_obj:
            # Update existing list
            list_obj.name = list_name
            list_obj.description = list_description
        else:
            # Create new list
            list_obj = List(
                name=list_name,
                description=list_description
            )
            db.session.add(list_obj)
            db.session.commit()
            list_id = list_obj.id
        
        # Process items
        # First, get all existing items to track which ones to delete
        existing_items = {item.id: item for item in ListItem.query.filter_by(list_id=list_id).all()}
        processed_item_ids = set()
        
        # Get all item data from form
        item_values = request.form.getlist('item_value[]')
        item_descriptions = request.form.getlist('item_description[]')
        item_orders = request.form.getlist('item_order[]')
        item_ids = request.form.getlist('item_id[]')
        
        # Process each item
        for i in range(len(item_values)):
            value = item_values[i].strip()
            if not value:  # Skip empty values
                continue
                
            description = item_descriptions[i] if i < len(item_descriptions) else ''
            order = int(item_orders[i]) if i < len(item_orders) and item_orders[i].isdigit() else i+1
            item_id = int(item_ids[i]) if i < len(item_ids) and item_ids[i].isdigit() else None
            
            if item_id and item_id in existing_items:
                # Update existing item
                item = existing_items[item_id]
                item.value = value
                item.description = description
                item.order = order
                processed_item_ids.add(item_id)
            else:
                # Create new item
                new_item = ListItem(
                    list_id=list_id,
                    value=value,
                    description=description,
                    order=order
                )
                db.session.add(new_item)
        
        # Delete items that weren't in the form
        for item_id, item in existing_items.items():
            if item_id not in processed_item_ids:
                db.session.delete(item)
        
        # Save all changes
        db.session.commit()
        
        flash('List and items saved successfully.', 'success')
        return redirect(url_for('admin.lists'))
    
    # For GET request or if form validation fails
    return render_template('admin/lists/manage.html', 
                          list=list_obj, 
                          items=items)

@admin_bp.route('/lists/manage', methods=['GET'])
@login_required
@admin_required
def manage_new_list():
    """
    Create a new list using the management interface.
    """
    return render_template('admin/lists/manage.html', 
                          list=None, 
                          items=[])

@admin_bp.route('/lists/delete/<int:list_id>', methods=['POST'])
@login_required
@admin_required
def delete_list(list_id):
    """
    Handle list deletion.
    """
    list_obj = List.query.get_or_404(list_id)
    db.session.delete(list_obj)
    db.session.commit()
    flash('List deleted successfully.', 'success')
    return redirect(url_for('admin.lists'))

# TODO: Add routes for reports and analytics
# TODO: Add routes for system settings
