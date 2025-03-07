import sqlite3
import os
import shutil
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

def copy_db():
    """
    Copy the data from instance/app.db to app.db.
    """
    # Get the Flask app to access the instance path
    app = create_app()
    
    # Define the source and destination paths
    instance_db_path = os.path.join(app.instance_path, 'app.db')
    root_db_path = os.path.join(os.path.dirname(app.instance_path), 'app.db')
    
    # Check if the source file exists
    if not os.path.exists(instance_db_path):
        print(f"Error: {instance_db_path} does not exist")
        return
    
    # Backup the destination file if it exists
    if os.path.exists(root_db_path):
        backup_path = f"{root_db_path}.bak"
        shutil.copy2(root_db_path, backup_path)
        print(f"Backed up {root_db_path} to {backup_path}")
    
    # Copy the source file to the destination
    shutil.copy2(instance_db_path, root_db_path)
    print(f"Copied {instance_db_path} to {root_db_path}")

if __name__ == "__main__":
    copy_db() 