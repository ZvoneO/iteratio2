from app import create_app
import logging
from flask_login import login_user
from app.models import User

logging.basicConfig(level=logging.DEBUG)

app = create_app()
app.config['DEBUG'] = True
app.config['TESTING'] = True

with app.app_context():
    # Get a user for testing
    user = User.query.filter_by(username='admin').first()
    
    with app.test_client() as client:
        with client.session_transaction() as sess:
            # Log in the user
            if user:
                sess['user_id'] = user.id
                sess['_fresh'] = True
        
        # Now try to access the groups page
        response = client.get('/catalog/groups')
        print(f"Status code: {response.status_code}")
        if response.status_code == 200:
            print("Success!")
        else:
            print(f"Response: {response.data.decode('utf-8')}") 