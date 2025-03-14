    # Projects Module Specification

## Overview

The Projects module is a core component of the Resource Planning Application. It allows users to create, manage, and track projects throughout their lifecycle. Projects are organized with a hierarchical structure consisting of project groups and phases, and are associated with clients, managers, and various metadata.

## Database Structure

### Main Tables

#### Project

The `Project` model is the central entity in the Projects module.

```python
class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    template_id = db.Column(db.Integer, db.ForeignKey('project_templates.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20))  # Automatically set to "Preparation" for new projects
    industry_id = db.Column(db.Integer, db.ForeignKey('list_items.id'))
    profit_center_id = db.Column(db.Integer, db.ForeignKey('list_items.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = db.relationship('ProductService', secondary='project_products', lazy='subquery',
                              backref=db.backref('projects', lazy=True))
    groups = db.relationship('ProjectGroup', backref='project', lazy=True, 
                            cascade="all, delete-orphan", order_by="ProjectGroup.order")
```

#### ProjectGroup

Project groups organize phases within a project and are associated with product groups.

```python
class ProjectGroup(db.Model):
    __tablename__ = 'project_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    product_group_id = db.Column(db.Integer, db.ForeignKey('product_groups.id'))
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    phases = db.relationship('ProjectPhase', backref='group', lazy=True, 
                            cascade="all, delete-orphan", order_by="ProjectPhase.order")
```

#### ProjectPhase

Phases are the individual components of a project group, representing specific stages of work.

```python
class ProjectPhase(db.Model):
    __tablename__ = 'project_phases'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('project_groups.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration_id = db.Column(db.Integer, db.ForeignKey('list_items.id'))
    online = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='Not Started')  # Not Started, In Progress, Completed
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### ProjectTemplate

Templates allow for quick creation of projects with predefined structures.

```python
class ProjectTemplate(db.Model):
    __tablename__ = 'project_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = db.relationship('ProductService', secondary='template_products', lazy='subquery',
                              backref=db.backref('templates', lazy=True))
    structure = db.relationship('TemplateGroup', backref='template', lazy=True, 
                               cascade="all, delete-orphan", order_by="TemplateGroup.order")
```

### Supporting Tables

#### List and ListItem

These tables store various dropdown options used throughout the application.

```python
class List(db.Model):
    __tablename__ = 'lists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('ListItem', backref='list', lazy=True, cascade="all, delete-orphan")

class ListItem(db.Model):
    __tablename__ = 'list_items'
    
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id', ondelete='CASCADE'), nullable=False)
    value = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

Important lists for the Projects module:
- ProjectStatusList (ID: 6): Contains project status options (Preparation, Initiation, Planning, Implementation, Closure, Paid, One-Time)
- PhaseDuration: Contains duration options for project phases
- Industry (ID: 5): Contains industry options
- ProfitCenter (ID: 2): Contains profit center options

## Routes and Controllers

The Projects module is implemented in `app/routes/projects.py` with the following routes:

### Main Project Routes

#### List Projects
```python
@projects_bp.route('/')
@login_required
def list_projects():
    """Display a list of all projects with filtering options."""
```

- **Method**: GET
- **Template**: projects/list.html
- **Access**: All authenticated users
- **Functionality**: Displays all projects with sorting and filtering options

#### Create Project
```python
@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
@project_manager_required
def create_project():
    """Handle project creation."""
```

- **Method**: GET, POST
- **Template**: projects/create.html
- **Access**: Users with Project Manager role
- **Functionality**: 
  - GET: Displays the project creation form
  - POST: Processes form submission and creates a new project

#### Edit Project
```python
@projects_bp.route('/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
@project_manager_required
def edit_project(project_id):
    """Handle project editing."""
```

- **Method**: GET, POST
- **Template**: projects/edit.html
- **Access**: Project Manager of the specific project or users with Admin/Manager roles
- **Functionality**: 
  - GET: Displays the project editing form
  - POST: Processes form submission and updates the project

#### View Project
```python
@projects_bp.route('/view/<int:project_id>')
@login_required
def view_project(project_id):
    """Display project details."""
```

- **Method**: GET
- **Template**: projects/view.html
- **Access**: All authenticated users
- **Functionality**: Displays detailed information about a specific project

#### Delete Project
```python
@projects_bp.route('/delete/<int:project_id>', methods=['POST'])
@login_required
@manager_required
def delete_project(project_id):
    """Handle project deletion."""
```

- **Method**: POST
- **Access**: Users with Manager role
- **Functionality**: Deletes a project and all associated data

### API Routes

#### Get Product Group Elements
```python
@projects_bp.route('/api/product-groups/<int:group_id>/elements')
@login_required
def get_product_group_elements(group_id):
    """API endpoint to get elements for a product group."""
```

