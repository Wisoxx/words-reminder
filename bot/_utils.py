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


def pad(pad_str, original_str, pad_left=False):
    """
    Pads a string to a specified length, either on the left or the right.

    :param pad_str: The padding string to use for filling.
    :param original_str: The original string to pad. If None, returns the pad string.
    :param pad_left: Boolean indicating whether to pad on the left (default is False for right padding).
    :return: The padded string.
    """
    if original_str is None:
        return pad_str

    if pad_left:
        return (pad_str + original_str)[-len(pad_str):]
    else:
        return (original_str + pad_str)[:len(pad_str)]

