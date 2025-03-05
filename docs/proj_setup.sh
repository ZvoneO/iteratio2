#!/bin/bash

# Step 1: Install dependencies
echo "Updating package list and installing dependencies..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip sqlite3

# Step 2: Set up project directory and virtual environment
echo "Creating Flask project structure..."
mkdir resource_planner
cd resource_planner

echo "Initializing virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Step 3: Install Flask dependencies
echo "Installing Flask and required packages..."
pip install Flask Flask-SQLAlchemy Flask-Migrate Flask-Login

# Step 4: Create necessary project files
echo "Creating initial project files..."
mkdir app app/routes app/templates app/static
touch app/__init__.py app/models.py app/routes/__init__.py run.py config.py requirements.txt README.md

echo "Writing dependencies to requirements.txt..."
pip freeze > requirements.txt

echo "Setup complete! Activate your virtual environment with: source venv/bin/activate"
