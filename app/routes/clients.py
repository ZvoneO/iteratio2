from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
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
    # Get search and filter parameters
    search = request.args.get('search', '')
    country_id = request.args.get('country', '')
    status = request.args.get('status', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Show 20 clients per page
    
    # Base query
    query = Client.query.options(db.joinedload(Client.country))
    
    # Apply filters
    if search:
        query = query.filter(Client.name.ilike(f'%{search}%'))
    
    if country_id:
        query = query.filter(Client.country_id == country_id)
        
    if status:
        if status == 'active':
            query = query.filter(Client.active == True)
        elif status == 'inactive':
            query = query.filter(Client.active == False)
    
    # Apply role-based filtering
    if user_has_role(current_user, 'Admin') or user_has_role(current_user, 'Manager'):
        # Admins and Managers see all clients
        filtered_query = query
    elif user_has_role(current_user, 'Project Manager'):
        # Project Managers see clients with projects they manage
        client_ids = db.session.query(Project.client_id).filter_by(manager_id=current_user.id).distinct()
        filtered_query = query.filter(Client.id.in_(client_ids))
    else:
        # Other users don't see any clients
        filtered_query = query.filter(Client.id == None)  # Empty result
    
    # Order by name and ensure fresh data
    filtered_query = filtered_query.order_by(Client.name).execution_options(synchronize_session="fetch")
    
    # Paginate the results
    pagination = filtered_query.paginate(page=page, per_page=per_page, error_out=False)
    clients = pagination.items
    
    # Debug log to verify client active status
    for client in clients:
        print(f"Client {client.id} - {client.name} - Active: {client.active}")
    
    # Get countries list for dropdown
    countries_list = List.query.filter_by(name='Countries').first()
    countries = countries_list.items if countries_list else []
    
    # Get sales persons list
    sales_list = List.query.filter_by(name='Sales').first()
    sales_persons = sales_list.items if sales_list else []
    
    # Get project managers (users with Project Manager role)
    pm_role = Role.query.filter_by(name='Project Manager').first()
    project_managers = pm_role.users if pm_role else []
    
    return render_template(
        'clients/list.html', 
        clients=clients,
        countries=countries,
        sales_persons=sales_persons,
        project_managers=project_managers,
        pagination=pagination
    )

@clients_bp.route('/create', methods=['GET', 'POST'])
@login_required
@manager_required
def create_client():
    """Create a new client."""
    # Get countries list for dropdown
    countries_list = List.query.filter_by(name='Countries').first()
    if countries_list:
        countries = countries_list.items
    else:
        countries = []
    
    # Get sales persons list
    sales_list = List.query.filter_by(name='Sales').first()
    if sales_list:
        sales_persons = sales_list.items
    else:
        sales_persons = []
    
    # Get industries list for dropdown
    industries_list = List.query.filter_by(id=5).first()
    if industries_list:
        industries = industries_list.items
    else:
        industries = []
    
    # Get project managers (users with Project Manager role)
    pm_role = Role.query.filter_by(name='Project Manager').first()
    if pm_role:
        project_managers = [user for user in pm_role.users]
    else:
        project_managers = []
    
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        address = request.form.get('address')
        city = request.form.get('city')
        country_id = request.form.get('country_id')
        sales_person = request.form.get('sales_person')
        project_manager = request.form.get('project_manager')
        industry = request.form.get('industry')
        active = True  # Default to active
        
        # Create new client
        new_client = Client(
            name=name,
            address=address,
            city=city,
            country_id=country_id if country_id else None,
            sales_person=sales_person,
            project_manager=project_manager,
            industry=industry,
            active=active
        )
        
        # Add to database
        db.session.add(new_client)
        db.session.commit()
        
        flash('Client created successfully!', 'success')
        return redirect(url_for('clients.list_clients'))
    
    return render_template('clients/create.html', 
                          countries=countries,
                          sales_persons=sales_persons,
                          project_managers=project_managers,
                          industries=industries)

@clients_bp.route('/edit/<int:client_id>', methods=['GET', 'POST'])
@login_required
@manager_required
def edit_client(client_id):
    """Edit an existing client."""
    # Get client
    client = Client.query.get_or_404(client_id)
    
    # Get countries list for dropdown
    countries_list = List.query.filter_by(name='Countries').first()
    if countries_list:
        countries = countries_list.items
    else:
        countries = []
    
    # Get sales persons list
    sales_list = List.query.filter_by(name='Sales').first()
    if sales_list:
        sales_persons = sales_list.items
    else:
        sales_persons = []
    
    # Get industries list for dropdown
    industries_list = List.query.filter_by(id=5).first()
    if industries_list:
        industries = industries_list.items
    else:
        industries = []
    
    # Get project managers (users with Project Manager role)
    pm_role = Role.query.filter_by(name='Project Manager').first()
    if pm_role:
        project_managers = [user for user in pm_role.users]
    else:
        project_managers = []
    
    if request.method == 'POST':
        # Check if it's an AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if is_ajax:
            # Get JSON data
            data = request.get_json()
            
            # Update client data
            client.name = data.get('name')
            client.address = data.get('address')
            client.city = data.get('city')
            client.country_id = data.get('country_id') if data.get('country_id') else None
            client.sales_person = data.get('sales_person')
            client.project_manager = data.get('project_manager')
            client.industry = data.get('industry')
            
            # Fix for active status - properly convert to boolean
            active_value = data.get('active')
            client.active = bool(active_value) if active_value is not None else True
            
            # Log the update for debugging
            print(f"AJAX updating client {client.id} - Active status: {client.active}, Raw value: {active_value}")
            
            try:
                # Save to database
                db.session.flush()  # Flush changes to the database
                db.session.commit()
                
                # Refresh the client object to ensure it reflects the latest changes
                db.session.refresh(client)
                print(f"After AJAX commit - Client {client.id} active status: {client.active}")
                
                return json.dumps({'success': True, 'message': 'Client updated successfully!'})
            except Exception as e:
                db.session.rollback()
                return json.dumps({'success': False, 'message': f'Error updating client: {str(e)}'})
        else:
            # Regular form submission
            client.name = request.form.get('name')
            client.address = request.form.get('address')
            client.city = request.form.get('city')
            client.country_id = request.form.get('country_id') if request.form.get('country_id') else None
            client.sales_person = request.form.get('sales_person')
            client.project_manager = request.form.get('project_manager')
            client.industry = request.form.get('industry')
            
            # Fix for active status - properly convert checkbox value to boolean
            client.active = 'active' in request.form and request.form.get('active') == 'on'
            
            # Log the update for debugging
            print(f"Updating client {client.id} - Active status: {client.active}")
            
            try:
                # Save to database
                db.session.flush()  # Flush changes to the database
                db.session.commit()
                
                # Refresh the client object to ensure it reflects the latest changes
                db.session.refresh(client)
                print(f"After commit - Client {client.id} active status: {client.active}")
                
                flash('Client updated successfully!', 'success')
                return redirect(url_for('clients.list_clients'))
            except Exception as e:
                db.session.rollback()
                flash(f'Error updating client: {str(e)}', 'danger')
                return redirect(url_for('clients.edit_client', client_id=client.id))
    
    return render_template('clients/edit.html', 
                          client=client, 
                          countries=countries,
                          sales_persons=sales_persons,
                          project_managers=project_managers,
                          industries=industries)

@clients_bp.route('/delete/<int:client_id>', methods=['POST'])
@login_required
@manager_required
def delete_client(client_id):
    """Handle client deletion."""
    client = Client.query.get_or_404(client_id)
    
    # Check if it's an AJAX request
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    
    # Check if client has projects
    if client.projects:
        if is_ajax:
            return json.dumps({'success': False, 'message': 'Cannot delete client with associated projects.'})
        else:
            flash('Cannot delete client with associated projects.', 'danger')
            return redirect(url_for('clients.list_clients'))
    
    try:
        # Delete the client
        db.session.delete(client)
        db.session.commit()
        
        if is_ajax:
            return json.dumps({'success': True, 'message': 'Client deleted successfully!'})
        else:
            flash('Client deleted successfully!', 'success')
            return redirect(url_for('clients.list_clients'))
    except Exception as e:
        db.session.rollback()
        
        if is_ajax:
            return json.dumps({'success': False, 'message': f'Error deleting client: {str(e)}'})
        else:
            flash(f'Error deleting client: {str(e)}', 'danger')
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

@clients_bp.route('/search', methods=['GET'])
@login_required
def search_clients():
    """
    Search for clients by name.
    Returns JSON with matching clients.
    """
    query = request.args.get('query', '')
    if len(query) < 2:
        return jsonify([])
    
    # Search for clients matching the query
    clients = Client.query.filter(Client.name.ilike(f'%{query}%')).limit(7).all()
    
    # Get sales list
    sales_list = List.query.filter_by(name='Sales').first()
    sales_items = []
    if sales_list:
        sales_items = ListItem.query.filter_by(list_id=sales_list.id).all()
        sales_items = [{'id': item.id, 'value': item.value} for item in sales_items]
    
    # Get project managers (users with Project Manager role)
    pm_role = Role.query.filter_by(name='Project Manager').first()
    project_managers = []
    if pm_role:
        project_managers = [{'id': user.id, 'name': f"{user.first_name} {user.last_name}"} for user in pm_role.users]
    
    # Format the results
    results = []
    for client in clients:
        client_data = {
            'id': client.id,
            'name': client.name,
            'address': client.address or '',
            'city': client.city or '',
            'country_id': client.country_id,
            'country': client.country.value if client.country else '',
            'sales_person': client.sales_person or '',
            'project_manager': client.project_manager or '',
            'industry': client.industry or '',
            'active': client.active
        }
        results.append(client_data)
    
    # Return client data along with sales and project manager options
    response = {
        'clients': results,
        'sales_items': sales_items,
        'project_managers': project_managers
    }
    
    return jsonify(response)

@clients_bp.route('/get/<int:client_id>', methods=['GET'])
@login_required
def get_client(client_id):
    """
    Get detailed information for a specific client.
    Returns JSON with client details.
    """
    client = Client.query.get_or_404(client_id)
    
    # Get sales list
    sales_list = List.query.filter_by(name='Sales').first()
    sales_items = []
    if sales_list:
        sales_items = ListItem.query.filter_by(list_id=sales_list.id).all()
        sales_items = [{'id': item.id, 'value': item.value} for item in sales_items]
    
    # Get project managers (users with Project Manager role)
    pm_role = Role.query.filter_by(name='Project Manager').first()
    project_managers = []
    if pm_role:
        project_managers = [{'id': user.id, 'name': f"{user.first_name} {user.last_name}"} for user in pm_role.users]
    
    # Format the client data
    client_data = {
        'id': client.id,
        'name': client.name,
        'address': client.address or '',
        'city': client.city or '',
        'country_id': client.country_id,
        'country': client.country.value if client.country else '',
        'sales_person': client.sales_person or '',
        'project_manager': client.project_manager or '',
        'industry': client.industry or '',
        'active': client.active
    }
    
    # Return client data along with sales and project manager options
    response = {
        'client': client_data,
        'sales_items': sales_items,
        'project_managers': project_managers
    }
    
    return jsonify(response)

# TODO: Add routes for client projects
# TODO: Add routes for client contacts
