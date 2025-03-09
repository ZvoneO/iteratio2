from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app as app
from flask_login import login_required, current_user
from ..models import db, ProductService, ProductGroup, ProductElement, Role, List
from functools import wraps
from ..utils import user_has_role as utils_user_has_role
from contextlib import contextmanager

catalog_bp = Blueprint('catalog', __name__, url_prefix='/catalog')

# Helper function to check if user has a specific role
def user_has_role(user, role_name):
    """Check if a user has a specific role."""
    return utils_user_has_role(user, role_name)

# Custom decorator for manager-only routes
def manager_required(f):
    """
    Decorator for routes that require manager privileges.
    Redirects to catalog list if user is not a manager or admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (user_has_role(current_user, 'Admin') or user_has_role(current_user, 'Manager') or current_user.username == 'admin'):
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('catalog.list_products'))
        return f(*args, **kwargs)
    return decorated_function

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

@catalog_bp.route('/')
@login_required
def list_products():
    """Display a list of all products and services."""
    products = ProductService.query.all()
    return render_template('catalog/list.html', products=products)

@catalog_bp.route('/product/<int:product_id>', methods=['GET', 'POST'])
@catalog_bp.route('/product/new', methods=['GET', 'POST'])
@login_required
@manager_required
def manage_product(product_id=None):
    """
    Handle product creation and editing.
    If product_id is provided, edit existing product.
    If product_id is None, create new product.
    """
    # Get product if editing, otherwise None
    product = ProductService.query.get_or_404(product_id) if product_id else None
    
    # Get product groups for dropdown
    groups = ProductGroup.query.all()
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            description = request.form.get('description')
            type = request.form.get('type')
            group_id = request.form.get('group_id')
            
            # Validate form data
            if not name or not type or not group_id:
                flash('All required fields must be filled.', 'danger')
                return redirect(url_for('catalog.manage_product', product_id=product_id))
            
            with db_transaction():
                if product:
                    # Update existing product
                    product.name = name
                    product.description = description
                    product.type = type
                    product.group_id = group_id
                else:
                    # Create new product
                    product = ProductService(
                        name=name,
                        description=description,
                        type=type,
                        group_id=group_id
                    )
                    db.session.add(product)
            
            flash(f'Product/Service {"updated" if product_id else "created"} successfully.', 'success')
            return redirect(url_for('catalog.view_product', product_id=product.id) if product_id else url_for('catalog.list_products'))
            
        except Exception as e:
            flash(f'Error {"updating" if product_id else "creating"} product: {str(e)}', 'danger')
            return redirect(url_for('catalog.manage_product', product_id=product_id))
    
    return render_template('catalog/product_form.html', product=product, groups=groups)

@catalog_bp.route('/view/<int:product_id>')
@login_required
def view_product(product_id):
    """Display product details."""
    try:
        product = ProductService.query.get_or_404(product_id)
        return render_template('catalog/view.html', product=product)
    except Exception as e:
        app.logger.error(f"Error viewing product {product_id}: {str(e)}")
        flash(f"Error loading product details: {str(e)}", 'danger')
        return redirect(url_for('catalog.list_products'))

@catalog_bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
@manager_required
def delete_product(product_id):
    """Handle product deletion."""
    try:
        product = ProductService.query.get_or_404(product_id)
        
        # Store the group_id for redirection after deletion
        group_id = product.group_id
        
        # Check if product is used in any projects or templates
        if hasattr(product, 'projects') and product.projects:
            flash('Cannot delete product/service that is used in projects.', 'danger')
            return redirect(url_for('catalog.list_products'))
        
        if hasattr(product, 'templates') and product.templates:
            flash('Cannot delete product/service that is used in templates.', 'danger')
            return redirect(url_for('catalog.list_products'))
        
        # Get the referrer to determine where to redirect after deletion
        referrer = request.referrer
        
        with db_transaction():
            db.session.delete(product)
        
        flash('Product/Service deleted successfully.', 'success')
        
        # If deleted from group page, redirect back to group page
        if referrer and 'groups/group' in referrer:
            return redirect(url_for('catalog.manage_group', group_id=group_id))
        else:
            return redirect(url_for('catalog.list_products'))
    except Exception as e:
        flash(f'Error deleting product: {str(e)}', 'danger')
        return redirect(url_for('catalog.list_products'))

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
    
    # Load elements for each group
    for group in groups:
        group.elements = ProductElement.query.filter_by(group_id=group.id).all()
    
    # Get phase durations list for reference
    phase_durations_list = List.query.filter_by(name='Phase Durations').first()
    phase_durations = {duration.id: duration.value for duration in phase_durations_list.items} if phase_durations_list else {}
    
    return render_template('catalog/groups/list.html', groups=groups, phase_durations=phase_durations)

@catalog_bp.route('/groups/group/<int:group_id>', methods=['GET', 'POST'])
@catalog_bp.route('/groups/group/new', methods=['GET', 'POST'])
@login_required
@manager_required
def manage_group(group_id=None):
    """
    Handle product group creation and editing.
    If group_id is provided, edit existing group.
    If group_id is None, create new group.
    """
    # Get group if editing, otherwise None
    group = ProductGroup.query.get_or_404(group_id) if group_id else None
    
    # Get phase durations list for dropdown
    phase_durations_list = List.query.filter_by(name='PhaseDuration').first()
    phase_durations = phase_durations_list.items if phase_durations_list else []
    
    # If editing, load the products and elements in this group
    products = []
    elements = []
    if group:
        products = ProductService.query.filter_by(group_id=group.id).all()
        elements = ProductElement.query.filter_by(group_id=group.id).all()
    
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name')
            description = request.form.get('description')
            duration_id = request.form.get('duration_id')
            
            # Get product elements data
            element_labels = request.form.getlist('element_label[]')
            element_activities = request.form.getlist('element_activity[]')
            
            # Validate form data
            if not name:
                flash('Group name is required.', 'danger')
                return redirect(url_for('catalog.manage_group', group_id=group_id))
            
            # Check if group name already exists (excluding current group)
            existing_group = ProductGroup.query.filter_by(name=name).first()
            if existing_group and (not group or existing_group.id != group.id):
                flash('A group with this name already exists.', 'danger')
                return redirect(url_for('catalog.manage_group', group_id=group_id))
            
            with db_transaction():
                if group:
                    # Update existing group
                    group.name = name
                    group.description = description
                    group.duration_id = duration_id if duration_id else None
                    
                    # Delete existing elements
                    ProductElement.query.filter_by(group_id=group.id).delete()
                else:
                    # Create new group
                    group = ProductGroup(
                        name=name,
                        description=description,
                        duration_id=duration_id if duration_id else None
                    )
                    db.session.add(group)
                    db.session.flush()  # Flush to get the group ID
                
                # Add new elements
                for i in range(len(element_labels)):
                    if element_labels[i] and element_activities[i]:  # Only add if both fields are filled
                        element = ProductElement(
                            label=element_labels[i],
                            activity=element_activities[i],
                            group_id=group.id
                        )
                        db.session.add(element)
            
            flash(f'Product group {"updated" if group_id else "created"} successfully.', 'success')
            return redirect(url_for('catalog.list_groups'))
            
        except Exception as e:
            flash(f'Error {"updating" if group_id else "creating"} group: {str(e)}', 'danger')
            return redirect(url_for('catalog.manage_group', group_id=group_id))
    
    return render_template('catalog/group_form.html', group=group, products=products, elements=elements, phase_durations=phase_durations)

@catalog_bp.route('/groups/delete/<int:group_id>', methods=['POST'])
@login_required
@manager_required
def delete_group(group_id):
    """Handle product group deletion."""
    try:
        group = ProductGroup.query.get_or_404(group_id)
        
        # Check if group has products
        if group.products:
            flash('Cannot delete group with associated products.', 'danger')
            return redirect(url_for('catalog.list_groups'))
        
        with db_transaction():
            db.session.delete(group)
        
        flash('Product group deleted successfully.', 'success')
        return redirect(url_for('catalog.list_groups'))
    except Exception as e:
        flash(f'Error deleting group: {str(e)}', 'danger')
        return redirect(url_for('catalog.list_groups'))

@catalog_bp.route('/groups/group/<int:group_id>/add_product', methods=['POST'])
@login_required
@manager_required
def add_product_to_group(group_id):
    """
    Handle adding a new product to a specific group directly from the group form.
    """
    try:
        # Get the group
        group = ProductGroup.query.get_or_404(group_id)
        
        # Get form data
        name = request.form.get('name')
        description = request.form.get('description')
        type = request.form.get('type')
        
        # Validate form data
        if not name or not type:
            flash('Product name and type are required.', 'danger')
            return redirect(url_for('catalog.manage_group', group_id=group_id))
        
        # Create new product
        with db_transaction():
            product = ProductService(
                name=name,
                description=description,
                type=type,
                group_id=group_id
            )
            db.session.add(product)
        
        flash(f'Product "{name}" added to group successfully.', 'success')
        return redirect(url_for('catalog.manage_group', group_id=group_id))
        
    except Exception as e:
        flash(f'Error adding product to group: {str(e)}', 'danger')
        return redirect(url_for('catalog.manage_group', group_id=group_id))

@catalog_bp.route('/groups/group/<int:group_id>/add_element', methods=['POST'])
@login_required
@manager_required
def add_element_to_group(group_id):
    """
    Handle adding a new element to a specific group via AJAX.
    """
    try:
        # Get the group
        group = ProductGroup.query.get_or_404(group_id)
        
        # Get form data
        label = request.form.get('label')
        activity = request.form.get('activity')
        
        # Validate form data
        if not label or not activity:
            return jsonify({'success': False, 'message': 'Label and activity are required.'})
        
        # Create new element
        with db_transaction():
            element = ProductElement(
                label=label,
                activity=activity,
                group_id=group_id
            )
            db.session.add(element)
            db.session.flush()  # Flush to get the element ID
        
        # Return success response with element ID
        return jsonify({
            'success': True, 
            'message': 'Element added successfully.',
            'element': {
                'id': element.id,
                'label': element.label,
                'activity': element.activity
            }
        })
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error adding element: {str(e)}'})

@catalog_bp.route('/groups/element/<int:element_id>/delete', methods=['POST'])
@login_required
@manager_required
def delete_element(element_id):
    """
    Handle deleting a product element via AJAX.
    """
    try:
        # Get the element
        element = ProductElement.query.get_or_404(element_id)
        group_id = element.group_id
        
        # Delete the element
        with db_transaction():
            db.session.delete(element)
        
        # Return success response
        return jsonify({'success': True, 'message': 'Element deleted successfully.'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error deleting element: {str(e)}'})

# TODO: Add routes for product filtering by group
# TODO: Add routes for product import/export
