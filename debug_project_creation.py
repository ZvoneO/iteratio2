from app import create_app, db
from app.models import Project, List, ListItem, Client, User, ProductGroup
import traceback

app = create_app()

with app.app_context():
    try:
        # Print debug information about the project_statuses
        project_statuses_list = List.query.filter_by(name='ProjectStatusList').first()
        if project_statuses_list:
            print(f"ProjectStatusList found with ID: {project_statuses_list.id}")
            project_statuses = ListItem.query.filter_by(list_id=project_statuses_list.id).all()
            print(f"Found {len(project_statuses)} statuses:")
            for status in project_statuses:
                print(f"  ID: {status.id}, Value: {status.value}")
        else:
            print("ProjectStatusList not found")
        
        # Test creating a project with status_id
        print("\nTesting project creation with status_id...")
        
        # Get a client
        client = Client.query.first()
        if not client:
            print("No clients found in database")
        else:
            print(f"Using client: {client.id} - {client.name}")
        
        # Get a manager
        manager = User.query.first()
        if not manager:
            print("No users found in database")
        else:
            print(f"Using manager: {manager.id} - {manager.username}")
        
        # Get a status
        status = None
        if project_statuses:
            status = project_statuses[0]
            print(f"Using status: {status.id} - {status.value}")
        
        # Create a test project
        if client and manager and status:
            new_project = Project(
                name="Test Project",
                description="Test Description",
                client_id=client.id,
                manager_id=manager.id,
                start_date=None,
                end_date=None,
                status=status.value,
                status_id=status.id
            )
            
            # Try to add and commit
            db.session.add(new_project)
            db.session.commit()
            print(f"Project created successfully with ID: {new_project.id}")
            
            # Clean up
            db.session.delete(new_project)
            db.session.commit()
            print("Test project deleted")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(traceback.format_exc()) 