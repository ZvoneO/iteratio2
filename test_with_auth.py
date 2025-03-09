import requests
from bs4 import BeautifulSoup

# Create a session to maintain cookies
session = requests.Session()

# First, get the login page to get the CSRF token
login_url = 'http://127.0.0.1:5000/login'
login_response = session.get(login_url)

# Check if login page is accessible
if login_response.status_code != 200:
    print(f"Login page not accessible: {login_response.status_code}")
    exit(1)

login_soup = BeautifulSoup(login_response.text, 'html.parser')

# Find the CSRF token
csrf_token = None
for input_tag in login_soup.find_all('input'):
    if input_tag.get('name') == 'csrf_token':
        csrf_token = input_tag.get('value')
        break

if not csrf_token:
    print("Could not find CSRF token on login page")
    exit(1)

# Login credentials
login_data = {
    'csrf_token': csrf_token,
    'email': 'admin@example.com',  # Replace with actual credentials
    'password': 'admin',  # Replace with actual credentials
    'remember': 'y'
}

# Submit login form
login_post_response = session.post(login_url, data=login_data)

# Check if login was successful
if login_post_response.url.endswith('/login'):
    print("Login failed. Check credentials.")
    exit(1)

print("Login successful!")

# Now access the create project page
create_url = 'http://127.0.0.1:5000/projects/create'
create_response = session.get(create_url)

# Check if we got the create project page
if 'Create Project' in create_response.text:
    print("Successfully accessed the create project page!")
    
    # Parse the HTML
    soup = BeautifulSoup(create_response.text, 'html.parser')
    
    # Find the status select
    status_select = soup.find('select', {'id': 'status'})
    
    if status_select:
        print("\nStatus Select Found!")
        
        # Count options
        options = status_select.find_all('option')
        print(f"Number of options: {len(options)}")
        
        # Print options
        print("\nOptions:")
        for option in options:
            print(f"  Value: '{option.get('value')}', Text: '{option.text.strip()}'")
    else:
        print("\nStatus Select Not Found!")
        
        # Check if there are any selects
        selects = soup.find_all('select')
        print(f"Number of selects found: {len(selects)}")
        
        if selects:
            print("\nSelect elements found:")
            for i, select in enumerate(selects):
                print(f"\nSelect {i+1}:")
                print(f"  ID: '{select.get('id')}'")
                print(f"  Name: '{select.get('name')}'")
                print(f"  Class: '{select.get('class')}'")
                
                # Count options
                options = select.find_all('option')
                print(f"  Number of options: {len(options)}")
else:
    print("Failed to access the create project page.")
    print("Page title:", BeautifulSoup(create_response.text, 'html.parser').title.text if BeautifulSoup(create_response.text, 'html.parser').title else "No title") 