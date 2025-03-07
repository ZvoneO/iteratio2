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
    Stores consultant details and availability information.
    """
    __tablename__ = 'consultants'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    surname = db.Column(db.String(50), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone_number = db.Column(db.String(20))
    availability_days_per_month = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='Active')  # Active, Inactive, On Leave
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    calendar_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    expertise = db.relationship('ConsultantExpertise', backref='consultant', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Consultant {self.full_name}>'

# Expertise categories for consultants
class ExpertiseCategory(db.Model):
    """
    Expertise categories for consultants.
    Defines different areas of expertise that consultants can have.
    """
    __tablename__ = 'expertise_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    consultant_expertise = db.relationship('ConsultantExpertise', backref='category', lazy=True)
    
    def __repr__(self):
        return f'<ExpertiseCategory {self.name}>'

# Consultant expertise mapping
class ConsultantExpertise(db.Model):
    """
    Consultant expertise mapping.
    Links consultants to expertise categories with ratings.
    """
    __tablename__ = 'consultant_expertise'
    
    id = db.Column(db.Integer, primary_key=True)
    consultant_id = db.Column(db.Integer, db.ForeignKey('consultants.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('expertise_categories.id', ondelete='CASCADE'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 rating
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ConsultantExpertise {self.consultant_id}-{self.category_id}>'

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = db.relationship('ProductService', secondary='project_products', lazy='subquery',
                              backref=db.backref('projects', lazy=True))
    
    def __repr__(self):
        return f'<Project {self.name}>'

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    products = db.relationship('ProductService', backref='group', lazy=True)
    
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
