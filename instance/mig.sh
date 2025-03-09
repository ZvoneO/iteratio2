#!/usr/bin/env python3

import sqlite3
import json

# Connect to SQLite database
conn = sqlite3.connect("app.db")
cursor = conn.cursor()

# 1️⃣ Create the new `consultants_new` table **without** `custom_data`
cursor.execute("""
    CREATE TABLE IF NOT EXISTS consultants_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        availability_days_per_month INTEGER,
        status VARCHAR(20),
        start_date DATE,
        end_date DATE,
        notes TEXT,
        calendar_name VARCHAR(100),
        created_at DATETIME,
        updated_at DATETIME
    )
""")

# 2️⃣ Copy all consultant data (excluding `custom_data`)
cursor.execute("""
    INSERT INTO consultants_new (id, user_id, availability_days_per_month, status, start_date, end_date, notes, calendar_name, created_at, updated_at)
    SELECT id, user_id, availability_days_per_month, status, start_date, end_date, notes, calendar_name, created_at, updated_at FROM consultants
""")

# 3️⃣ Process expertise data from `custom_data` and insert it into `consultant_expertise`
cursor.execute("SELECT id, custom_data FROM consultants WHERE custom_data IS NOT NULL")
consultants = cursor.fetchall()

for consultant_id, custom_data_json in consultants:
    if custom_data_json:
        try:
            custom_data = json.loads(custom_data_json)  # Convert JSON string to dict
            expertise_data = custom_data.get("expertise", {})

            for key, exp in expertise_data.items():
                expertise_type = exp.get("type")
                item_id = int(exp.get("id"))
                rating = int(exp.get("rating", 0))
                notes = exp.get("notes", "")

                if rating > 0:  # Only store meaningful expertise
                    cursor.execute("""
                        INSERT INTO consultant_expertise (consultant_id, product_group_id, product_element_id, rating, notes)
                        VALUES (?, ?, ?, ?, ?)
                    """, (consultant_id,
                          item_id if expertise_type == "product_group" else None,
                          item_id if expertise_type == "product_element" else None,
                          rating, notes))

        except json.JSONDecodeError:
            print(f"❌ Skipping consultant {consultant_id}: Invalid JSON format.")

# Commit changes
conn.commit()
conn.close()

print("✅ Migration completed successfully! `custom_data` is now removed, and expertise is relational.")

