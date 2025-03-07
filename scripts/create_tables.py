import sqlite3
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

def create_tables():
    """
    Create tables directly using SQLite commands.
    """
    # Get the Flask app to access the instance path
    app = create_app()
    
    # Ensure the instance directory exists
    os.makedirs(app.instance_path, exist_ok=True)
    
    # Connect to the database in the instance directory
    db_path = os.path.join(app.instance_path, 'app.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the consultants table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consultants (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        name VARCHAR(50) NOT NULL,
        surname VARCHAR(50) NOT NULL,
        full_name VARCHAR(100) NOT NULL,
        email VARCHAR(120),
        phone_number VARCHAR(20),
        availability_days_per_month INTEGER,
        status VARCHAR(20),
        start_date DATE,
        end_date DATE,
        notes TEXT,
        calendar_name VARCHAR(100),
        created_at DATETIME,
        updated_at DATETIME,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create the expertise_categories table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS expertise_categories (
        id INTEGER PRIMARY KEY,
        name VARCHAR(100) NOT NULL UNIQUE,
        description TEXT,
        created_at DATETIME,
        updated_at DATETIME
    )
    ''')
    
    # Create the consultant_expertise table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS consultant_expertise (
        id INTEGER PRIMARY KEY,
        consultant_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        rating INTEGER NOT NULL,
        notes TEXT,
        created_at DATETIME,
        updated_at DATETIME,
        FOREIGN KEY (consultant_id) REFERENCES consultants (id) ON DELETE CASCADE,
        FOREIGN KEY (category_id) REFERENCES expertise_categories (id) ON DELETE CASCADE
    )
    ''')
    
    # Commit the changes
    conn.commit()
    
    # Insert sample data
    try:
        # Check if users table exists and has data
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            # Get the first user ID
            cursor.execute("SELECT id FROM users LIMIT 1")
            user_id = cursor.fetchone()[0]
            
            # Insert a sample consultant if none exists
            cursor.execute("SELECT COUNT(*) FROM consultants")
            if cursor.fetchone()[0] == 0:
                cursor.execute('''
                INSERT INTO consultants (
                    user_id, name, surname, full_name, email, phone_number,
                    availability_days_per_month, status, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id, 'John', 'Doe', 'John Doe', 'john.doe@example.com',
                    '123-456-7890', 20, 'Active', 'Sample consultant'
                ))
                print("Inserted sample consultant")
            
            # Insert sample expertise categories if none exist
            cursor.execute("SELECT COUNT(*) FROM expertise_categories")
            if cursor.fetchone()[0] == 0:
                categories = ['Java', 'Python', 'JavaScript', 'DevOps', 'Database', 'Cloud']
                for category in categories:
                    cursor.execute('''
                    INSERT INTO expertise_categories (name) VALUES (?)
                    ''', (category,))
                print("Inserted sample expertise categories")
            
            # Get consultant ID
            cursor.execute("SELECT id FROM consultants LIMIT 1")
            consultant_id = cursor.fetchone()[0]
            
            # Get category IDs
            cursor.execute("SELECT id, name FROM expertise_categories LIMIT 3")
            categories = cursor.fetchall()
            
            # Insert sample consultant expertise if none exists
            cursor.execute("SELECT COUNT(*) FROM consultant_expertise")
            if cursor.fetchone()[0] == 0 and categories:
                for category_id, category_name in categories:
                    rating = 5 if category_name == 'Java' else 4 if category_name == 'Python' else 3
                    cursor.execute('''
                    INSERT INTO consultant_expertise (
                        consultant_id, category_id, rating, notes
                    ) VALUES (?, ?, ?, ?)
                    ''', (
                        consultant_id, category_id, rating, f'Expertise in {category_name}'
                    ))
                print("Inserted sample consultant expertise")
    except sqlite3.Error as e:
        print(f"Error inserting sample data: {e}")
    
    # Commit the changes
    conn.commit()
    
    # Close the connection
    conn.close()
    
    print("Tables created successfully")

if __name__ == "__main__":
    create_tables() 