import json
import database as db
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from ._settings import get_user, get_user_parameters, set_user_state, reset_user_state
from .temp_manager import *
from ._enums import TaskStatus, QUERY_ACTIONS, TEMP_KEYS, USER_STATES
from .utils import html_wrapper, escape_html, get_hh_mm, suggest_reminder_time, shift_time
from router import route, get_route
from translations import translate


@route(trigger="text", command="/test", action="send")
def test(update):
    text = "Test"
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="PICK TIME",
                                     callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value,
                                                               suggest_reminder_time(),
                                                               True,
                                                               ('callback_query', None,
                                                                QUERY_ACTIONS.DELETE_REMINDER.value, None),
                                                               QUERY_ACTIONS.MENU_REMINDERS.value])),
            ],
        ]
    )
    return text, reply_markup


@route(trigger="text", command="/test2", action="send")
def test2(update):
    text = "Test"
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="PICK TIME",
                                     callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value,
                                                               suggest_reminder_time(),
                                                               False,
                                                               ('callback_query', None,
                                                                QUERY_ACTIONS.DELETE_REMINDER.value, None),
                                                               QUERY_ACTIONS.MENU_REMINDERS.value])),
            ],
        ]
    )
    return text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.PICK_TIME.value, action="edit_markup")
def pick_time(update):
    user = get_user(update)
    parameters = get_user_parameters(user)
    lang = parameters.language
    timezone = parameters.timezone
    callback_data = json.loads(update["callback_query"]["data"])
    time, include_minutes, return_route, back_button_action = callback_data[1:]
    h = translate(lang, 'short_hours')
    mins = translate(lang, 'short_minutes')

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
                        return_route,
                        back_button_action
                    ])
                )
            )
        return buttons

    rows = [
        [
            InlineKeyboardButton(
                text=shift_time(time, hour_offset=timezone),
                callback_data=json.dumps([
                    QUERY_ACTIONS.TIME_CHOSEN.value,
                    time,
                    return_route,
                    back_button_action
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


@route(trigger="callback_query", query_action=QUERY_ACTIONS.TIME_CHOSEN.value, action="send")
def chosen_time(update):
    callback_data = json.loads(update["callback_query"]["data"])
    time, return_route, back_button_action = callback_data[1:]
    update["callback_query"]["data"] = json.dumps([back_button_action, time])
    return get_route(*return_route).call(update)


@route(trigger="callback_query", query_action=QUERY_ACTIONS.DELETE_REMINDER.value, action="send")
def test1(update):
    callback_data = json.loads(update["callback_query"]["data"])
    time = callback_data[1]
    return time, None


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
