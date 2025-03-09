from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# User model for authentication and role-based access control
class User(db.Model, UserMixin):
    """
    User model for authentication and role-based access control.
    Stores user credentials and profile information.
    """
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    consultants = db.relationship('Consultant', backref='user', lazy=True)
    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy=True))
    
    def __repr__(self):
        return f'<User {self.username}>'

# Consultant model for resource management
class Consultant(db.Model):
    """
    Consultant model for resource management.
    Stores consultant-specific information not available in the User model.
    """
    __tablename__ = 'consultants'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    availability_days_per_month = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='Active')  # Active, Inactive, On Leave
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    calendar_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    custom_data = db.Column(db.JSON, nullable=True)  # For flexible, evolving attributes
    
    # Relationships - updated to use expertise_entries instead of expertise
    expertise_entries = db.relationship('ConsultantExpertise', backref='consultant', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Consultant {self.user.first_name} {self.user.last_name}>'
    
    @property
    def full_name(self):
        """Get the consultant's full name from the associated user"""
        if self.user:
            return f"{self.user.first_name or ''} {self.user.last_name or ''}".strip()
        return ""
    
    @property
    def email(self):
        """Get the consultant's email from the associated user"""
        return self.user.email if self.user else None

# Expertise categories for consultants
class ExpertiseCategory(db.Model):
    """
    Expertise categories for consultants.
    Defines different areas of expertise that consultants can have.
    Note: This model is kept for historical purposes but is no longer used with the new expertise system.
    """
    __tablename__ = 'expertise_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # No relationships with ConsultantExpertise anymore
    
    def __repr__(self):
        return f'<ExpertiseCategory {self.name}>'

# Consultant expertise mapping
class ConsultantExpertise(db.Model):
    """
    Consultant expertise mapping.
    Links consultants to product groups and elements with ratings.
    Ensures only meaningful expertise (rating 1-5) is stored.
    """
    __tablename__ = 'consultant_expertise'
    
    id = db.Column(db.Integer, primary_key=True)
    consultant_id = db.Column(db.Integer, db.ForeignKey('consultants.id', ondelete='CASCADE'), nullable=False)
    product_group_id = db.Column(db.Integer, db.ForeignKey('product_groups.id', ondelete='CASCADE'), nullable=True)
    product_element_id = db.Column(db.Integer, db.ForeignKey('product_elements.id', ondelete='CASCADE'), nullable=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 rating, enforced by CHECK constraint
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - use existing relationship from Consultant model
    product_group = db.relationship('ProductGroup', backref=db.backref('expertise_entries', lazy=True))
    product_element = db.relationship('ProductElement', backref=db.backref('expertise_entries', lazy=True))
    
    def __repr__(self):
        if self.product_group_id:
            return f'<ConsultantExpertise {self.consultant_id}-Group:{self.product_group_id}>'
        else:
            return f'<ConsultantExpertise {self.consultant_id}-Element:{self.product_element_id}>'
            
    @property
    def item_name(self):
        """Get a formatted name for the expertise item."""
        if self.product_group_id and self.product_group:
            return self.product_group.name
        elif self.product_element_id and self.product_element:
            element_name = self.product_element.label
            if hasattr(self.product_element, 'group') and self.product_element.group:
                group_name = self.product_element.group.name
                return f"{element_name} ({group_name})"
            return element_name
        return "Unknown"

# Lists for dropdown values
class List(db.Model):
    """
    Lists for dropdown values.
    Stores categories of list items for various dropdowns in the application.
    """
    __tablename__ = 'lists'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    items = db.relationship('ListItem', backref='list', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<List {self.name}>'

# List items for dropdown values
class ListItem(db.Model):
    """
    List items for dropdown values.
    Stores individual items for dropdowns in the application.
    """
    __tablename__ = 'list_items'
    
    id = db.Column(db.Integer, primary_key=True)
    list_id = db.Column(db.Integer, db.ForeignKey('lists.id', ondelete='CASCADE'), nullable=False)
    value = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    clients = db.relationship('Client', backref='country', lazy=True)
    
    def __repr__(self):
        return f'<ListItem {self.value}>'

# Client model
class Client(db.Model):
    """
    Client model.
    Stores client information for projects.
    """
    __tablename__ = 'clients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    city = db.Column(db.String(100))
    country_id = db.Column(db.Integer, db.ForeignKey('list_items.id'))
    sales_person = db.Column(db.String(100))  # Sales person name
    project_manager = db.Column(db.String(100))  # Project manager name
    industry = db.Column(db.String(100))  # Industry field
    active = db.Column(db.Boolean, default=True)  # Active status
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    projects = db.relationship('Project', backref='client', lazy=True)
    project_templates = db.relationship('ProjectTemplate', backref='client', lazy=True)
    
    def __repr__(self):
        return f'<Client {self.name}>'

# Project template model
class ProjectTemplate(db.Model):
    """
    Project template model.
    Stores templates for standardized project creation.
    """
    __tablename__ = 'project_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    phases = db.relationship('PhaseTemplate', backref='template', lazy=True, cascade="all, delete-orphan")
    projects = db.relationship('Project', backref='template', lazy=True)
    products = db.relationship('ProductService', secondary='template_products', lazy='subquery',
                              backref=db.backref('templates', lazy=True))
    
    def __repr__(self):
        return f'<ProjectTemplate {self.name}>'

# Phase template model
class PhaseTemplate(db.Model):
    """
    Phase template model.
    Stores phases for project templates.
    """
    __tablename__ = 'phase_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('project_templates.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)
    duration_days = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PhaseTemplate {self.name}>'

# Project model
class Project(db.Model):
    """
    Project model.
    Stores project information and status.
    """
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    template_id = db.Column(db.Integer, db.ForeignKey('project_templates.id'))
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    manager_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20))  # Active, Completed, On Hold
    status_id = db.Column(db.Integer, db.ForeignKey('list_items.id'))
    industry_id = db.Column(db.Integer, db.ForeignKey('list_items.id'))
    profit_center_id = db.Column(db.Integer, db.ForeignKey('list_items.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = db.relationship('ProductService', secondary='project_products', lazy='subquery',
                              backref=db.backref('projects', lazy=True))
    groups = db.relationship('ProjectGroup', backref='project', lazy=True, cascade="all, delete-orphan", order_by="ProjectGroup.order")
    industry = db.relationship('ListItem', foreign_keys=[industry_id])
    profit_center = db.relationship('ListItem', foreign_keys=[profit_center_id])
    status_item = db.relationship('ListItem', foreign_keys=[status_id])
    manager = db.relationship('User', foreign_keys=[manager_id])
    
    def __repr__(self):
        return f'<Project {self.name}>'

# Project Group model
class ProjectGroup(db.Model):
    """
    Project Group model.
    Represents a group of project phases (Level I in the project hierarchy).
    """
    __tablename__ = 'project_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    product_group_id = db.Column(db.Integer, db.ForeignKey('product_groups.id'), nullable=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    phases = db.relationship('ProjectPhase', backref='group', lazy=True, cascade="all, delete-orphan", order_by="ProjectPhase.order")
    product_group = db.relationship('ProductGroup', foreign_keys=[product_group_id])
    
    def __repr__(self):
        return f'<ProjectGroup {self.product_group.name if self.product_group else "Unknown"} for Project {self.project_id}>'

# Project Phase model
class ProjectPhase(db.Model):
    """
    Project Phase model.
    Represents a phase within a project group (Level II in the project hierarchy).
    """
    __tablename__ = 'project_phases'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('project_groups.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration_id = db.Column(db.Integer, db.ForeignKey('list_items.id'))
    online = db.Column(db.Boolean, default=False)
    order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    duration = db.relationship('ListItem', foreign_keys=[duration_id])
    
    def __repr__(self):
        return f'<ProjectPhase {self.name} for Group {self.group_id}>'

# Product group model
class ProductGroup(db.Model):
    """
    Product group model.
    Categorizes products and services.
    """
    __tablename__ = 'product_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration_id = db.Column(db.Integer, db.ForeignKey('list_items.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = db.relationship('ProductService', backref='group', lazy=True)
    elements = db.relationship('ProductElement', backref='group', lazy=True, cascade='all, delete-orphan')
    duration = db.relationship('ListItem', foreign_keys=[duration_id])
    
    def __repr__(self):
        return f'<ProductGroup {self.name}>'

# Product/Service model
class ProductService(db.Model):
    """
    Product/Service model.
    Stores products and services that can be used in projects.
    """
    __tablename__ = 'products_services'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(20), nullable=False)  # Product or Service
    group_id = db.Column(db.Integer, db.ForeignKey('product_groups.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProductService {self.name}>'

# Product Element model
class ProductElement(db.Model):
    """
    Product Element model.
    Stores label and activity pairs for product groups.
    """
    __tablename__ = 'product_elements'
    
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(100), nullable=False)
    activity = db.Column(db.String(255), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('product_groups.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProductElement {self.label}>'

# Association table for template-product relationship
template_products = db.Table('template_products',
    db.Column('template_id', db.Integer, db.ForeignKey('project_templates.id', ondelete='CASCADE'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products_services.id', ondelete='CASCADE'), primary_key=True)
)

# Association table for project-product relationship
project_products = db.Table('project_products',
    db.Column('project_id', db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True),
    db.Column('product_id', db.Integer, db.ForeignKey('products_services.id', ondelete='CASCADE'), primary_key=True)
)

# Association table for User and Role
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'), primary_key=True)
)

# Role model for defining user roles
class Role(db.Model):
    """
    Role model for defining user roles.
    """
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    description = db.Column(db.String(100))

# TODO: Add Task model for project task management
# TODO: Add Document model for file attachments
# TODO: Add Calendar/Event models for consultant scheduling
