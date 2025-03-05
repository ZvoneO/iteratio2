from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from ..models import db, ProductService, ProductGroup
from functools import wraps

catalog_bp = Blueprint('catalog', __name__, url_prefix='/catalog')

# Custom decorator for manager-only routes
def manager_required(f):
    """
    Decorator for routes that require manager privileges.
    Redirects to catalog list if user is not a manager or admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or (current_user.role != 'Admin' and current_user.role != 'Manager'):
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('catalog.list_products'))
        return f(*args, **kwargs)
    return decorated_function

@catalog_bp.route('/')
@login_required
def list_products():
    """Display a list of all products and services."""
    products = ProductService.query.all()
    return render_template('catalog/list.html', products=products)

@catalog_bp.route('/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_product():
    """
    Handle product creation.
    
    GET: Display product creation form
    POST: Process product creation form submission
    """
    # Get product groups for dropdown
    groups = ProductGroup.query.all()
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        type = request.form.get('type')
        group_id = request.form.get('group_id')
        
        # Validate form data
        if not name or not type or not group_id:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('catalog.create_product'))
        
        # Create new product
        new_product = ProductService(
            name=name,
            description=description,
            type=type,
            group_id=group_id
        )
        
        # Add product to database
        db.session.add(new_product)
        db.session.commit()
        
        flash('Product/Service created successfully.', 'success')
        return redirect(url_for('catalog.list_products'))
    
    return render_template('catalog/create.html', groups=groups)

@catalog_bp.route('/edit/<int:product_id>', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_product(product_id):
    """
    Handle product editing.
    
    GET: Display product edit form
    POST: Process product edit form submission
    """
    product = ProductService.query.get_or_404(product_id)
    
    # Get product groups for dropdown
    groups = ProductGroup.query.all()
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        type = request.form.get('type')
        group_id = request.form.get('group_id')
        
        # Validate form data
        if not name or not type or not group_id:
            flash('All required fields must be filled.', 'danger')
            return redirect(url_for('catalog.edit_product', product_id=product_id))
        
        # Update product
        product.name = name
        product.description = description
        product.type = type
        product.group_id = group_id
        
        db.session.commit()
        
        flash('Product/Service updated successfully.', 'success')
        return redirect(url_for('catalog.list_products'))
    
    return render_template('catalog/edit.html', product=product, groups=groups)

@catalog_bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
@manager_required
def delete_product(product_id):
    """Handle product deletion."""
    product = ProductService.query.get_or_404(product_id)
    
    # Check if product is used in any projects or templates
    if product.projects or product.templates:
        flash('Cannot delete product/service that is used in projects or templates.', 'danger')
        return redirect(url_for('catalog.list_products'))
    
    db.session.delete(product)
    db.session.commit()
    
    flash('Product/Service deleted successfully.', 'success')
    return redirect(url_for('catalog.list_products'))

@catalog_bp.route('/view/<int:product_id>')
@login_required
def view_product(product_id):
    """Display product details."""
    product = ProductService.query.get_or_404(product_id)
    return render_template('catalog/view.html', product=product)

@catalog_bp.route('/search')
@login_required
def search_products():
    """Search for products by name or description."""
    query = request.args.get('query', '')
    
    if query:
        # Search for products matching the query
        products = ProductService.query.filter(
            (ProductService.name.ilike(f'%{query}%')) | 
            (ProductService.description.ilike(f'%{query}%'))
        ).all()
    else:
        products = []
    
    # If AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify([{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'type': p.type,
            'group': p.group.name if p.group else None
        } for p in products])
    
    # Otherwise, render template
    return render_template('catalog/search.html', products=products, query=query)

# Product Group Routes

@catalog_bp.route('/groups')
@login_required
def list_groups():
    """Display a list of all product groups."""
    groups = ProductGroup.query.all()
    return render_template('catalog/groups/list.html', groups=groups)

@catalog_bp.route('/groups/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_group():
    """
    Handle product group creation.
    
    GET: Display group creation form
    POST: Process group creation form submission
    """
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        
        # Validate form data
        if not name:
            flash('Group name is required.', 'danger')
            return redirect(url_for('catalog.create_group'))
        
        # Check if group already exists
        if ProductGroup.query.filter_by(name=name).first():
            flash('A group with this name already exists.', 'danger')
            return redirect(url_for('catalog.create_group'))
        
        # Create new group
        new_group = ProductGroup(
            name=name,
            description=description
        )
        
        # Add group to database
        db.session.add(new_group)
        db.session.commit()
        
        flash('Product group created successfully.', 'success')
        return redirect(url_for('catalog.list_groups'))
    
    return render_template('catalog/groups/create.html')

@catalog_bp.route('/groups/edit/<int:group_id>', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_group(group_id):
    """
    Handle product group editing.
    
    GET: Display group edit form
    POST: Process group edit form submission
    """
    group = ProductGroup.query.get_or_404(group_id)
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        
        # Validate form data
        if not name:
            flash('Group name is required.', 'danger')
            return redirect(url_for('catalog.edit_group', group_id=group_id))
        
        # Check if group name already exists (excluding current group)
        existing_group = ProductGroup.query.filter_by(name=name).first()
        if existing_group and existing_group.id != group_id:
            flash('A group with this name already exists.', 'danger')
            return redirect(url_for('catalog.edit_group', group_id=group_id))
        
        # Update group
        group.name = name
        group.description = description
        
        db.session.commit()
        
        flash('Product group updated successfully.', 'success')
        return redirect(url_for('catalog.list_groups'))
    
    return render_template('catalog/groups/edit.html', group=group)

@catalog_bp.route('/groups/delete/<int:group_id>', methods=['POST'])
@login_required
@manager_required
def delete_group(group_id):
    """Handle product group deletion."""
    group = ProductGroup.query.get_or_404(group_id)
    
    # Check if group has products
    if group.products:
        flash('Cannot delete group with associated products.', 'danger')
        return redirect(url_for('catalog.list_groups'))
    
    db.session.delete(group)
    db.session.commit()
    
    flash('Product group deleted successfully.', 'success')
    return redirect(url_for('catalog.list_groups'))

# TODO: Add routes for product filtering by group
# TODO: Add routes for product import/export
