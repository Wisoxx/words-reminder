import json
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from .temp_manager import *
from ._enums import QUERY_ACTIONS
from .utils import get_hh_mm, shift_time
from router import route
from translations import translate


@route(trigger="callback_query", query_action=QUERY_ACTIONS.PICK_TIME.value, action="edit_markup")
def pick_time(update, time=None, include_minutes=None, next_query_action=None, back_button_action=None,
              real_time_mins=None, adjust_to_timezone=None):
    """
    Generates an inline keyboard to pick or adjust a time, with optional real-time update of minutes.

    :param update: The Telegram update object.
    :param time: The initial time in "HH:MM" format. If None, it's derived from the callback data.
    :param include_minutes: Whether to include minute adjustment buttons. Conflicts with 'real_time_mins'.
    :param next_query_action: The next action to execute upon selecting a time.
    :param back_button_action: The callback action for the back button.
    :param real_time_mins: Whether to update the minutes dynamically in real-time. Conflicts with `include_minutes`
    :param adjust_to_timezone: Whether to adjust the displayed time to the user's timezone.
    :return: An InlineKeyboardMarkup object with the time adjustment buttons.
    """
    user = get_user(update)
    parameters = get_user_parameters(user)
    lang = parameters.language
    timezone = parameters.timezone if adjust_to_timezone else 0

    if all((not time, not include_minutes, not next_query_action, not back_button_action, not real_time_mins,
            not adjust_to_timezone)):
        callback_data = json.loads(update["callback_query"]["data"])
        time, include_minutes, next_query_action, back_button_action, real_time_mins, adjust_to_timezone = callback_data[1:]

    h = translate(lang, 'short_hours')
    mins = translate(lang, 'short_minutes')

    if real_time_mins:
        if include_minutes:
            raise ValueError("Two conflicting parameters are enabled")
        current_time = get_hh_mm()
        hours, _ = time.split(":")
        _, current_minutes = current_time.split(":")
        time = f"{hours}:{current_minutes}"

    def build_adjustment_row(label, adjustments, is_hour=True):
        """
        Helper to create a row of adjustment buttons for time.
        :param label: Unit label for the button text (e.g., 'hours' or 'minutes').
        :param adjustments: List of integers for the time adjustments.
        :param is_hour: If True, adjusts hours; otherwise, adjusts minutes.
        :return: A list of InlineKeyboardButton objects.
        """
        buttons = []
        for adjustment in adjustments:
            offset_args = {"hour_offset": adjustment} if is_hour else {"min_offset": adjustment}
            adjusted_time = shift_time(time, **offset_args)
            buttons.append(
                InlineKeyboardButton(
                    text=f"  {adjustment:+} {label}  ",
                    callback_data=json.dumps([
                        QUERY_ACTIONS.PICK_TIME.value,
                        adjusted_time,
                        include_minutes,
                        next_query_action,
                        back_button_action,
                        real_time_mins,
                        adjust_to_timezone
                    ])
                )
            )
        return buttons

    rows = [
        [
            InlineKeyboardButton(  # Button to confirm chosen time
                text=shift_time(time, hour_offset=timezone),
                callback_data=json.dumps([
                    next_query_action,
                    time
                ])
            )
        ],
        build_adjustment_row(h, [-5, -1, 1, 5]),
    ]

    if include_minutes:
        rows.extend([
            build_adjustment_row(mins, [-5, -1, 1, 5], is_hour=False),
            build_adjustment_row(mins, [-15, -10, 10, 15], is_hour=False),
        ])

    rows.append([
        InlineKeyboardButton(
            text='      ↩️      ',
            callback_data=json.dumps([back_button_action])
        )
    ])

    reply_markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return reply_markup


def generate_number_keyboard(next_query_action, back_button_action, max_number=15):
    """
    Generates an inline keyboard for selecting numbers from 1 to max_number with a back button.

    :param next_query_action: The query action to use in the callback data for number buttons.
    :param back_button_action: The callback action for the back button.
    :param max_number: The maximum number to include in the keyboard (default is 15).
    :return: An InlineKeyboardMarkup object with the number buttons and a back button.
    """
    buttons = []

    for i in range(1, max_number + 1, 5):  # Group numbers in rows of 5
        row = [
            InlineKeyboardButton(
                text=str(number),
                callback_data=json.dumps([next_query_action, number])
            )
            for number in range(i, min(i + 5, max_number + 1))
        ]
        buttons.append(row)

    buttons.append([
        InlineKeyboardButton(
            text='      ↩️      ',
            callback_data=json.dumps([back_button_action])
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)
