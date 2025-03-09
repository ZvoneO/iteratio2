from app import create_app, db
from app.models import List, ListItem

app = create_app()

with app.app_context():
    project_statuses_list = List.query.filter_by(id=6).first()
    
    if project_statuses_list:
        print(f'ProjectStatusList ID: {project_statuses_list.id}, Name: {project_statuses_list.name}')
        
        statuses = ListItem.query.filter_by(list_id=project_statuses_list.id).all()
        print(f'Found {len(statuses)} statuses:')
        for status in statuses:
            print(f'  ID: {status.id}, Value: {status.value}, Order: {status.order}')
    else:
        print('ProjectStatusList not found') 