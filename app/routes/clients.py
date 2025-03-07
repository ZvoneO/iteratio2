from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ..models import db, Client, List, ListItem, Project, Role
from functools import wraps
import csv
import io
import json
from ..utils import user_has_role as utils_user_has_role

clients_bp = Blueprint('clients', __name__, url_prefix='/clients')

# Helper function to check if user has a specific role
def user_has_role(user, role_name):
    """Check if a user has a specific role."""
    return utils_user_has_role(user, role_name)

# Custom decorator for manager-only routes
def manager_required(f):
    """
    Decorator for routes that require manager privileges.
    Redirects to clients list if user is not a manager or admin.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not (user_has_role(current_user, 'Admin') or user_has_role(current_user, 'Manager') or current_user.username == 'admin'):
            flash('You do not have permission to access this page.', 'danger')
            return redirect(url_for('clients.list_clients'))
        return f(*args, **kwargs)
    return decorated_function

@clients_bp.route('/')
@login_required
def list_clients():
    """Display a list of all clients."""
    # Get clients based on user role
    if user_has_role(current_user, 'Admin') or user_has_role(current_user, 'Manager'):
        # Admins and Managers see all clients
        clients = Client.query.all()
    elif user_has_role(current_user, 'Project Manager'):
        # Project Managers see clients with projects they manage
        client_ids = db.session.query(Project.client_id).filter_by(manager_id=current_user.id).distinct()
        clients = Client.query.filter(Client.id.in_(client_ids)).all()
    else:
        # Other users don't see any clients
        clients = []
    
    return render_template('clients/list.html', clients=clients)

@clients_bp.route('/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_client():
    """
    Handle client creation.
    
    GET: Display client creation form
    POST: Process client creation form submission
    """
    # Get countries for dropdown
    countries = ListItem.query.join(ListItem.list).filter(ListItem.list.has(name='Countries')).all()
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        address = request.form.get('address')
        city = request.form.get('city')
        country_id = request.form.get('country_id')
        
        # Validate form data
        if not name:
            flash('Client name is required.', 'danger')
            return redirect(url_for('clients.create_client'))
        
        # Create new client
        new_client = Client(
            name=name,
            address=address,
            city=city,
            country_id=country_id if country_id else None
        )
        
        # Add client to database
        db.session.add(new_client)
        db.session.commit()
        
        flash('Client created successfully.', 'success')
        return redirect(url_for('clients.list_clients'))
    
    return render_template('clients/create.html', countries=countries)

@clients_bp.route('/edit/<int:client_id>', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_client(client_id):
    """
    Handle client editing.
    
    GET: Display client edit form
    POST: Process client edit form submission
    """
    client = Client.query.get_or_404(client_id)
    
    # Get countries for dropdown
    countries = ListItem.query.join(ListItem.list).filter(ListItem.list.has(name='Countries')).all()
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        address = request.form.get('address')
        city = request.form.get('city')
        country_id = request.form.get('country_id')
        
        # Validate form data
        if not name:
            flash('Client name is required.', 'danger')
            return redirect(url_for('clients.edit_client', client_id=client_id))
        
        # Update client
        client.name = name
        client.address = address
        client.city = city
        client.country_id = country_id if country_id else None
        
        db.session.commit()
        
        flash('Client updated successfully.', 'success')
        return redirect(url_for('clients.list_clients'))
    
    return render_template('clients/edit.html', client=client, countries=countries)

@clients_bp.route('/delete/<int:client_id>', methods=['POST'])
@login_required
@manager_required
def delete_client(client_id):
    """Handle client deletion."""
    client = Client.query.get_or_404(client_id)
    
    # Check if client has projects
    if client.projects:
        flash('Cannot delete client with associated projects.', 'danger')
        return redirect(url_for('clients.list_clients'))
    
    db.session.delete(client)
    db.session.commit()
    
    flash('Client deleted successfully.', 'success')
    return redirect(url_for('clients.list_clients'))

@clients_bp.route('/view/<int:client_id>')
@login_required
def view_client(client_id):
    """Display client details."""
    client = Client.query.get_or_404(client_id)
    return render_template('clients/view.html', client=client)

@clients_bp.route('/import-csv', methods=['GET', 'POST'])
@login_required
@manager_required
def import_csv():
    """
    Handle client import from CSV file.
    
    GET: Display import form
    POST: Process CSV file upload
    """
    if request.method == 'POST':
        # Check if file was uploaded
        if 'csv_file' not in request.files:
            flash('No file selected.', 'danger')
            return redirect(url_for('clients.import_csv'))
        
        file = request.files['csv_file']
        
        # Check if file is empty
        if file.filename == '':
            flash('No file selected.', 'danger')
            return redirect(url_for('clients.import_csv'))
        
        # Check if file is CSV
        if not file.filename.endswith('.csv'):
            flash('File must be a CSV file.', 'danger')
            return redirect(url_for('clients.import_csv'))
        
        try:
            # Read CSV file
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            
            # Get countries for lookup
            countries = {country.value: country.id for country in 
                        ListItem.query.join(ListItem.list).filter(ListItem.list.has(name='Countries')).all()}
            
            # Process CSV rows
            clients_added = 0
            clients_skipped = 0
            
            for row in csv_reader:
                # Check if required fields are present
                if 'name' not in row or not row['name']:
                    clients_skipped += 1
                    continue
                
                # Check if client already exists
                if Client.query.filter_by(name=row['name']).first():
                    clients_skipped += 1
                    continue
                
                # Create new client
                new_client = Client(
                    name=row['name'],
                    address=row.get('address', ''),
                    city=row.get('city', '')
                )
                
                # Set country if provided and exists in database
                if 'country' in row and row['country'] in countries:
                    new_client.country_id = countries[row['country']]
                
                # Add client to database
                db.session.add(new_client)
                clients_added += 1
            
            db.session.commit()
            
            flash(f'Import complete: {clients_added} clients added, {clients_skipped} skipped.', 'success')
            return redirect(url_for('clients.list_clients'))
        except Exception as e:
            flash(f'Error importing clients: {str(e)}', 'danger')
            return redirect(url_for('clients.import_csv'))
    
    return render_template('clients/import_csv.html')

# TODO: Add routes for client projects
# TODO: Add routes for client contacts
