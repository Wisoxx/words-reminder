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
    return shift_time(now.strftime("%H:%M"), hour_offset=offset)


def shift_time(time_str, hour_offset=0, min_offset=0):
    """
    Adjusts a given time in HH:MM format by specified hour and minute offsets.

    :param time_str: The input time in "HH:MM" format.
    :param hour_offset: The number of hours to adjust the time by (can be positive or negative). Default is 0.
    :param min_offset: The number of minutes to adjust the time by (can be positive or negative). Default is 0.
    :return: A string in the format "Adjusted Time: HH:MM".
    """
    input_time = datetime.strptime(time_str, "%H:%M")
    adjusted_time = input_time + timedelta(hours=hour_offset, minutes=min_offset)
    return adjusted_time.strftime('%H:%M')


def calculate_timezone_offset(user_time_str: str):
    """
    Calculates the user's timezone offset based on the provided current time in HH:MM format.

    :param user_time_str: The time the user claims to have right now, in HH:MM format (24-hour clock).
    :return: The timezone offset in hours as an integer (e.g., -5, 0, +3).
    """
    utc_now = datetime.utcnow()
    user_time = datetime.strptime(user_time_str, "%H:%M")

    if user_time.hour < utc_now.hour:
        user_time = user_time.replace(year=utc_now.year, month=utc_now.month, day=utc_now.day + 1)
    else:
        user_time = user_time.replace(year=utc_now.year, month=utc_now.month, day=utc_now.day)

    time_difference = user_time - utc_now
    offset_hours = round(time_difference.total_seconds() / 3600)

    return offset_hours


def suggest_reminder_time():
    """
    Suggests a time for a reminder, rounded to the nearest hour.
    :return: A string representing the suggested time in "HH:00" format.
    """
    now = datetime.now()
    rounded_time = now.replace(minute=0, second=0, microsecond=0)
    if now.minute >= 30:
        rounded_time += timedelta(hours=1)
    return rounded_time.strftime("%H:%M")


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
