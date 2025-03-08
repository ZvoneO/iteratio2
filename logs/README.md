# Application Logs

This directory contains log files for the Resource Planning Application. These logs are essential for debugging and monitoring the application.

## Log Files

- **admin.log**: Logs from the admin module, including user management operations
- **app.log**: General application logs
- Other module-specific logs may be created as needed

## Log Format

Logs are formatted as follows:

```
TIMESTAMP - MODULE - LEVEL - MESSAGE
```

Example:
```
2023-04-15 12:34:56,789 - admin - INFO - User updated successfully
```

## Log Levels

- **DEBUG**: Detailed information, typically of interest only when diagnosing problems
- **INFO**: Confirmation that things are working as expected
- **WARNING**: An indication that something unexpected happened, or may happen in the near future
- **ERROR**: Due to a more serious problem, the software has not been able to perform some function
- **CRITICAL**: A serious error, indicating that the program itself may be unable to continue running

## Analyzing Logs

You can use the `scripts/check_logs.py` script to analyze logs:

```bash
# List available log files
python scripts/check_logs.py --list

# View all ERROR logs from the last 24 hours
python scripts/check_logs.py --level ERROR --hours 24

# Search for specific text in logs
python scripts/check_logs.py --contains "user updated"

# Output logs in JSON format
python scripts/check_logs.py --json
```

For more options, run:
```bash
python scripts/check_logs.py --help
```

## Log Rotation

Log files are not automatically rotated. Consider implementing log rotation to prevent log files from growing too large.

## Troubleshooting

If you encounter issues with the application, checking the logs should be your first step. Look for ERROR or WARNING messages that might indicate the source of the problem. 