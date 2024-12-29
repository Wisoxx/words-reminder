import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger(name):
    log_path = os.path.join(os.path.expanduser("~"), 'mysite', 'logs')
    os.makedirs(log_path, exist_ok=True)

    logger = logging.getLogger(name)

    if not logger.hasHandlers():
        file_handler = RotatingFileHandler(os.path.join(log_path, 'app.log'), maxBytes=500000, backupCount=3)
        formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.INFO)

        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.DEBUG)

        logger.setLevel(logging.DEBUG)  # lowest level to allow separate levels for files and console
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

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
        with open(log_file_path, 'r') as log_file:
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
