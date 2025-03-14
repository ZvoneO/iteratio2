"""
Utility functions for the application.
"""
from flask import current_app
from sqlalchemy.exc import SQLAlchemyError
from .models import Role, db
import logging
import os
import sys

def user_has_role(user, role_name):
    """
    Check if a user has a specific role.
    This function handles potential database issues and provides a fallback mechanism.
    
    Args:
        user: The user object to check
        role_name: The name of the role to check for
        
    Returns:
        bool: True if the user has the role, False otherwise
    """
    if not user or not user.is_authenticated:
        return False
    
    try:
        # Try the ORM approach first
        role = Role.query.filter_by(name=role_name).first()
        if role and role in user.roles:
            return True
            
        # If that doesn't work, try direct SQL
        if role:
            result = db.session.execute("""
                SELECT COUNT(*) FROM user_roles 
                WHERE user_id = :user_id AND role_id = :role_id
            """, {"user_id": user.id, "role_id": role.id}).scalar()
            return result > 0
            
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error checking role {role_name} for user {user.username}: {str(e)}")
        
        # Last resort: check username for admin
        if role_name == 'Admin' and user.username == 'admin':
            return True
    
    return False

def user_has_any_role(user, role_names):
    """
    Check if a user has any of the specified roles.
    
    Args:
        user: The user object to check
        role_names: A list of role names to check for
        
    Returns:
        bool: True if the user has any of the roles, False otherwise
    """
    if not user or not user.is_authenticated or not role_names:
        return False
    
    for role_name in role_names:
        if user_has_role(user, role_name):
            return True
    
    return False

def get_user_roles(user):
    """
    Get all roles for a user.
    This function handles potential database issues and provides a fallback mechanism.
    
    Args:
        user: The user object to get roles for
        
    Returns:
        list: A list of role names for the user
    """
    if not user or not user.is_authenticated:
        return []
    
    try:
        # Try the ORM approach first
        return [role.name for role in user.roles]
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error getting roles for user {user.username}: {str(e)}")
        
        # Try direct SQL
        try:
            results = db.session.execute("""
                SELECT r.name FROM roles r
                JOIN user_roles ur ON r.id = ur.role_id
                WHERE ur.user_id = :user_id
            """, {"user_id": user.id}).fetchall()
            return [row[0] for row in results]
        except SQLAlchemyError as e2:
            current_app.logger.error(f"Error getting roles via SQL for user {user.username}: {str(e2)}")
            
            # Last resort: if username is admin, return Admin role
            if user.username == 'admin':
                return ['Admin']
    
    return []

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Set up a logger for any module in the application.
    
    Args:
        name (str): Name of the logger
        log_file (str, optional): Path to the log file. If None, a default path will be used.
        level (int, optional): Logging level. Defaults to INFO.
        
    Returns:
        logging.Logger: Configured logger
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Check if logger already has handlers to avoid duplicates
    if logger.handlers:
        return logger
    
    # Create console handler (always works)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    
    # Add console handler to logger
    logger.addHandler(console_handler)
    
    # Try to set up file handler if possible
    try:
        # Create log directory if it doesn't exist
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        # Set default log file if not provided
        if log_file is None:
            log_file = os.path.join(log_dir, f'{name}.log')
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        
        # Add file handler to logger
        logger.addHandler(file_handler)
    except Exception as e:
        # If file logging fails, just log to console
        console_handler.setLevel(logging.DEBUG)  # Ensure we get all messages
        logger.warning(f"Could not set up file logging: {str(e)}. Logging to console only.")
    
    return logger 