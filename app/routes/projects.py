from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from ..models import db, Project, ProjectTemplate, PhaseTemplate, User, Client, ProductService, Role, ProjectGroup, ProjectPhase, ProductGroup, List, ListItem
from functools import wraps
import os
import json
from datetime import datetime
from ..utils import user_has_role as utils_user_has_role
from ..utils import user_has_any_role as utils_user_has_any_role

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')

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

# Helper function to check if user has a specific role
def user_has_role(user, role_name):
    """Check if a user has a specific role."""
    return utils_user_has_role(user, role_name)

# Helper function to check if user has any of the specified roles
def user_has_any_role(user, role_names):
    """Check if a user has any of the specified roles."""
    return utils_user_has_any_role(user, role_names)

# Custom decorator for manager-only routes
def manager_required(f):
    """
    Decorator for routes that require manager privileges.
    Redirects to projects list if user is not a manager or admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not user_has_any_role(current_user, ['Admin', 'Manager']):
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('projects.list_projects'))
        return f(*args, **kwargs)
    return decorated_function

# Custom decorator for project manager-only routes
def project_manager_required(f):
    """
    Decorator for routes that require project manager privileges.
    Redirects to projects list if user is not a project manager, manager, or admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (user_has_any_role(current_user, ['Admin', 'Manager', 'Project Manager']) or current_user.username == 'admin'):
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('projects.list_projects'))
        return f(*args, **kwargs)
    return decorated_function

@projects_bp.route('/')
@login_required
def list_projects():
    """
    Display a list of all projects with filtering options.
    
    GET: Display projects list with optional filters
    """
    # Get filter parameters
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status_filter', '')
    client_filter = request.args.get('client_filter', '')
    
    # Base query
    query = Project.query
    
    # Apply filters
    if search_query:
        query = query.filter(Project.name.ilike(f'%{search_query}%'))
    
    if status_filter:
        query = query.filter(Project.status == status_filter)
    
    if client_filter:
        query = query.filter(Project.client_id == client_filter)
    
    # Get all projects with filters applied
    projects = query.order_by(Project.created_at.desc()).all()
    
    # Get all clients for filter dropdown
    clients = Client.query.all()
    
    # Get project statuses for dropdown from ProjectStatusList
    project_statuses_list = List.query.filter_by(name='ProjectStatusList').first()
    if project_statuses_list:
        # Directly query the ListItem table to ensure we get the items
        project_statuses = ListItem.query.filter_by(list_id=project_statuses_list.id).order_by(ListItem.order).all()
    else:
        # Try to find the list by ID 6 (known ProjectStatusList ID)
        project_statuses_list = List.query.filter_by(id=6).first()
        if project_statuses_list:
            project_statuses = ListItem.query.filter_by(list_id=project_statuses_list.id).order_by(ListItem.order).all()
        else:
            project_statuses = []
    
    return render_template('projects/list.html', projects=projects, clients=clients, project_statuses=project_statuses)