- **Method**: GET
- **Response**: JSON
- **Access**: All authenticated users
- **Functionality**: Returns elements associated with a specific product group for populating project phases

### Debug Routes

```python
@projects_bp.route('/debug-create')
@login_required
def debug_create():
    """Debug route to check what's being passed to the template."""
```

- **Method**: GET
- **Response**: JSON
- **Access**: All authenticated users
- **Functionality**: Returns debug information about the data being passed to the create project template

## Forms and UI Components

### Project Creation Form

The project creation form is divided into several sections:

1. **Project Information**
   - Project Name (required)
   - Description
   - Client (required, with search functionality)
   - Project Manager (required, dropdown)
   - Start Date
   - End Date
   - Industry (dropdown)
   - Profit Center (dropdown)

2. **Project Structure**
   - Dynamic addition of project groups
   - Each group is associated with a product group
   - Each group contains phases
   - Phases can be populated automatically from product group elements
   - Phases can be reordered using drag-and-drop

3. **Form Actions**
   - Create Project button
   - Cancel button

### Project Edit Form

The project edit form has similar fields to the creation form, with additional sections:

1. **Project Phases**
   - Table view of all phases
   - Status management for each phase
   - Ability to add/delete phases

2. **Products & Services**
   - List of associated products/services
   - Ability to add/remove products

## UI Implementation

### Templates

The Projects module uses Jinja2 templates located in `app/templates/projects/`:

- **list.html**: Displays a list of all projects
- **create.html**: Form for creating new projects
- **edit.html**: Form for editing existing projects
- **view.html**: Detailed view of a project

### Styling

The application uses Bootstrap 5 for base styling with custom CSS for specific components:

1. **Card-based Layout**
   - Each section is contained in a Bootstrap card
   - Shadow effects for depth
   - White backgrounds with consistent padding

2. **Custom Components**
   - Phase items with flex layout
   - Group items with nested structure
   - Drag handles for sortable elements

3. **Form Controls**
   - Bootstrap form controls with custom validation
   - Custom dropdown for client search
   - Date pickers for start/end dates

### JavaScript Components

The Projects module uses several JavaScript components:

1. **SortableJS**
   - Used for drag-and-drop reordering of groups and phases
   - Configured with animation and handle options

2. **Client Search**
   - Custom AJAX-based search functionality
   - Debounced input handling
   - Dropdown results with selection

3. **Dynamic Form Elements**
   - Add/remove project groups
   - Add/remove phases within groups
   - Populate phases from product group elements

4. **Form Validation**
   - Client-side validation for required fields
   - Date validation (end date after start date)
   - Group and phase validation

## Data Flow

### Project Creation

1. User fills out the project information form
2. User adds project groups and phases
3. On form submission:
   - Basic validation is performed
   - A new Project record is created
   - Project groups and phases are created based on the form data
   - If a template was selected, products are copied from the template
   - User is redirected to the project view page

### Project Status Management

1. Project status is automatically set to "Preparation" for new projects
2. Status can be viewed but not directly edited through the UI
3. Status changes are managed programmatically based on project lifecycle events

## Security and Access Control

The Projects module implements several security measures:

1. **Authentication**
   - All routes require authentication (`@login_required`)
   - Sensitive operations require specific roles

2. **Authorization**
   - Project creation requires Project Manager role
   - Project editing requires Project Manager role or ownership
   - Project deletion requires Manager role

3. **Data Validation**
   - Server-side validation for all form submissions
   - CSRF protection for all forms
   - Input sanitization for all user inputs

## Integration Points

The Projects module integrates with several other modules:

1. **Clients Module**
   - Projects are associated with clients
   - Client search functionality in project forms

2. **Users Module**
   - Projects are assigned to project managers
   - Role-based access control

3. **Products Module**
   - Projects can have associated products/services
   - Product groups provide structure for project phases

## Implementation Notes

### Project Status

Project status is a string field in the database, but it's not directly editable through the UI. Instead, it's set automatically:

- New projects are assigned the status "Preparation"
- Status changes are managed programmatically based on project lifecycle events

### Project Structure

The project structure is hierarchical:

1. **Project**: The top-level entity
2. **Project Groups**: Organizational units within a project, associated with product groups
3. **Phases**: Individual work items within a group

This structure allows for flexible organization of project work and alignment with product offerings.

### Client Search

The client search functionality uses a custom implementation:

1. User types in the search box
2. AJAX request is sent to the server after a short delay
3. Results are displayed in a dropdown
4. User selects a client, which populates a hidden input field

This approach provides a better user experience than a simple dropdown for large numbers of clients.

## Conclusion

The Projects module is a comprehensive system for managing projects throughout their lifecycle. It provides a flexible structure for organizing project work, integrates with other modules for a cohesive user experience, and implements appropriate security measures to protect sensitive data.

