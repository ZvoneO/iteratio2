import requests

try:
    response = requests.get('http://127.0.0.1:5000/projects/create')
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        html = response.text
        
        # Check if this is a login page
        if 'login' in html.lower():
            print("This appears to be a login page. Authentication is required.")
        else:
            print("This does not appear to be a login page.")
        
        # Print the first 500 characters of the HTML
        print("\nFirst 500 characters of the HTML:")
        print(html[:500])
        
        # Check for specific elements
        print("\nChecking for specific elements:")
        elements_to_check = [
            '<form', 
            'id="status"', 
            'name="status"', 
            'class="form-select"',
            'Project Information',
            'Create Project'
        ]
        
        for element in elements_to_check:
            found = element in html
            print(f"'{element}': {'Found' if found else 'Not found'}")
    else:
        print(f"Failed to get the page: {response.status_code}")
except Exception as e:
    print(f"Error: {e}") 