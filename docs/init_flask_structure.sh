#!/bin/bash

# Step 1: Navigate to the project directory
cd "$(dirname "$0")"

# Step 2: Create Flask modular structure
echo "Setting up Flask structure..."

mkdir -p app/routes app/templates app/static/css app/static/js
touch app/__init__.py app/models.py app/routes/__init__.py
touch app/routes/projects.py app/routes/clients.py app/routes/catalog.py app/routes/admin.py
touch app/templates/base.html app/templates/projects.html app/templates/clients.html app/templates/catalog.html app/templates/admin.html
touch app/static/css/style.css app/static/js/script.js

echo "Flask structure has been set up!"