@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
@project_manager_required
def create_project():
    """
    Handle project creation.
    
    GET: Display project creation form
    POST: Process project creation form submission
    """
    # Get clients and managers for dropdown
    clients = Client.query.all()
    managers = User.query.join(User.roles).filter(Role.name == 'Project Manager').all()
    templates = ProjectTemplate.query.all()
    
    # Get product groups for dropdown
    product_groups = ProductGroup.query.all()
    
    # Get lists for dropdowns - Use list_id=5 for Industries
    industries_list = List.query.filter_by(id=5).first()
    industries = industries_list.items if industries_list else []
    
    # Get Profit Centers from list id=2
    profit_centers_list = List.query.filter_by(id=2).first()
    profit_centers = profit_centers_list.items if profit_centers_list else []
    
    phase_durations_list = List.query.filter_by(name='PhaseDuration').first()
    phase_durations = phase_durations_list.items if phase_durations_list else []
    
    # Get project statuses for dropdown from ProjectStatusList
    project_statuses_list = List.query.filter_by(name='ProjectStatusList').first()
    if project_statuses_list:
        # Directly query the ListItem table to ensure we get the items
        project_statuses = ListItem.query.filter_by(list_id=project_statuses_list.id).order_by(ListItem.order).all()
    else:
        # Try to find the list by ID 6 (known ProjectStatusList ID)
        project_statuses_list = List.query.filter_by(id=6).first()
        if project_statuses_list:
            project_statuses = ListItem.query.filter_by(list_id=project_statuses_list.id).order_by(ListItem.order).all()
        else:
            project_statuses = []
    
    # Debug print
    print(f"DEBUG - Project Statuses List: {project_statuses_list}")
    print(f"DEBUG - Project Statuses: {project_statuses}")
    if project_statuses:
        for status in project_statuses:
            print(f"DEBUG - Status: {status.id} - {status.value}")
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            description = request.form.get('description')
            client_id = request.form.get('client_id')
            manager_id = request.form.get('manager_id')
            template_id = request.form.get('template_id')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            industry_id = request.form.get('industry_id') if request.form.get('industry_id') else None
            profit_center_id = request.form.get('profit_center_id') if request.form.get('profit_center_id') else None
            
            # Get status_id from form
            status_id = request.form.get('status_id')
            
            # Debug print
            print(f"DEBUG - Form data received:")
            print(f"DEBUG - name: {name}")
            print(f"DEBUG - client_id: {client_id}")
            print(f"DEBUG - manager_id: {manager_id}")
            print(f"DEBUG - status_id: {status_id}")
            
            # Set default status to "Preparation" if not provided
            if not status_id and project_statuses:
                # Find the "Preparation" status
                preparation_status = next((s for s in project_statuses if s.value == "Preparation"), None)
                if preparation_status:
                    status_id = preparation_status.id
                    print(f"DEBUG - Using default status_id: {status_id}")
            
            # Get the status value from the status_id
            status_value = None
            if status_id:
                status_item = ListItem.query.get(status_id)
                if status_item:
                    status_value = status_item.value
                    print(f"DEBUG - Found status_value: {status_value}")
            
            # If no status_value was found, default to "Preparation"
            if not status_value:
                status_value = "Preparation"
                print(f"DEBUG - Using default status_value: {status_value}")
            
            # Validate form data
            if not name or not client_id or not manager_id:
                flash('All required fields must be filled.', 'danger')
                return redirect(url_for('projects.create_project'))
            
            # Validate dates
            if start_date and end_date:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                if start_date_obj > end_date_obj:
                    flash('End date must be after start date.', 'danger')
                    return redirect(url_for('projects.create_project'))
            else:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date() if start_date else None
                end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date() if end_date else None
            
            # Create new project
            new_project = Project(
                name=name,
                description=description,
                client_id=client_id,
                manager_id=manager_id,
                template_id=template_id if template_id else None,
                start_date=start_date_obj,
                end_date=end_date_obj,
                status=status_value,
                status_id=status_id,
                industry_id=industry_id,
                profit_center_id=profit_center_id
            )
            
            # Add project to database
            db.session.add(new_project)
            db.session.commit()
            print(f"DEBUG - Project created with ID: {new_project.id}")
            
            # If template was selected, copy products from template to project
            if template_id:
                template = ProjectTemplate.query.get(template_id)
                if template and template.products:
                    for product in template.products:
                        new_project.products.append(product)
                    db.session.commit()
            
            # Process project groups and phases if submitted
            if 'group_data' in request.form:
                try:
                    group_data = json.loads(request.form.get('group_data'))
                    print(f"DEBUG - Processing {len(group_data)} groups")
                    
                    for group_idx, group in enumerate(group_data):
                        # Create project group
                        new_group = ProjectGroup(
                            project_id=new_project.id,
                            product_group_id=group['product_group_id'],
                            order=group_idx
                        )
                        db.session.add(new_group)
                        db.session.flush()  # Get the new group ID
                        
                        # Create phases for this group
                        for phase_idx, phase in enumerate(group['phases']):
                            new_phase = ProjectPhase(
                                group_id=new_group.id,
                                name=phase['name'],
                                description=phase.get('description', ''),
                                duration_id=phase.get('duration_id'),
                                online=phase.get('online', False),
                                order=phase_idx
                            )
                            db.session.add(new_phase)
                    
                    db.session.commit()
                    print(f"DEBUG - Project structure processed successfully")
                except Exception as e:
                    db.session.rollback()
                    print(f"DEBUG - Error processing project structure: {str(e)}")
                    import traceback
                    print(traceback.format_exc())
                    flash(f'Error processing project structure: {str(e)}', 'danger')
                    return redirect(url_for('projects.edit_project', project_id=new_project.id))
            
            flash('Project created successfully!', 'success')
            return redirect(url_for('projects.view_project', project_id=new_project.id))
        
        except Exception as e:
            db.session.rollback()
            print(f"DEBUG - Error creating project: {str(e)}")
            import traceback
            print(traceback.format_exc())
            flash(f'Error creating project: {str(e)}', 'danger')
            return redirect(url_for('projects.create_project'))
    
    return render_template(
        'projects/create.html', 
        clients=clients, 
        managers=managers, 
        templates=templates,
        product_groups=product_groups,
        industries=industries,
        profit_centers=profit_centers,
        phase_durations=phase_durations,
        project_statuses=project_statuses
    )

