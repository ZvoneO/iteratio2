from app import create_app
import logging
from flask import session
from app.models import User, db

logging.basicConfig(level=logging.DEBUG)

app = create_app()
app.config['DEBUG'] = True
app.config['TESTING'] = True
app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
app.config['SECRET_KEY'] = 'test-key'  # Set a secret key for the session

with app.app_context():
    # Get the admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print("Admin user not found. Creating one...")
        admin = User(username='admin', email='admin@example.com')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()
        print(f"Created admin user with ID {admin.id}")
    else:
        print(f"Found admin user with ID {admin.id}")

with app.test_client() as client:
    # First, log in
    login_response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin'
    }, follow_redirects=True)
    
    print(f"Login status code: {login_response.status_code}")
    print(f"Login response: {login_response.data.decode('utf-8')[:200]}...")
    
    # Check if we're logged in
    with client.session_transaction() as sess:
        print(f"Session after login: {sess}")
    
    # Now try to access the groups page
    groups_response = client.get('/catalog/groups', follow_redirects=True)
    print(f"Groups status code: {groups_response.status_code}")
    print(f"Groups response: {groups_response.data.decode('utf-8')[:200]}...") 