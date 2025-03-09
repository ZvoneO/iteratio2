from app import create_app, db
from app.models import List, ListItem

app = create_app()

with app.app_context():
    # Check if ProjectStatusList exists
    project_statuses_list = List.query.filter_by(name='ProjectStatusList').first()
    
    if project_statuses_list:
        print(f"Found existing ProjectStatusList with ID: {project_statuses_list.id}")
        
        # Check existing items
        existing_items = ListItem.query.filter_by(list_id=project_statuses_list.id).all()
        print(f"Found {len(existing_items)} existing items:")
        for item in existing_items:
            print(f"  ID: {item.id}, Value: {item.value}, Order: {item.order}")
        
        # Ask if we should delete existing items
        if existing_items:
            print("\nDeleting existing items...")
            for item in existing_items:
                db.session.delete(item)
            db.session.commit()
            print("Existing items deleted.")
    else:
        # Create new ProjectStatusList
        project_statuses_list = List(name='ProjectStatusList', description='Project Status Options')
        db.session.add(project_statuses_list)
        db.session.commit()
        print(f"Created new ProjectStatusList with ID: {project_statuses_list.id}")
    
    # Add default statuses
    default_statuses = ['Preparation', 'Initiation', 'Planning', 'Implementation', 'Closure', 'Paid', 'One-Time']
    
    print("\nAdding default statuses...")
    for i, status in enumerate(default_statuses):
        list_item = ListItem(list_id=project_statuses_list.id, value=status, order=i)
        db.session.add(list_item)
    
    db.session.commit()
    print("Default statuses added.")
    
    # Verify the items were added
    updated_items = ListItem.query.filter_by(list_id=project_statuses_list.id).order_by(ListItem.order).all()
    print(f"\nVerified {len(updated_items)} items in ProjectStatusList:")
    for item in updated_items:
        print(f"  ID: {item.id}, Value: {item.value}, Order: {item.order}")
    
    print("\nUpdate completed successfully!") 