@projects_bp.route('/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
@project_manager_required
def edit_project(project_id):
    """
    Handle project editing.
    
    GET: Display project editing form
    POST: Process project editing form submission
    """
    # Get project
    project = Project.query.get_or_404(project_id)
    
    # Check if user has permission to edit this project
    if not user_has_role(current_user, 'Admin') and not user_has_role(current_user, 'Manager') and project.manager_id != current_user.id:
        flash('You do not have permission to edit this project.', 'danger')
        return redirect(url_for('projects.list_projects'))
    
    # Get clients and managers for dropdown
    clients = Client.query.all()
    managers = User.query.join(User.roles).filter(Role.name == 'Project Manager').all()
    
    # Get product groups for dropdown
    product_groups = ProductGroup.query.all()
    
    # Get lists for dropdowns
    industries_list = List.query.filter_by(id=5).first()
    industries = industries_list.items if industries_list else []
    
    # Get Profit Centers from list id=2
    profit_centers_list = List.query.filter_by(id=2).first()
    profit_centers = profit_centers_list.items if profit_centers_list else []
    
    phase_durations_list = List.query.filter_by(name='PhaseDuration').first()
    phase_durations = phase_durations_list.items if phase_durations_list else []
    
    # Get project statuses for dropdown from ProjectStatusList
    project_statuses_list = List.query.filter_by(name='ProjectStatusList').first()
    if project_statuses_list:
        # Directly query the ListItem table to ensure we get the items
        project_statuses = ListItem.query.filter_by(list_id=project_statuses_list.id).order_by(ListItem.order).all()
    else:
        # Try to find the list by ID 6 (known ProjectStatusList ID)
        project_statuses_list = List.query.filter_by(id=6).first()
        if project_statuses_list:
            project_statuses = ListItem.query.filter_by(list_id=project_statuses_list.id).order_by(ListItem.order).all()
        else:
            project_statuses = []
    
    if request.method == 'POST':
        # Get form data
        project.name = request.form.get('name')
        project.description = request.form.get('description')
        project.client_id = request.form.get('client_id')
        project.manager_id = request.form.get('manager_id')
        project.industry_id = request.form.get('industry_id') if request.form.get('industry_id') else None
        project.profit_center_id = request.form.get('profit_center_id') if request.form.get('profit_center_id') else None
        
        # Get status_id from form
        status_id = request.form.get('status_id')
        
        # Update status_id and status value
        if status_id:
            project.status_id = status_id
            # Get the status value from the status_id
            status_item = ListItem.query.get(status_id)
            if status_item:
                project.status = status_item.value
        # Keep existing status or set default if none
        elif not project.status:
            # Find the "Preparation" status
            preparation_status = next((s for s in project_statuses if s.value == "Preparation"), None)
            if preparation_status:
                project.status_id = preparation_status.id
                project.status = "Preparation"
            else:
                project.status = "Preparation"
        
        # Validate form data
        if not project.name or not project.client_id or not project.manager_id:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('projects.edit_project', project_id=project_id))
        
        # Validate dates
        if project.start_date and project.end_date:
            if project.start_date > project.end_date:
                flash('End date must be after start date.', 'danger')
                return redirect(url_for('projects.edit_project', project_id=project_id))
        
        # Convert string dates to Python date objects
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        
        if start_date:
            project.start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        else:
            project.start_date = None
            
        if end_date:
            project.end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        else:
            project.end_date = None
        
        # Process project groups and phases if submitted
        if 'group_data' in request.form:
            try:
                # Delete existing groups and phases
                for group in project.groups:
                    db.session.delete(group)  # This will cascade delete phases
                db.session.flush()
                
                # Add new groups and phases
                group_data = json.loads(request.form.get('group_data'))
                for group_idx, group in enumerate(group_data):
                    # Create project group
                    new_group = ProjectGroup(
                        project_id=project.id,
                        product_group_id=group['product_group_id'],
                        order=group_idx
                    )
                    db.session.add(new_group)
                    db.session.flush()  # Get the new group ID
                    
                    # Create phases for this group
                    for phase_idx, phase in enumerate(group['phases']):
                        new_phase = ProjectPhase(
                            group_id=new_group.id,
                            name=phase['name'],
                            description=phase.get('description', ''),
                            duration_id=phase.get('duration_id'),
                            online=phase.get('online', False),
                            order=phase_idx
                        )
                        db.session.add(new_phase)
            except Exception as e:
                db.session.rollback()
                flash(f'Error processing project structure: {str(e)}', 'danger')
                return redirect(url_for('projects.edit_project', project_id=project_id))
        
        # Save changes
        db.session.commit()
        
        flash('Project updated successfully!', 'success')
        return redirect(url_for('projects.view_project', project_id=project_id))
    
    return render_template(
        'projects/edit.html', 
        project=project,
        clients=clients, 
        managers=managers,
        product_groups=product_groups,
        industries=industries,
        profit_centers=profit_centers,
        phase_durations=phase_durations,
        project_statuses=project_statuses
    )

