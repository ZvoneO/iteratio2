# AI Proposed Changes

Based on the cursor recommendations, here are proposed changes to improve the codebase:

## 1. Unify Consultant Forms

### Current Issues:
- Separate routes and templates for creating and editing consultants
- Duplicated code for form handling
- Inconsistent error handling

### Proposed Solution:
Create a unified form handler for consultants:

```python
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
            db.or_(
                Consultant.id == None,
                User.id == consultant.user_id
            )
        ).all()
    else:
        # For new consultants, only show users without consultant entries
        users = User.query.outerjoin(Consultant).filter(Consultant.id == None).all()
    
    # Get expertise categories
    categories = ExpertiseCategory.query.all()
    
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
                
                # Remove existing expertise
                ConsultantExpertise.query.filter_by(consultant_id=consultant.id).delete()
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
            
            # Process expertise
            for category in categories:
                rating = request.form.get(f'expertise_{category.id}')
                if rating:
                    expertise = ConsultantExpertise(
                        consultant_id=consultant.id,
                        category_id=category.id,
                        rating=int(rating),
                        notes=request.form.get(f'expertise_notes_{category.id}')
                    )
                    db.session.add(expertise)
            
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
                          categories=categories,
                          statuses=statuses)
```

### Create a Unified Template:

Create a new template `consultant_form.html` that handles both creation and editing:

```html
{% extends 'base.html' %}

{% block title %}{{ 'Edit' if consultant else 'Create' }} Consultant - Resource Planning Application{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col">
        <h1 class="h2">
            <i class="fas fa-user-tie"></i> {{ 'Edit' if consultant else 'Create' }} Consultant
        </h1>
    </div>
    <div class="col-auto">
        <a href="{{ url_for('consultants.list_consultants') }}" class="btn btn-outline-secondary">
            <i class="fas fa-arrow-left"></i> Back to Consultants
        </a>
    </div>
</div>

<div class="card shadow">
    <div class="card-header bg-white">
        <h5 class="mb-0">Consultant Information</h5>
    </div>
    <div class="card-body">
        <form method="POST" id="consultantForm">
            <div class="row mb-3">
                <div class="col-md-6">
                    <label for="user_id" class="form-label">User*</label>
                    <select class="form-select" id="user_id" name="user_id" required>
                        <option value="">Select User</option>
                        {% for user in users %}
                        <option value="{{ user.id }}" {% if consultant and consultant.user_id == user.id %}selected{% endif %}>
                            {{ user.first_name }} {{ user.last_name }} ({{ user.email }})
                        </option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-6">
                    <label for="status" class="form-label">Status*</label>
                    <select class="form-select" id="status" name="status" required>
                        {% for status in statuses %}
                        <option value="{{ status.value }}" {% if consultant and consultant.status == status.value %}selected{% endif %}>
                            {{ status.value }}
                        </option>
                        {% endfor %}
                    </select>
                </div>
            </div>
            
            <div class="row mb-3">
                <div class="col-md-6">
                    <label for="availability_days" class="form-label">Availability (days/month)*</label>
                    <input type="number" class="form-control" id="availability_days" name="availability_days" 
                           value="{{ consultant.availability_days_per_month if consultant else 0 }}" min="0" max="31" required>
                </div>
                <div class="col-md-6">
                    <label for="calendar_name" class="form-label">Calendar Name</label>
                    <input type="text" class="form-control" id="calendar_name" name="calendar_name" 
                           value="{{ consultant.calendar_name if consultant and consultant.calendar_name else '' }}">
                </div>
            </div>
            
            <div class="row mb-3">
                <div class="col-md-6">
                    <label for="start_date" class="form-label">Start Date</label>
                    <input type="date" class="form-control" id="start_date" name="start_date" 
                           value="{{ consultant.start_date.strftime('%Y-%m-%d') if consultant and consultant.start_date else '' }}">
                </div>
                <div class="col-md-6">
                    <label for="end_date" class="form-label">End Date</label>
                    <input type="date" class="form-control" id="end_date" name="end_date" 
                           value="{{ consultant.end_date.strftime('%Y-%m-%d') if consultant and consultant.end_date else '' }}">
                </div>
            </div>
            
            <div class="mb-3">
                <label for="notes" class="form-label">Notes</label>
                <textarea class="form-control" id="notes" name="notes" rows="3">{{ consultant.notes if consultant and consultant.notes else '' }}</textarea>
            </div>
            
            <h5 class="mt-4 mb-3">Expertise</h5>
            {% for category in categories %}
            <div class="card mb-3">
                <div class="card-header bg-light">
                    <h6 class="mb-0">{{ category.name }}</h6>
                </div>
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-6">
                            <label for="expertise_{{ category.id }}" class="form-label">Rating (1-5)</label>
                            <select class="form-select" id="expertise_{{ category.id }}" name="expertise_{{ category.id }}">
                                <option value="">Not Applicable</option>
                                {% for i in range(1, 6) %}
                                <option value="{{ i }}" 
                                    {% if consultant and consultant.expertise %}
                                        {% for exp in consultant.expertise %}
                                            {% if exp.category_id == category.id and exp.rating == i %}
                                                selected
                                            {% endif %}
                                        {% endfor %}
                                    {% endif %}
                                >
                                    {{ i }} - {{ ['Beginner', 'Basic', 'Intermediate', 'Advanced', 'Expert'][i-1] }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>
                        <div class="col-md-6">
                            <label for="expertise_notes_{{ category.id }}" class="form-label">Notes</label>
                            <input type="text" class="form-control" id="expertise_notes_{{ category.id }}" 
                                   name="expertise_notes_{{ category.id }}" 
                                   value="{% if consultant and consultant.expertise %}{% for exp in consultant.expertise %}{% if exp.category_id == category.id %}{{ exp.notes }}{% endif %}{% endfor %}{% endif %}">
                        </div>
                    </div>
                </div>
            </div>
            {% endfor %}
            
            <div class="d-grid gap-2 d-md-flex justify-content-md-end">
                <button type="submit" class="btn btn-primary">
                    {{ 'Update' if consultant else 'Create' }} Consultant
                </button>
                <a href="{{ url_for('consultants.list_consultants') }}" class="btn btn-secondary">Cancel</a>
            </div>
        </form>
    </div>
</div>
{% endblock %}

{% block extra_js %}
<script>
    document.addEventListener('DOMContentLoaded', function() {
        // Add any client-side validation or dynamic behavior here
    });
</script>
{% endblock %}
```

