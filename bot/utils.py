import time
from datetime import datetime, timedelta


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


def get_hh_mm(offset=0):
    """
    Returns the current time in HH:MM format (24-hour clock), adjusted by an optional offset in hours.
    :param offset: The number of hours to adjust the time by (can be positive or negative). Default is 0.
    :return: A string representing the adjusted time in HH:MM format.
    """
    now = datetime.now()
    return display_time(now.strftime("%H:%M"), offset=offset)


def display_time(time_str, offset=0):
    """
    Adjusts a given time in HH:MM format by a specified offset in hours and displays the result.
    :param time_str: The input time in "HH:MM" format.
    :param offset: The number of hours to adjust the time by (can be positive or negative). Default is 0.
    :return: A string in the format "Adjusted Time: HH:MM (UTC+offset)".
    """
    input_time = datetime.strptime(time_str, "%H:%M")
    adjusted_time = input_time + timedelta(hours=offset)
    return adjusted_time.strftime('%H:%M')


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

