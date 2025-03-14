from app import create_app, db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    
    print('Columns in projects table:')
    for column in inspector.get_columns('projects'):
        print(f"  {column['name']}: {column['type']}")
    
    print('\nColumns in project_phases table:')
    for column in inspector.get_columns('project_phases'):
        print(f"  {column['name']}: {column['type']}")
    
    print('\nForeign keys in projects table:')
    for fk in inspector.get_foreign_keys('projects'):
        print(f"  {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    print('\nForeign keys in project_phases table:')
    for fk in inspector.get_foreign_keys('project_phases'):
        print(f"  {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}") 