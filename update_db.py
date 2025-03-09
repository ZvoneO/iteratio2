"""
Direct database update script.
This script updates the database schema and migrates the expertise data.
"""

from app import create_app, db
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import text
import logging
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_database():
    """
    Update the database schema and migrate the expertise data.
    """
    app = create_app()
    with app.app_context():
        conn = db.engine.connect()
        
        # Create a new table with the updated schema
        logger.info("Creating new consultant_expertise table...")
        conn.execute(text("""
        CREATE TABLE IF NOT EXISTS consultant_expertise_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            consultant_id INTEGER NOT NULL,
            product_group_id INTEGER,
            product_element_id INTEGER,
            rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
            notes TEXT DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (consultant_id) REFERENCES consultants (id) ON DELETE CASCADE,
            FOREIGN KEY (product_group_id) REFERENCES product_groups (id) ON DELETE CASCADE,
            FOREIGN KEY (product_element_id) REFERENCES product_elements (id) ON DELETE CASCADE
        )
        """))
        
        # Drop the existing table if it exists
        logger.info("Dropping old consultant_expertise table...")
        conn.execute(text("DROP TABLE IF EXISTS consultant_expertise"))
        
        # Rename the new table to the original name
        logger.info("Renaming new table to consultant_expertise...")
        conn.execute(text("ALTER TABLE consultant_expertise_new RENAME TO consultant_expertise"))
        
        # Commit the schema changes
        conn.commit()
        
        # Migrate the expertise data
        logger.info("Migrating expertise data from JSON to new table...")
        
        # We'll use direct SQL to migrate the data to avoid model loading issues
        # Get all consultants with expertise data
        result = conn.execute(text("SELECT id, custom_data FROM consultants WHERE custom_data IS NOT NULL"))
        consultants = result.fetchall()
        logger.info(f"Found {len(consultants)} consultants to process")
        
        migrated_count = 0
        skipped_count = 0
        
        for consultant in consultants:
            consultant_id = consultant[0]
            custom_data_str = consultant[1]
            
            # Parse the JSON data
            try:
                if isinstance(custom_data_str, str):
                    custom_data = json.loads(custom_data_str)
                else:
                    custom_data = custom_data_str
                
                if not custom_data or 'expertise' not in custom_data:
                    logger.info(f"Consultant {consultant_id} has no expertise data, skipping")
                    skipped_count += 1
                    continue
                
                expertise_data = custom_data['expertise']
                logger.info(f"Processing consultant {consultant_id} with {len(expertise_data)} expertise entries")
                
                for key, exp_data in expertise_data.items():
                    # Skip if rating is not between 1 and 5
                    rating = exp_data.get('rating', 0)
                    if not (1 <= rating <= 5):
                        logger.info(f"Skipping expertise with invalid rating {rating}")
                        continue
                    
                    # Set the appropriate fields based on expertise type
                    product_group_id = 'NULL'
                    product_element_id = 'NULL'
                    
                    if exp_data['type'] == 'product_group':
                        product_group_id = exp_data['id']
                    elif exp_data['type'] == 'product_element':
                        product_element_id = exp_data['id']
                    
                    # Insert the expertise entry
                    notes = exp_data.get('notes', '')
                    # Escape single quotes in notes
                    notes = notes.replace("'", "''")
                    
                    conn.execute(text(f"""
                    INSERT INTO consultant_expertise 
                    (consultant_id, product_group_id, product_element_id, rating, notes)
                    VALUES 
                    ({consultant_id}, {product_group_id if product_group_id != 'NULL' else 'NULL'}, 
                    {product_element_id if product_element_id != 'NULL' else 'NULL'}, {rating}, '{notes}')
                    """))
                    
                    migrated_count += 1
                
                # Clear the expertise data from the custom_data field
                if 'expertise' in custom_data:
                    del custom_data['expertise']
                    # Escape single quotes in JSON
                    custom_data_json = json.dumps(custom_data).replace("'", "''")
                    conn.execute(text(f"""
                    UPDATE consultants 
                    SET custom_data = '{custom_data_json}'
                    WHERE id = {consultant_id}
                    """))
                    logger.info(f"Cleared expertise data from consultant {consultant_id}")
            except Exception as e:
                logger.error(f"Error processing consultant {consultant_id}: {str(e)}")
                continue
        
        # Commit the data changes
        conn.commit()
        logger.info(f"Migration completed: {migrated_count} expertise entries migrated, {skipped_count} consultants skipped")

if __name__ == "__main__":
    update_database() 