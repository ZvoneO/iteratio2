import requests
import json

try:
    response = requests.get('http://127.0.0.1:5000/projects/debug-create')
    print(f"Status code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\nDebug Info:")
        print(json.dumps(data, indent=2))
        
        # Check project statuses
        project_statuses = data.get('project_statuses', [])
        print(f"\nProject Statuses Count: {len(project_statuses)}")
        
        if project_statuses:
            print("\nProject Statuses:")
            for status in project_statuses:
                print(f"  ID: {status.get('id')}, Value: {status.get('value')}")
        else:
            print("\nNo project statuses found!")
    else:
        print(f"Failed to get debug info: {response.status_code}")
except Exception as e:
    print(f"Error: {e}") 