@projects_bp.route('/delete/<int:project_id>', methods=['POST'])
@login_required
@manager_required
def delete_project(project_id):
    """Handle project deletion."""
    project = Project.query.get_or_404(project_id)
    
    db.session.delete(project)
    db.session.commit()
    
    flash('Project deleted successfully.', 'success')
    return redirect(url_for('projects.list_projects'))

@projects_bp.route('/view/<int:project_id>')
@login_required
def view_project(project_id):
    """Display project details."""
    project = Project.query.get_or_404(project_id)
    
    # Check if user has permission to view this project
    if not user_has_role(current_user, 'Admin') and not user_has_role(current_user, 'Manager') and project.manager_id != current_user.id:
        # TODO: Check if consultant is assigned to this project
        if user_has_role(current_user, 'Consultant'):
            flash('You do not have permission to view this project.', 'danger')
            return redirect(url_for('projects.list_projects'))
    
    # Get phase durations for reference
    phase_durations_list = List.query.filter_by(name='PhaseDuration').first()
    phase_durations = {item.id: item.value for item in phase_durations_list.items} if phase_durations_list else {}
    
    return render_template('projects/view.html', project=project, phase_durations=phase_durations)

# Project Template Routes

@projects_bp.route('/templates')
@login_required
@manager_required
def list_templates():
    """Display a list of project templates."""
    templates = ProjectTemplate.query.all()
    return render_template('projects/templates/list.html', templates=templates)

