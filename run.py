"""
Entry point for the Resource Planning Application.
Run this file to start the Flask development server.
"""

from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    # Get port from environment variable or use default 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Run the Flask application
    app.run(host='0.0.0.0', port=port, debug=True)
