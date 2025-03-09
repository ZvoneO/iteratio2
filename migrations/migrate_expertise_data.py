"""
Migration script to migrate expertise data from JSON field to the new table.
This script migrates the existing expertise data from the custom_data JSON field
to the new consultant_expertise table.
"""

from app import create_app, db
from app.models import Consultant, ConsultantExpertise
from sqlalchemy.orm.attributes import flag_modified
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_expertise_data():
    """
    Migrate expertise data from the custom_data JSON field to the new consultant_expertise table.
    """
    app = create_app()
    with app.app_context():
        # Get all consultants
        consultants = Consultant.query.all()
        logger.info(f"Found {len(consultants)} consultants to process")
        
        migrated_count = 0
        skipped_count = 0
        
        for consultant in consultants:
            if not consultant.custom_data or 'expertise' not in consultant.custom_data:
                logger.info(f"Consultant {consultant.id} has no expertise data, skipping")
                skipped_count += 1
                continue
            
            logger.info(f"Processing consultant {consultant.id} with {len(consultant.custom_data['expertise'])} expertise entries")
            
            for key, exp_data in consultant.custom_data['expertise'].items():
                # Skip if rating is not between 1 and 5
                rating = exp_data.get('rating', 0)
                if not (1 <= rating <= 5):
                    logger.info(f"Skipping expertise with invalid rating {rating}")
                    continue
                
                # Create new expertise entry
                new_expertise = ConsultantExpertise(
                    consultant_id=consultant.id,
                    rating=rating,
                    notes=exp_data.get('notes', '')
                )
                
                # Set the appropriate field based on expertise type
                if exp_data['type'] == 'product_group':
                    new_expertise.product_group_id = exp_data['id']
                elif exp_data['type'] == 'product_element':
                    new_expertise.product_element_id = exp_data['id']
                
                db.session.add(new_expertise)
                migrated_count += 1
            
            # Clear the expertise data from the custom_data field
            if 'expertise' in consultant.custom_data:
                del consultant.custom_data['expertise']
                flag_modified(consultant, 'custom_data')
                logger.info(f"Cleared expertise data from consultant {consultant.id}")
        
        # Commit the changes
        db.session.commit()
        logger.info(f"Migration completed: {migrated_count} expertise entries migrated, {skipped_count} consultants skipped")

if __name__ == "__main__":
    migrate_expertise_data() 