## 2. Improve Database Error Handling

### Current Issues:
- Inconsistent error handling in database operations
- Direct attribute access without fallbacks
- Missing type conversions for form inputs

### Proposed Solution:

Add a utility function for safe attribute access:

```python
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
```

Update the view_consultant function to use safe attribute access:

```python
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
```

## 3. Add JSON Field for Flexible Metadata

### Current Issues:
- Adding new consultant attributes requires schema changes
- Frequent migrations for minor data additions

### Proposed Solution:

Update the Consultant model to include a metadata JSON field:

```python
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
    metadata = db.Column(db.JSON, nullable=True)  # For flexible, evolving attributes
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    expertise = db.relationship('ConsultantExpertise', backref='consultant', lazy=True, cascade="all, delete-orphan")
```

Example usage in the manage_consultant function:

```python
# Store additional data in metadata
metadata = {}
if request.form.get('skills'):
    metadata['skills'] = request.form.get('skills').split(',')
if request.form.get('hourly_rate'):
    metadata['hourly_rate'] = float(request.form.get('hourly_rate'))
if request.form.get('preferred_clients'):
    metadata['preferred_clients'] = request.form.get('preferred_clients').split(',')

# Update or create consultant with metadata
if consultant:
    consultant.metadata = metadata
else:
    consultant = Consultant(
        # ... other fields ...
        metadata=metadata
    )
```

## 4. Implement Proper Transaction Management

### Current Issues:
- Inconsistent transaction handling
- Missing rollbacks in some error cases

### Proposed Solution:

Create a context manager for database transactions:

```python
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
```

Example usage in the delete_consultant function:

```python
@consultants_bp.route('/delete/<int:consultant_id>', methods=['POST'])
@login_required
@manager_required
def delete_consultant(consultant_id):
    """
    Handle consultant deletion.
    """
    try:
        # Get consultant
        consultant = Consultant.query.get_or_404(consultant_id)
        
        # Store user_id before deleting consultant
        user_id = consultant.user_id
        
        with db_transaction():
            # Delete consultant
            db.session.delete(consultant)
            
            # Check if the user should keep the Consultant role
            user = User.query.get(user_id)
            consultant_role = Role.query.filter_by(name='Consultant').first()
            
            if user and consultant_role:
                # Check if the user has other consultant entries
                other_consultants = Consultant.query.filter_by(user_id=user_id).count()
                
                # If this was the only consultant entry for this user, remove the Consultant role
                if other_consultants == 0 and consultant_role in user.roles:
                    user.roles.remove(consultant_role)
        
        flash('Consultant deleted successfully.', 'success')
        return redirect(url_for('consultants.list_consultants'))
    except Exception as e:
        flash(f'Error deleting consultant: {str(e)}', 'danger')
        return redirect(url_for('consultants.list_consultants'))
```

## Implementation Plan

1. Create the unified consultant form template
2. Implement the unified manage_consultant route
3. Add the safe_get_attr utility function
4. Update the Consultant model with a metadata field
5. Create the db_transaction context manager
6. Update all consultant routes to use these improvements
7. Test thoroughly to ensure backward compatibility