@projects_bp.route('/templates/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_template():
    """
    Handle project template creation.
    
    GET: Display template creation form
    POST: Process template creation form submission
    """
    # Get clients and managers for dropdown
    clients = Client.query.all()
    managers = User.query.join(User.roles).filter(Role.name == 'Project Manager').all()
    products = ProductService.query.all()
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        client_id = request.form.get('client_id')
        manager_id = request.form.get('manager_id')
        
        # Validate form data
        if not name:
            flash('Template name is required.', 'danger')
            return redirect(url_for('projects.create_template'))
        
        # Create new template
        new_template = ProjectTemplate(
            name=name,
            description=description,
            client_id=client_id if client_id else None,
            manager_id=manager_id if manager_id else None
        )
        
        # Add template to database
        db.session.add(new_template)
        db.session.commit()
        
        # Process phases
        phase_names = request.form.getlist('phase_name[]')
        phase_descriptions = request.form.getlist('phase_description[]')
        phase_durations = request.form.getlist('phase_duration[]')
        
        for i in range(len(phase_names)):
            if phase_names[i]:  # Only add if name is provided
                phase = PhaseTemplate(
                    template_id=new_template.id,
                    name=phase_names[i],
                    description=phase_descriptions[i] if i < len(phase_descriptions) else None,
                    order=i+1,
                    duration_days=phase_durations[i] if i < len(phase_durations) and phase_durations[i] else None
                )
                db.session.add(phase)
        
        # Process products
        product_ids = request.form.getlist('product_ids[]')
        for product_id in product_ids:
            product = ProductService.query.get(product_id)
            if product:
                new_template.products.append(product)
        
        db.session.commit()
        
        flash('Project template created successfully.', 'success')
        return redirect(url_for('projects.list_templates'))
    
    return render_template('projects/templates/create.html', 
                          clients=clients, 
                          managers=managers,
                          products=products)

@projects_bp.route('/templates/edit/<int:template_id>', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_template(template_id):
    """
    Handle project template editing.
    
    GET: Display template edit form
    POST: Process template edit form submission
    """
    template = ProjectTemplate.query.get_or_404(template_id)
    
    # Get clients and managers for dropdown
    clients = Client.query.all()
    managers = User.query.join(User.roles).filter(Role.name == 'Project Manager').all()
    products = ProductService.query.all()
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        client_id = request.form.get('client_id')
        manager_id = request.form.get('manager_id')
        
        # Validate form data
        if not name:
            flash('Template name is required.', 'danger')
            return redirect(url_for('projects.edit_template', template_id=template_id))
        
        # Update template
        template.name = name
        template.description = description
        template.client_id = client_id if client_id else None
        template.manager_id = manager_id if manager_id else None
        
        # Process phases
        # First, remove existing phases
        for phase in template.phases:
            db.session.delete(phase)
        
        # Then add new phases
        phase_names = request.form.getlist('phase_name[]')
        phase_descriptions = request.form.getlist('phase_description[]')
        phase_durations = request.form.getlist('phase_duration[]')
        
        for i in range(len(phase_names)):
            if phase_names[i]:  # Only add if name is provided
                phase = PhaseTemplate(
                    template_id=template.id,
                    name=phase_names[i],
                    description=phase_descriptions[i] if i < len(phase_descriptions) else None,
                    order=i+1,
                    duration_days=phase_durations[i] if i < len(phase_durations) and phase_durations[i] else None
                )
                db.session.add(phase)
        
        # Process products
        # First, remove existing products
        template.products = []
        
        # Then add new products
        product_ids = request.form.getlist('product_ids[]')
        for product_id in product_ids:
            product = ProductService.query.get(product_id)
            if product:
                template.products.append(product)
        
        db.session.commit()
        
        flash('Project template updated successfully.', 'success')
        return redirect(url_for('projects.list_templates'))
    
    return render_template('projects/templates/edit.html', 
                          template=template,
                          clients=clients, 
                          managers=managers,
                          products=products)

@projects_bp.route('/templates/delete/<int:template_id>', methods=['POST'])
@login_required
@manager_required
def delete_template(template_id):
    """Handle project template deletion."""
    template = ProjectTemplate.query.get_or_404(template_id)
    
    db.session.delete(template)
    db.session.commit()
    
    flash('Project template deleted successfully.', 'success')
    return redirect(url_for('projects.list_templates'))

@projects_bp.route('/templates/view/<int:template_id>')
@login_required
@project_manager_required
def view_template(template_id):
    """Display project template details."""
    template = ProjectTemplate.query.get_or_404(template_id)
    return render_template('projects/templates/view.html', template=template)

# TODO: Add routes for project tasks
# TODO: Add routes for consultant assignment to projects
# TODO: Add routes for project phases

@projects_bp.route('/api/product-groups/<int:group_id>/elements')
@login_required
def get_product_group_elements(group_id):
    """
    API endpoint to get product elements for a product group.
    Returns a JSON object with:
    - elements: Array of elements with label, activity, and other properties
    - group: Information about the product group
    - count: Total number of elements
    """
    try:
        # Get product group
        product_group = ProductGroup.query.get_or_404(group_id)
        
        # Get elements
        elements = product_group.elements
        
        # Format elements for JSON response
        elements_data = [
            {
                'id': element.id,
                'label': element.label,
                'activity': element.activity,
                'group_duration_id': product_group.duration_id
            }
            for element in elements
        ]
        
        # Include group information
        response_data = {
            'elements': elements_data,
            'group': {
                'id': product_group.id,
                'name': product_group.name,
                'description': product_group.description,
                'duration_id': product_group.duration_id
            },
            'count': len(elements_data),
            'success': True
        }
        
        return jsonify(response_data)
    except Exception as e:
        # Return error response
        return jsonify({
            'success': False,
            'error': str(e),
            'message': 'Failed to retrieve product group elements'
        }), 500

@projects_bp.route('/debug-create')
@login_required
def debug_create():
    """Debug route to check what's being passed to the template"""
    # Get clients and managers for dropdown
    clients = Client.query.all()
    managers = User.query.join(User.roles).filter(Role.name == 'Project Manager').all()
    
    # Get product groups for dropdown
    product_groups = ProductGroup.query.all()
    
    # Get lists for dropdowns
    industries_list = List.query.filter_by(id=5).first()
    industries = industries_list.items if industries_list else []
    print(f"DEBUG - Industries List: {industries_list}")
    print(f"DEBUG - Industries Count: {len(industries)}")
    
    # Get Profit Centers from list id=2
    profit_centers_list = List.query.filter_by(id=2).first()
    profit_centers = profit_centers_list.items if profit_centers_list else []
    print(f"DEBUG - Profit Centers List: {profit_centers_list}")
    print(f"DEBUG - Profit Centers Count: {len(profit_centers)}")
    
    phase_durations_list = List.query.filter_by(name='PhaseDuration').first()
    phase_durations = phase_durations_list.items if phase_durations_list else []
    print(f"DEBUG - Phase Durations List: {phase_durations_list}")
    print(f"DEBUG - Phase Durations Count: {len(phase_durations)}")
    
    # Get project statuses for dropdown from ProjectStatusList
    project_statuses_list = List.query.filter_by(name='ProjectStatusList').first()
    print(f"DEBUG - Project Statuses List: {project_statuses_list}")
    
    # Try both ways to get items
    project_statuses_1 = project_statuses_list.items if project_statuses_list else []
    print(f"DEBUG - Project Statuses Count (using .items): {len(project_statuses_1)}")
    
    project_statuses_2 = ListItem.query.filter_by(list_id=project_statuses_list.id).all() if project_statuses_list else []
    print(f"DEBUG - Project Statuses Count (using direct query): {len(project_statuses_2)}")
    
    # Use the direct query method
    project_statuses = project_statuses_2
    
    # Debug output
    debug_info = {
        'project_statuses_list': str(project_statuses_list),
        'project_statuses': [{'id': s.id, 'value': s.value} for s in project_statuses],
        'industries': [{'id': i.id, 'value': i.value} for i in industries],
        'profit_centers': [{'id': p.id, 'value': p.value} for p in profit_centers],
        'phase_durations': [{'id': d.id, 'value': d.value} for d in phase_durations],
    }
    
    return jsonify(debug_info)
