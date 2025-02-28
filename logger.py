import logging
from logging.handlers import RotatingFileHandler
import os
import threading
from datetime import datetime


LOG_PATH = os.path.join(os.path.expanduser("~"), 'mysite', 'logs')
os.makedirs(LOG_PATH, exist_ok=True)

LOG_FILE = os.path.join(LOG_PATH, 'app.log')

# Thread-local storage for per-update debug logs
thread_local = threading.local()
show_debug = False  # controls debug showing in logs


def set_show_debug(value: bool):
    global show_debug
    show_debug = value


class DebugLogFilter(logging.Filter):
    """Custom filter to store DEBUG logs per Telegram update in thread-local storage."""
    def filter(self, record):
        if record.levelno == logging.DEBUG:
            # Check if we should show debug logs
            if show_debug:
                return True  # Allow DEBUG logs to be logged to the output

            # Otherwise, store them in thread-local storage
            if not hasattr(thread_local, "debug_log_stack"):
                thread_local.debug_log_stack = []
            log_entry = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {record.levelname}: {record.getMessage()} [in {record.pathname}:{record.lineno}]"
            print(f"Adding to debug log stack: {log_entry}")  # Debug print to see the added entries
            thread_local.debug_log_stack.append(log_entry)  # Store formatted log
            return False  # Prevent DEBUG log from being processed normally
        return True  # Allow all other log levels


def setup_logger(name):
    logger = logging.getLogger("main_logger")  # Use a single global name
    if logger.hasHandlers():
        return logger  # Prevent duplicate handlers

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=10_000_000, backupCount=3, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
                                  datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.DEBUG)

    # Add debug log filter
    debug_filter = DebugLogFilter()
    file_handler.addFilter(debug_filter)

    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter('%(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.DEBUG)

    logger.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger


def clean_line(line):
    return ''.join(char for char in line if char.isprintable())


def process_logs():
    from flask import Response, render_template_string
    import re
    log_file_path = os.path.join(os.path.expanduser("~"), 'mysite', 'logs', 'app.log')
    level_colors = {
        "DEBUG": "lightblue",
        "INFO": "lightgreen",
        "WARNING": "orange",
        "ERROR": "red",
        "CRITICAL": "magenta",
    }

    try:
        with open(log_file_path, 'r', encoding='utf-8', errors='replace') as log_file:
            log_content = log_file.readlines()  # Read the log file line by line

        colored_logs = []
        entry_lines = []
        timestamp_pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'

        for line in log_content:
            line = clean_line(line).rstrip()  # Clean line and remove trailing whitespace

            # Detect the start of a new log entry by timestamp format
            if re.match(timestamp_pattern, line) and entry_lines:
                # Process the accumulated entry
                entry_text = "\n".join(entry_lines)

                # Determine the color based on log level in the first line of the entry
                current_color = "white"
                parts = entry_lines[0].split(maxsplit=3)
                if len(parts) >= 3:
                    level = parts[2].strip(":")
                    current_color = level_colors.get(level, "white")

                # Append the entry with the determined color
                colored_logs.append(
                    f'<span style="color: {current_color};">{entry_text}</span><br>'
                )

                # Reset for the next entry
                entry_lines = []

            # Accumulate lines for the current entry
            entry_lines.append(line)

        # Process the last entry if there are remaining lines
        if entry_lines:
            entry_text = "\n".join(entry_lines)
            current_color = "white"
            parts = entry_lines[0].split(maxsplit=3)
            if len(parts) >= 3:
                level = parts[2].strip(":")
                current_color = level_colors.get(level, "white")

            colored_logs.append(
                f'<span style="color: {current_color};">{entry_text}</span><br>'
            )

        # Join the logs for rendering and wrap in the HTML template
        return render_template_string('''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Log Viewer</title>
                <style>
                    body {
                        display: flex;
                        flex-direction: column;
                        height: 100vh;
                        margin: 0;
                        background-color: #000;  /* Set the background to black */
                        color: #fff;              /* Set the text color to white */
                    }
                    .log-content {
                        flex: 1;
                        overflow-y: auto;
                        padding: 10px;
                        border: 1px solid #ccc;
                        background-color: #000;  /* Keep log content background black */
                    }
                    pre {
                        white-space: pre-wrap;   /* Ensure long lines wrap */
                        word-wrap: break-word;   /* Break words to fit the container */
                    }
                </style>
            </head>
            <body>
                <div class="log-content">
                    <pre>{{ colored_logs|safe }}</pre>  <!-- Render the colored logs safely -->
                </div>
                <script>
                    // Scroll to the bottom of the log content
                    document.querySelector('.log-content').scrollTop = document.querySelector('.log-content').scrollHeight;
                </script>
            </body>
            </html>
        ''', colored_logs=''.join(colored_logs))  # Join the colored logs for rendering

    except Exception as e:
        return Response(f"Error reading log file: {str(e)}", status=500)
