from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from ..models import db, Consultant, User, ConsultantExpertise, Role, user_roles, List, ListItem, ProductGroup, ProductElement
from functools import wraps
import json
import os
import logging
import traceback
from ..utils import user_has_role as utils_user_has_role, get_user_roles, setup_logger
from datetime import datetime, date
from contextlib import contextmanager
from sqlalchemy.orm.attributes import flag_modified

consultants_bp = Blueprint('consultants', __name__, url_prefix='/consultants')

# Initialize logger
logger = setup_logger('consultants', level=logging.DEBUG)
# Also log to admin log for important events
admin_logger = logging.getLogger('admin')

# Helper function to check if user has a specific role
def user_has_role(user, role_name):
    """Check if a user has a specific role."""
    return utils_user_has_role(user, role_name)

# Custom decorator for manager-only routes
def manager_required(f):
    """
    Decorator for routes that require manager privileges.
    Redirects to consultants list if user is not a manager or admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (user_has_role(current_user, 'Admin') or user_has_role(current_user, 'Manager') or current_user.username == 'admin'):
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('consultants.list_consultants'))
        return f(*args, **kwargs)
    return decorated_function

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

def ensure_consultant_entries():
    """
    Ensure that every user with the Consultant role has a corresponding entry in the consultants table.
    This helps maintain consistency between the role assignments and the consultant records.
    """
    # Get the Consultant role
    consultant_role = Role.query.filter_by(name='Consultant').first()
    if not consultant_role:
        return
    
    # Get all users with the Consultant role
    consultant_users = db.session.query(User).join(user_roles).filter(user_roles.c.role_id == consultant_role.id).all()
    
    # For each user with the Consultant role, check if they have a consultant entry
    for user in consultant_users:
        # Check if the user already has a consultant entry
        existing_consultant = Consultant.query.filter_by(user_id=user.id).first()
        if not existing_consultant:
            # Create a new consultant entry for the user
            new_consultant = Consultant(
                user_id=user.id,
                status='Active',
                availability_days_per_month=0
            )
            db.session.add(new_consultant)
    
    # Commit the changes
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error ensuring consultant entries: {e}")

def ensure_consultant_status_list():
    """
    Ensure that the 'Consultant Status' list exists in the database.
    This helps maintain consistency in the application.
    """
    # Check if the list already exists
    status_list = List.query.filter_by(name='Consultant Status').first()
    if not status_list:
        try:
            # Create the list
            status_list = List(name='Consultant Status', description='Status options for consultants')
            db.session.add(status_list)
            db.session.flush()  # This assigns the ID without committing the transaction
            
            # Add default status options
            statuses = ['Active', 'Inactive', 'On Leave']
            for i, status in enumerate(statuses):
                item = ListItem(value=status, display_order=i+1, list_id=status_list.id)
                db.session.add(item)
            
            # Commit all changes
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error creating Consultant Status list: {e}")
            # Provide fallback behavior
            return None
    
    return status_list

@consultants_bp.route('/')
@login_required
def list_consultants():
    """
    Display a list of all consultants.
    """
    # Ensure consultant entries for users with Consultant role
    ensure_consultant_entries()
    
    # Ensure the Consultant Status list exists
    status_list = ensure_consultant_status_list()
    
    # Get search parameters
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    expertise_filter = request.args.get('expertise', '')
    
    # Base query
    query = Consultant.query.join(User)
    
    # Apply filters
    if search:
        # Search in user data
        user_match = db.or_(
            User.first_name.ilike(f'%{search}%'),
            User.last_name.ilike(f'%{search}%'),
            User.email.ilike(f'%{search}%')
        )
        
        # Get consultants with matching expertise
        expertise_consultants = []
        if search:
            # Search in product groups
            product_groups = ProductGroup.query.filter(
                ProductGroup.name.ilike(f'%{search}%')
            ).all()
            
            # Search in product elements
            product_elements = ProductElement.query.filter(
                ProductElement.label.ilike(f'%{search}%')
            ).all()
            
            # Get consultant IDs with matching expertise
            if product_groups:
                for group in product_groups:
                    expertise_entries = ConsultantExpertise.query.filter_by(product_group_id=group.id).all()
                    for entry in expertise_entries:
                        if entry.consultant_id not in expertise_consultants:
                            expertise_consultants.append(entry.consultant_id)
            
            if product_elements:
                for element in product_elements:
                    expertise_entries = ConsultantExpertise.query.filter_by(product_element_id=element.id).all()
                    for entry in expertise_entries:
                        if entry.consultant_id not in expertise_consultants:
                            expertise_consultants.append(entry.consultant_id)
        
        # Combine user match and expertise match
        if expertise_consultants:
            query = query.filter(
                db.or_(
                    user_match,
                    Consultant.id.in_(expertise_consultants)
                )
            )
        else:
            query = query.filter(user_match)
    
    # Apply status filter
    if status_filter:
        query = query.filter(Consultant.status == status_filter)
    
    # Apply expertise filter
    if expertise_filter:
        expertise_consultants = []
        
        # Check if it's a product group or element filter
        if expertise_filter.startswith('group_'):
            # Filter by product group
            group_id = expertise_filter.split('_')[1]
            expertise_entries = ConsultantExpertise.query.filter_by(product_group_id=group_id).all()
            for entry in expertise_entries:
                if entry.consultant_id not in expertise_consultants:
                    expertise_consultants.append(entry.consultant_id)
        elif expertise_filter.startswith('element_'):
            # Filter by product element
            element_id = expertise_filter.split('_')[1]
            expertise_entries = ConsultantExpertise.query.filter_by(product_element_id=element_id).all()
            for entry in expertise_entries:
                if entry.consultant_id not in expertise_consultants:
                    expertise_consultants.append(entry.consultant_id)
        
        # Apply the expertise filter
        if expertise_consultants:
            query = query.filter(Consultant.id.in_(expertise_consultants))
        else:
            # If no consultants match the expertise filter, return an empty list
            query = query.filter(Consultant.id == -1)  # This will return no results
    
    # Get all consultants
    consultants = query.all()
    
    # Get all product groups for expertise selection
    product_groups = ProductGroup.query.all()
    
    # Get product elements for filtering
    product_elements = ProductElement.query.all()
    
    # Get all statuses for filter dropdown
    if status_list:
        statuses = status_list.items
    else:
        # Fallback to default statuses if the list doesn't exist
        statuses = [
            {'value': 'Active'},
            {'value': 'Inactive'},
            {'value': 'On Leave'}
        ]
    
    # Get user roles for permission checks
    user_roles = get_user_roles(current_user)
    
    return render_template('consultants/list.html', 
                          consultants=consultants, 
                          statuses=statuses,
                          product_groups=product_groups,
                          product_elements=product_elements,
                          user_roles=user_roles)

@consultants_bp.route('/consultant/<int:consultant_id>', methods=['GET', 'POST'])
@consultants_bp.route('/consultant/new', methods=['GET', 'POST'])
@login_required
@manager_required
def manage_consultant(consultant_id=None):
    """
    Handle consultant creation and editing.
    If consultant_id is provided, edit existing consultant.
    If consultant_id is None, create new consultant.
    """
    # Get consultant if editing, otherwise None
    consultant = Consultant.query.get_or_404(consultant_id) if consultant_id else None
    
    # Get users for dropdown - include current consultant's user if editing
    if consultant:
        users = User.query.outerjoin(Consultant).filter(
            db.or_(Consultant.id == None, User.id == consultant.user_id)
        ).all()
    else:
        # For new consultants, only show users without consultant entries
        users = User.query.outerjoin(Consultant).filter(Consultant.id == None).all()
    
    # Get product groups for expertise selection
    product_groups = ProductGroup.query.all()
    
    # Get consultant statuses
    status_list = ensure_consultant_status_list()
    if status_list:
        statuses = status_list.items
    else:
        # Fallback to default statuses if the list doesn't exist
        statuses = [
            {'value': 'Active'},
            {'value': 'Inactive'},
            {'value': 'On Leave'}
        ]
    
    if request.method == 'POST':
        try:
            # Get form data
            user_id = request.form.get('user_id')
            availability_days = request.form.get('availability_days')
            status = request.form.get('status')
            start_date_str = request.form.get('start_date')
            end_date_str = request.form.get('end_date')
            notes = request.form.get('notes')
            calendar_name = request.form.get('calendar_name')
            
            # Validate form data
            if not user_id:
                flash('User selection is required.', 'danger')
                return redirect(url_for('consultants.manage_consultant', consultant_id=consultant_id))
            
            # Convert date strings to Python date objects
            start_date = None
            if start_date_str and start_date_str.strip():
                try:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid start date format. Please use YYYY-MM-DD.', 'danger')
                    return redirect(url_for('consultants.manage_consultant', consultant_id=consultant_id))
            
            end_date = None
            if end_date_str and end_date_str.strip():
                try:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid end date format. Please use YYYY-MM-DD.', 'danger')
                    return redirect(url_for('consultants.manage_consultant', consultant_id=consultant_id))
            
            # Process consultant data
            if consultant:
                # Update existing consultant
                consultant.user_id = user_id
                consultant.availability_days_per_month = int(availability_days) if availability_days else 0
                consultant.status = status
                consultant.start_date = start_date
                consultant.end_date = end_date
                consultant.notes = notes if notes and notes.lower() != 'none' else None
                consultant.calendar_name = calendar_name if calendar_name and calendar_name.lower() != 'none' else None
            else:
                # Create new consultant
                consultant = Consultant(
                    user_id=user_id,
                    availability_days_per_month=int(availability_days) if availability_days else 0,
                    status=status,
                    start_date=start_date,
                    end_date=end_date,
                    notes=notes if notes and notes.lower() != 'none' else None,
                    calendar_name=calendar_name if calendar_name and calendar_name.lower() != 'none' else None
                )
                db.session.add(consultant)
                db.session.flush()  # Get ID without committing
            
            # Ensure the user has the Consultant role
            user = User.query.get(user_id)
            consultant_role = Role.query.filter_by(name='Consultant').first()
            if user and consultant_role and consultant_role not in user.roles:
                user.roles.append(consultant_role)
            
            # Note: Expertise is now handled through the API, not through this form
            
            db.session.commit()
            
            flash(f'Consultant {"updated" if consultant_id else "created"} successfully.', 'success')
            return redirect(url_for('consultants.view_consultant', consultant_id=consultant.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error {"updating" if consultant_id else "creating"} consultant: {str(e)}', 'danger')
            return redirect(url_for('consultants.manage_consultant', consultant_id=consultant_id))
    
    return render_template('consultants/consultant_form.html', 
                          consultant=consultant, 
                          users=users, 
                          product_groups=product_groups,
                          statuses=statuses)

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

@consultants_bp.route('/view/<int:consultant_id>')
@login_required
def view_consultant(consultant_id):
    """
    Display consultant details.
    """
    try:
        # Get consultant
        consultant = Consultant.query.get_or_404(consultant_id)
        
        # Use safe attribute access
        user = safe_get_attr(consultant, 'user')
        first_name = safe_get_attr(user, 'first_name', 'Unknown')
        last_name = safe_get_attr(user, 'last_name', 'Unknown')
        email = safe_get_attr(user, 'email', 'No email')
        
        return render_template('consultants/view.html', 
                              consultant=consultant,
                              user_first_name=first_name,
                              user_last_name=last_name,
                              user_email=email)
    except Exception as e:
        app.logger.error(f"Error viewing consultant {consultant_id}: {str(e)}")
        flash(f"Error loading consultant details: {str(e)}", 'danger')
        return redirect(url_for('consultants.list_consultants'))

@consultants_bp.route('/delete/<int:consultant_id>', methods=['POST'])
@login_required
@manager_required
def delete_consultant(consultant_id):
    """
    Handle consultant deletion.
    """
    # Get consultant
    consultant = Consultant.query.get_or_404(consultant_id)
    
    # Store user_id before deleting consultant
    user_id = consultant.user_id
    
    # Delete consultant
    db.session.delete(consultant)
    
    # Check if the user should keep the Consultant role
    # If they have other consultant entries, keep the role
    user = User.query.get(user_id)
    consultant_role = Role.query.filter_by(name='Consultant').first()
    
    if user and consultant_role:
        # Check if the user has other consultant entries
        other_consultants = Consultant.query.filter_by(user_id=user_id).count()
        
        # If this was the only consultant entry for this user, remove the Consultant role
        if other_consultants == 0 and consultant_role in user.roles:
            user.roles.remove(consultant_role)
    
    db.session.commit()
    
    flash('Consultant deleted successfully.', 'success')
    return redirect(url_for('consultants.list_consultants'))

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

@consultants_bp.route('/expertise/update', methods=['POST'])
@login_required
@manager_required
def update_consultant_expertise():
    """
    Update consultant expertise via AJAX.
    Uses the ConsultantExpertise table to store expertise data.
    Only stores meaningful expertise (rating 1-5).
    """
    try:
        data = request.json
        consultant_id = data.get('consultant_id')
        expertise_type = data.get('expertise_type')  # 'product_group' or 'product_element'
        item_id = data.get('item_id')
        rating = data.get('rating', 0)  # Default to 0 (clear) if not provided
        notes = data.get('notes', '')
        
        # Log the request data
        logger.info(f"Updating expertise for consultant {consultant_id}: {data}")
        admin_logger.info(f"Consultant expertise update for ID {consultant_id}, {expertise_type} {item_id}")
        
        if not all([consultant_id, expertise_type, item_id]):
            error_msg = f'Missing required parameters: consultant_id={consultant_id}, expertise_type={expertise_type}, item_id={item_id}'
            logger.error(error_msg)
            admin_logger.error(error_msg)
            return jsonify({'success': False, 'message': 'Missing required parameters'}), 400
        
        try:
            # Get consultant
            consultant = Consultant.query.get_or_404(consultant_id)
            
            # Get item name for logging
            item_name = "Unknown"
            if expertise_type == 'product_group':
                group = ProductGroup.query.get(item_id)
                if group:
                    item_name = safe_get_attr(group, 'name', f"Group {item_id}")
            elif expertise_type == 'product_element':
                element = ProductElement.query.get(item_id)
                if element:
                    item_name = element.label
                    # Also include the group name if available
                    if hasattr(element, 'group') and element.group:
                        group_name = safe_get_attr(element.group, 'name', "Unknown Group")
                        item_name = f"{item_name} ({group_name})"
            
            # Handle different expertise types
            if expertise_type == 'product_group' or expertise_type == 'product_element':
                # Find existing expertise entry if any
                if expertise_type == 'product_group':
                    existing_expertise = ConsultantExpertise.query.filter_by(
                        consultant_id=consultant_id,
                        product_group_id=item_id,
                        product_element_id=None
                    ).first()
                else:  # product_element
                    existing_expertise = ConsultantExpertise.query.filter_by(
                        consultant_id=consultant_id,
                        product_element_id=item_id,
                        product_group_id=None
                    ).first()
                
                if int(rating) == 0:
                    # Remove expertise if rating is 0
                    if existing_expertise:
                        logger.info(f"Removing expertise for {item_name} (ID: {item_id})")
                        admin_logger.info(f"Removing expertise for {item_name} (ID: {item_id})")
                        db.session.delete(existing_expertise)
                elif 1 <= int(rating) <= 5:
                    # Update or create expertise with valid rating (1-5)
                    if existing_expertise:
                        # Update existing entry
                        existing_expertise.rating = int(rating)
                        existing_expertise.notes = notes
                        existing_expertise.updated_at = datetime.utcnow()
                        logger.info(f"Updating expertise for {item_name} (ID: {item_id}) to rating {rating}")
                        admin_logger.info(f"Updating expertise for {item_name} (ID: {item_id}) to rating {rating}")
                    else:
                        # Create new entry
                        new_expertise = ConsultantExpertise(
                            consultant_id=consultant_id,
                            rating=int(rating),
                            notes=notes
                        )
                        
                        # Set the appropriate field based on expertise type
                        if expertise_type == 'product_group':
                            new_expertise.product_group_id = item_id
                        else:  # product_element
                            new_expertise.product_element_id = item_id
                        
                        db.session.add(new_expertise)
                        logger.info(f"Creating new expertise for {item_name} (ID: {item_id}) with rating {rating}")
                        admin_logger.info(f"Creating new expertise for {item_name} (ID: {item_id}) with rating {rating}")
                else:
                    # Invalid rating
                    error_msg = f"Invalid rating value: {rating}. Must be between 1 and 5."
                    logger.error(error_msg)
                    admin_logger.error(error_msg)
                    return jsonify({'success': False, 'message': error_msg}), 400
            
            # Save changes
            db.session.commit()
            
            success_msg = f"Expertise updated for consultant {consultant_id}"
            if int(rating) == 0:
                success_msg = f"Expertise removed for {item_name}"
            else:
                success_msg = f"Expertise set to {rating} stars for {item_name}"
                
            logger.info(success_msg)
            admin_logger.info(success_msg)
            return jsonify({'success': True, 'message': success_msg})
        
        except Exception as inner_e:
            db.session.rollback()
            error_msg = f"Error processing expertise update: {str(inner_e)}"
            stack_trace = traceback.format_exc()
            logger.error(f"{error_msg}\n{stack_trace}")
            admin_logger.error(f"{error_msg}\n{stack_trace}")
            return jsonify({'success': False, 'message': 'Error updating expertise', 'error_details': str(inner_e)}), 500
    
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error updating expertise for consultant: {str(e)}"
        stack_trace = traceback.format_exc()
        logger.error(f"{error_msg}\n{stack_trace}")
        admin_logger.error(f"{error_msg}\n{stack_trace}")
        return jsonify({
            'success': False, 
            'message': 'Error updating expertise. Please try again.',
            'error_details': str(e)
        }), 500

@consultants_bp.route('/expertise/list/<int:consultant_id>', methods=['GET'])
@login_required
def list_consultant_expertise(consultant_id):
    """
    Get all expertise for a consultant in JSON format.
    Uses the ConsultantExpertise table to retrieve expertise data.
    """
    try:
        consultant = Consultant.query.get_or_404(consultant_id)
        expertise_list = []
        
        # Get all expertise entries for the consultant
        expertise_entries = ConsultantExpertise.query.filter_by(consultant_id=consultant_id).all()
        
        for entry in expertise_entries:
            if entry.product_group_id:
                # This is a product group expertise
                expertise_list.append({
                    'type': 'product_group',
                    'id': entry.product_group_id,
                    'name': entry.item_name,
                    'rating': entry.rating,
                    'notes': entry.notes or ''
                })
            elif entry.product_element_id:
                # This is a product element expertise
                expertise_list.append({
                    'type': 'product_element',
                    'id': entry.product_element_id,
                    'name': entry.item_name,
                    'rating': entry.rating,
                    'notes': entry.notes or ''
                })
        
        return jsonify({
            'success': True,
            'expertise': expertise_list
        })
    
    except Exception as e:
        error_msg = f"Error listing expertise for consultant: {str(e)}"
        stack_trace = traceback.format_exc()
        logger.error(f"{error_msg}\n{stack_trace}")
        return jsonify({'success': False, 'message': str(e)}), 500

@consultants_bp.route('/update/<int:consultant_id>', methods=['POST'])
@login_required
@manager_required
def update_consultant_details(consultant_id):
    """
    Update consultant details via AJAX.
    """
    try:
        data = request.json
        status = data.get('status')
        availability_days = data.get('availability_days')
        calendar_name = data.get('calendar_name')
        notes = data.get('notes')
        
        # Log the request data
        logger.info(f"Updating consultant {consultant_id} with data: {data}")
        admin_logger.info(f"Consultant update request for ID {consultant_id}")
        
        # Get consultant
        consultant = Consultant.query.get_or_404(consultant_id)
        
        # Track if any changes were made
        changes_made = False
        
        # Update consultant details
        if status and status != consultant.status:
            logger.info(f"Updating status from '{consultant.status}' to '{status}'")
            consultant.status = status
            changes_made = True
        
        if availability_days is not None:
            try:
                availability_days = int(availability_days)
                if availability_days != consultant.availability_days_per_month:
                    logger.info(f"Updating availability from {consultant.availability_days_per_month} to {availability_days}")
                    consultant.availability_days_per_month = availability_days
                    changes_made = True
            except ValueError as e:
                error_msg = f"Invalid availability value: {availability_days}"
                logger.error(error_msg)
                admin_logger.error(error_msg)
                return jsonify({'success': False, 'message': error_msg}), 400
        
        if calendar_name is not None:
            new_calendar_name = calendar_name.strip() if calendar_name.strip() else None
            if new_calendar_name != consultant.calendar_name:
                logger.info(f"Updating calendar name from '{consultant.calendar_name}' to '{new_calendar_name}'")
                consultant.calendar_name = new_calendar_name
                changes_made = True
        
        if notes is not None:
            new_notes = notes.strip() if notes.strip() else None
            if new_notes != consultant.notes:
                logger.info(f"Updating notes for consultant {consultant_id}")
                consultant.notes = new_notes
                changes_made = True
        
        # Save changes
        if changes_made:
            db.session.commit()
            success_msg = f"Consultant {consultant_id} updated successfully"
            logger.info(success_msg)
            admin_logger.info(success_msg)
            return jsonify({'success': True, 'message': success_msg})
        else:
            logger.info(f"No changes detected for consultant {consultant_id}")
            return jsonify({'success': True, 'message': 'No changes were made'})
    
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error updating consultant {consultant_id}: {str(e)}"
        stack_trace = traceback.format_exc()
        logger.error(f"{error_msg}\n{stack_trace}")
        admin_logger.error(f"{error_msg}\n{stack_trace}")
        return jsonify({
            'success': False, 
            'message': 'Error updating consultant. Please try again.',
            'error_details': str(e)
        }), 500 