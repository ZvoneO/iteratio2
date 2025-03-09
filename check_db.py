from app import create_app, db
from app.models import List, ListItem

app = create_app()

with app.app_context():
    print("All Lists:")
    lists = List.query.all()
    for l in lists:
        print(f"{l.id}: {l.name}")
    
    print("\nLooking for ProjectStatusList:")
    status_list = List.query.filter_by(name='ProjectStatusList').first()
    print(f"Found list: {status_list}")
    
    if status_list:
        print("\nItems in ProjectStatusList:")
        items = ListItem.query.filter_by(list_id=status_list.id).all()
        for item in items:
            print(f"{item.id}: {item.value}")
    else:
        print("\nLooking for Project Statuses:")
        status_list = List.query.filter_by(name='Project Statuses').first()
        print(f"Found list: {status_list}")
        
        if status_list:
            print("\nItems in Project Statuses:")
            items = ListItem.query.filter_by(list_id=status_list.id).all()
            for item in items:
                print(f"{item.id}: {item.value}") 