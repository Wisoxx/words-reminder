import time


def html_wrapper(text, wrapper=None):
    """Wrap text in an HTML tag if a wrapper is provided."""
    if wrapper:
        return f"<{wrapper}>{text}</{wrapper}>"
    return text


def escape_html(text):
    """Escape HTML special characters < and >."""
    return text.replace("<", "&lt;").replace(">", "&gt;")


def get_timestamp():
    return int(time.time())
