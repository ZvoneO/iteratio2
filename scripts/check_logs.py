#!/usr/bin/env python3
"""
Log Analyzer Script

This script analyzes log files to help diagnose issues in the application.
It can filter logs by level, module, and time range.
"""

import os
import re
import sys
import argparse
from datetime import datetime, timedelta
import json

# ANSI color codes for terminal output
COLORS = {
    'RESET': '\033[0m',
    'RED': '\033[91m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'PURPLE': '\033[95m',
    'CYAN': '\033[96m',
    'WHITE': '\033[97m',
}

# Log level colors
LEVEL_COLORS = {
    'DEBUG': COLORS['BLUE'],
    'INFO': COLORS['GREEN'],
    'WARNING': COLORS['YELLOW'],
    'ERROR': COLORS['RED'],
    'CRITICAL': COLORS['PURPLE'],
}

def parse_log_line(line):
    """Parse a log line into its components."""
    # Example log line: 2023-04-15 12:34:56,789 - admin - INFO - User updated successfully
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (\w+) - (.+)'
    match = re.match(pattern, line)
    
    if match:
        timestamp_str, module, level, message = match.groups()
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
            return {
                'timestamp': timestamp,
                'module': module,
                'level': level,
                'message': message.strip()
            }
        except ValueError:
            return None
    return None

def filter_logs(log_file, level=None, module=None, hours=None, contains=None, json_output=False):
    """Filter logs based on criteria."""
    if not os.path.exists(log_file):
        print(f"Log file not found: {log_file}")
        return []
    
    filtered_logs = []
    time_threshold = None
    
    if hours:
        time_threshold = datetime.now() - timedelta(hours=hours)
    
    with open(log_file, 'r') as f:
        current_entry = []
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a new log entry or continuation
            parsed = parse_log_line(line)
            
            if parsed:
                # If we have a previous entry, add it to filtered logs if it matches criteria
                if current_entry and current_entry[0]:
                    filtered_logs.append(current_entry[0])
                
                # Start a new entry
                current_entry = [parsed]
                
                # Apply filters
                if level and parsed['level'] != level.upper():
                    current_entry = [None]  # Mark as not matching
                    continue
                
                if module and parsed['module'] != module:
                    current_entry = [None]  # Mark as not matching
                    continue
                
                if time_threshold and parsed['timestamp'] < time_threshold:
                    current_entry = [None]  # Mark as not matching
                    continue
                
                if contains and contains.lower() not in parsed['message'].lower():
                    current_entry = [None]  # Mark as not matching
                    continue
            else:
                # This is a continuation of the previous entry
                if current_entry and current_entry[0]:
                    current_entry[0]['message'] += f"\n{line}"
        
        # Add the last entry if it matches
        if current_entry and current_entry[0]:
            filtered_logs.append(current_entry[0])
    
    if json_output:
        # Convert datetime objects to strings for JSON serialization
        for log in filtered_logs:
            log['timestamp'] = log['timestamp'].strftime('%Y-%m-%d %H:%M:%S,%f')[:-3]
        return json.dumps(filtered_logs, indent=2)
    
    return filtered_logs

def print_logs(logs):
    """Print logs with color formatting."""
    for log in logs:
        level_color = LEVEL_COLORS.get(log['level'], COLORS['WHITE'])
        timestamp = log['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"{COLORS['CYAN']}{timestamp}{COLORS['RESET']} - "
              f"{COLORS['YELLOW']}{log['module']}{COLORS['RESET']} - "
              f"{level_color}{log['level']}{COLORS['RESET']} - "
              f"{log['message']}")
        print('-' * 80)

def main():
    parser = argparse.ArgumentParser(description='Analyze application log files')
    parser.add_argument('--file', '-f', help='Log file to analyze', default=None)
    parser.add_argument('--level', '-l', help='Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)', default=None)
    parser.add_argument('--module', '-m', help='Filter by module name', default=None)
    parser.add_argument('--hours', '-t', type=int, help='Show logs from the last N hours', default=None)
    parser.add_argument('--contains', '-c', help='Filter logs containing this text', default=None)
    parser.add_argument('--json', '-j', action='store_true', help='Output in JSON format')
    parser.add_argument('--list', action='store_true', help='List available log files')
    
    args = parser.parse_args()
    
    # Get the logs directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logs_dir = os.path.join(os.path.dirname(script_dir), 'logs')
    
    if not os.path.exists(logs_dir):
        print(f"Logs directory not found: {logs_dir}")
        return 1
    
    # List available log files
    if args.list:
        print(f"Available log files in {logs_dir}:")
        for file in os.listdir(logs_dir):
            if file.endswith('.log'):
                file_path = os.path.join(logs_dir, file)
                size = os.path.getsize(file_path)
                print(f"  - {file} ({size/1024:.2f} KB)")
        return 0
    
    # Determine which log file to analyze
    log_file = args.file
    if not log_file:
        # Default to admin.log if it exists
        default_log = os.path.join(logs_dir, 'admin.log')
        if os.path.exists(default_log):
            log_file = default_log
        else:
            # Use the first log file found
            log_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
            if log_files:
                log_file = os.path.join(logs_dir, log_files[0])
            else:
                print("No log files found.")
                return 1
    else:
        # If the file doesn't include a path, assume it's in the logs directory
        if not os.path.isabs(log_file):
            log_file = os.path.join(logs_dir, log_file)
    
    # Filter and display logs
    filtered_logs = filter_logs(
        log_file, 
        level=args.level, 
        module=args.module, 
        hours=args.hours, 
        contains=args.contains,
        json_output=args.json
    )
    
    if args.json:
        print(filtered_logs)
    else:
        if not filtered_logs:
            print("No matching logs found.")
            return 0
        
        print(f"Found {len(filtered_logs)} matching log entries in {log_file}:")
        print('=' * 80)
        print_logs(filtered_logs)
    
    return 0

if __name__ == '__main__':
    sys.exit(main()) 