-- Create a new table with the updated schema
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
);

-- Drop the existing table if it exists
DROP TABLE IF EXISTS consultant_expertise;

-- Rename the new table to the original name
ALTER TABLE consultant_expertise_new RENAME TO consultant_expertise; 