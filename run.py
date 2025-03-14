"""
Entry point for the Resource Planning Application.
Run this file to start the Flask development server.
"""

from app import create_app
import os
import argparse
from config import config

# Create the Flask application
app = create_app(config[os.getenv('FLASK_ENV', 'production')])

if __name__ == '__main__':
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Run the Resource Planning Application')
    parser.add_argument('--port', type=int, default=int(os.environ.get('PORT', 5020)),
                        help='Port to run the application on (default: 5020)')
    args = parser.parse_args()
    
    # Run the Flask application
    app.run(host='0.0.0.0', port=args.port, debug=app.config['DEBUG'])

