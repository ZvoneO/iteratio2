from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import db, Project, ProjectTemplate, PhaseTemplate, User, Client, ProductService
from functools import wraps

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')

# Custom decorator for manager-only routes
def manager_required(f):
    """
    Decorator for routes that require manager privileges.
    Redirects to projects list if user is not a manager or admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (current_user.role != 'Admin' and current_user.role != 'Manager'):
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
        if not current_user.is_authenticated or (
            current_user.role != 'Admin' and 
            current_user.role != 'Manager' and 
            current_user.role != 'Project Manager'
        ):
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('projects.list_projects'))
        return f(*args, **kwargs)
    return decorated_function

@projects_bp.route('/')
@login_required
def list_projects():
    """
    Display a list of projects based on user role.
    Different user roles see different projects.
    """
    if current_user.role == 'Admin' or current_user.role == 'Manager':
        # Admins and Managers see all projects
        projects = Project.query.all()
    elif current_user.role == 'Project Manager':
        # Project Managers see projects they manage
        projects = Project.query.filter_by(manager_id=current_user.id).all()
    else:  # Consultant
        # Consultants see projects they're assigned to
        # TODO: Implement consultant-project assignment and filtering
        projects = []
    
    return render_template('projects/list.html', projects=projects)

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
    managers = User.query.filter(User.role.in_(['Admin', 'Manager', 'Project Manager'])).all()
    templates = ProjectTemplate.query.all()
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        client_id = request.form.get('client_id')
        manager_id = request.form.get('manager_id')
        template_id = request.form.get('template_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        status = request.form.get('status')
        
        # Validate form data
        if not name or not client_id or not manager_id or not status:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('projects.create_project'))
        
        # Create new project
        new_project = Project(
            name=name,
            description=description,
            client_id=client_id,
            manager_id=manager_id,
            template_id=template_id if template_id else None,
            start_date=start_date if start_date else None,
            end_date=end_date if end_date else None,
            status=status
        )
        
        # Add project to database
        db.session.add(new_project)
        db.session.commit()
        
        # If template was selected, copy products from template to project
        if template_id:
            template = ProjectTemplate.query.get(template_id)
            if template and template.products:
                for product in template.products:
                    new_project.products.append(product)
                db.session.commit()
        
        flash('Project created successfully.', 'success')
        return redirect(url_for('projects.list_projects'))
    
    return render_template('projects/create.html', 
                          clients=clients, 
                          managers=managers,
                          templates=templates)

@projects_bp.route('/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
@project_manager_required
def edit_project(project_id):
    """
    Handle project editing.
    
    GET: Display project edit form
    POST: Process project edit form submission
    """
    project = Project.query.get_or_404(project_id)
    
    # Check if user has permission to edit this project
    if current_user.role == 'Project Manager' and project.manager_id != current_user.id:
        flash('You do not have permission to edit this project.', 'danger')
        return redirect(url_for('projects.list_projects'))
    
    # Get clients and managers for dropdown
    clients = Client.query.all()
    managers = User.query.filter(User.role.in_(['Admin', 'Manager', 'Project Manager'])).all()
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        client_id = request.form.get('client_id')
        manager_id = request.form.get('manager_id')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        status = request.form.get('status')
        
        # Validate form data
        if not name or not client_id or not manager_id or not status:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('projects.edit_project', project_id=project_id))
        
        # Update project
        project.name = name
        project.description = description
        project.client_id = client_id
        project.manager_id = manager_id
        project.start_date = start_date if start_date else None
        project.end_date = end_date if end_date else None
        project.status = status
        
        db.session.commit()
        
        flash('Project updated successfully.', 'success')
        return redirect(url_for('projects.list_projects'))
    
    return render_template('projects/edit.html', 
                          project=project,
                          clients=clients, 
                          managers=managers)

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
    if current_user.role == 'Project Manager' and project.manager_id != current_user.id:
        # TODO: Check if consultant is assigned to this project
        if current_user.role == 'Consultant':
            flash('You do not have permission to view this project.', 'danger')
            return redirect(url_for('projects.list_projects'))
    
    return render_template('projects/view.html', project=project)

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
    managers = User.query.filter(User.role.in_(['Admin', 'Manager'])).all()
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
    managers = User.query.filter(User.role.in_(['Admin', 'Manager'])).all()
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
