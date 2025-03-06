#!/bin/bash

# fix_python_env.sh - Script to fix Python environment issues
# This script addresses the "No module named 'encodings'" error by ensuring
# the correct Python interpreter is used

echo "Fixing Python environment issues..."

# 1. Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Virtual environment found. Activating..."
    source venv/bin/activate
else
    echo "No virtual environment found. Creating one..."
    python3 -m venv venv
    source venv/bin/activate
fi

# 2. Ensure PYTHONHOME and PYTHONPATH are unset to avoid conflicts
echo "Unsetting PYTHONHOME and PYTHONPATH to avoid conflicts..."
unset PYTHONHOME
unset PYTHONPATH

# 3. Install or reinstall required packages
echo "Reinstalling required packages..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    # Install basic Flask packages if requirements.txt doesn't exist
    pip install flask flask-sqlalchemy flask-login
fi

# 4. Create a wrapper script to run the application with the correct Python
echo "Creating a wrapper script to run the application..."
cat > run_app.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
unset PYTHONHOME
unset PYTHONPATH
python3 run.py
EOF

chmod +x run_app.sh

echo "Environment fix completed!"
echo "To run your application, use: ./run_app.sh" 