#!/usr/bin/env python3
"""
Log Analysis Tool for Resource Planning Application

This script provides functionality to analyze log files, filter by various criteria,
and display results in a readable format.

Usage:
    python check_logs.py [options]

Options:
    --list              List available log files
    --file FILE         Specify log file to analyze (default: all log files)
    --level LEVEL       Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    --module MODULE     Filter by module name
    --hours HOURS       Show logs from the last N hours
    --contains TEXT     Filter logs containing specific text
    --json              Output in JSON format
    --help              Show this help message
"""

import os
import sys
import re
import json
import argparse
from datetime import datetime, timedelta
import glob
from colorama import init, Fore, Style

# Initialize colorama
init()

# Define color mapping for log levels
LEVEL_COLORS = {
    'DEBUG': Fore.BLUE,
    'INFO': Fore.GREEN,
    'WARNING': Fore.YELLOW,
    'ERROR': Fore.RED,
    'CRITICAL': Fore.RED + Style.BRIGHT
}

def parse_log_line(line):
    """
    Parse a log line into its components.
    
    Expected format: TIMESTAMP - MODULE - LEVEL - MESSAGE
    
    Returns:
        dict: Parsed log entry or None if the line doesn't match the expected format
    """
    # Regular expression to match log format
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (\w+) - (.+)'
    match = re.match(pattern, line)
    
    if match:
        timestamp_str, module, level, message = match.groups()
        try:
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
            return {
                'timestamp': timestamp,
                'timestamp_str': timestamp_str,
                'module': module,
                'level': level,
                'message': message,
                'raw': line
            }
        except ValueError:
            return None
    return None

def filter_logs(log_file, level=None, module=None, hours=None, contains=None, json_output=False):
    """
    Filter logs based on criteria.
    
    Args:
        log_file (str): Path to log file
        level (str): Log level to filter by
        module (str): Module name to filter by
        hours (int): Show logs from the last N hours
        contains (str): Filter logs containing specific text
        json_output (bool): Whether to output in JSON format
        
    Returns:
        list: Filtered log entries
    """
    filtered_logs = []
    
    # Calculate cutoff time if hours is specified
    cutoff_time = None
    if hours:
        cutoff_time = datetime.now() - timedelta(hours=int(hours))
    
    try:
        with open(log_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Parse log line
                log_entry = parse_log_line(line)
                if not log_entry:
                    continue
                
                # Apply filters
                if level and log_entry['level'] != level:
                    continue
                
                if module and log_entry['module'] != module:
                    continue
                
                if cutoff_time and log_entry['timestamp'] < cutoff_time:
                    continue
                
                if contains and contains.lower() not in log_entry['raw'].lower():
                    continue
                
                filtered_logs.append(log_entry)
    except FileNotFoundError:
        if not json_output:
            print(f"Error: Log file '{log_file}' not found.")
        return []
    except Exception as e:
        if not json_output:
            print(f"Error reading log file '{log_file}': {str(e)}")
        return []
    
    return filtered_logs

def print_logs(logs, json_output=False):
    """
    Print logs in a readable format.
    
    Args:
        logs (list): List of log entries
        json_output (bool): Whether to output in JSON format
    """
    if json_output:
        # Convert datetime objects to strings for JSON serialization
        for log in logs:
            log['timestamp'] = log['timestamp_str']
        print(json.dumps(logs, indent=2))
        return
    
    for log in logs:
        level_color = LEVEL_COLORS.get(log['level'], '')
        timestamp = log['timestamp_str']
        module = log['module']
        level = log['level']
        message = log['message']
        
        print(f"{Fore.WHITE}{timestamp} - {Fore.CYAN}{module} - {level_color}{level}{Fore.RESET} - {message}")

def main():
    """Main function to parse arguments and execute log analysis."""
    parser = argparse.ArgumentParser(description='Log Analysis Tool')
    parser.add_argument('--list', action='store_true', help='List available log files')
    parser.add_argument('--file', help='Specify log file to analyze (default: all log files)')
    parser.add_argument('--level', help='Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')
    parser.add_argument('--module', help='Filter by module name')
    parser.add_argument('--hours', type=int, help='Show logs from the last N hours')
    parser.add_argument('--contains', help='Filter logs containing specific text')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    
    args = parser.parse_args()
    
    # Get log directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_dir = os.path.join(os.path.dirname(script_dir), 'logs')
    
    # List available log files
    if args.list:
        log_files = glob.glob(os.path.join(log_dir, '*.log'))
        if log_files:
            print("Available log files:")
            for log_file in sorted(log_files):
                print(f"  - {os.path.basename(log_file)}")
        else:
            print("No log files found.")
        return
    
    # Determine which log files to analyze
    if args.file:
        log_files = [os.path.join(log_dir, args.file)]
        if not args.file.endswith('.log'):
            log_files = [f"{log_files[0]}.log"]
    else:
        log_files = glob.glob(os.path.join(log_dir, '*.log'))
    
    # Filter and print logs
    all_logs = []
    for log_file in log_files:
        logs = filter_logs(
            log_file,
            level=args.level,
            module=args.module,
            hours=args.hours,
            contains=args.contains,
            json_output=args.json
        )
        all_logs.extend(logs)
    
    # Sort logs by timestamp
    all_logs.sort(key=lambda x: x['timestamp'])
    
    # Print logs
    if all_logs:
        print_logs(all_logs, json_output=args.json)
    elif not args.json:
        print("No logs found matching the specified criteria.")

if __name__ == '__main__':
    main() 