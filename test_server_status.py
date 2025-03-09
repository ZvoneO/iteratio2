import requests

try:
    # Check if the server is running
    response = requests.get('http://127.0.0.1:5000/')
    print(f"Server status: {'Running' if response.status_code == 200 else 'Not running'}")
    print(f"Status code: {response.status_code}")
    
    # Check if the login page is accessible
    login_response = requests.get('http://127.0.0.1:5000/login')
    print(f"\nLogin page: {'Accessible' if login_response.status_code == 200 else 'Not accessible'}")
    print(f"Status code: {login_response.status_code}")
    
    # Check if the project creation page is accessible (will redirect to login)
    projects_response = requests.get('http://127.0.0.1:5000/projects/create')
    print(f"\nProject creation page: {'Accessible' if projects_response.status_code == 200 else 'Not accessible (may redirect to login)'}")
    print(f"Status code: {projects_response.status_code}")
    
    # Check if the debug_create route is accessible (will redirect to login)
    debug_response = requests.get('http://127.0.0.1:5000/projects/debug-create')
    print(f"\nDebug create route: {'Accessible' if debug_response.status_code == 200 else 'Not accessible (may redirect to login)'}")
    print(f"Status code: {debug_response.status_code}")
    
except Exception as e:
    print(f"Error: {e}") 