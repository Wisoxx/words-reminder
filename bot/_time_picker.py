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
                                     callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value, True])),
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
                                     callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value, False])),
            ],
        ]
    )
    return text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.PICK_TIME.value, action="edit_markup")
def pick_time(update):
    user = get_user(update)
    parameters = get_user_parameters(user)
    timezone = parameters.timezone
    callback_data = json.loads(update["callback_query"]["data"])
    include_minutes = callback_data[1]
    time = callback_data[2] if len(callback_data) > 2 else suggest_reminder_time()
    rows = [
        [
            InlineKeyboardButton(text=shift_time(time, hour_offset=timezone),
                                 callback_data=json.dumps([QUERY_ACTIONS.TIME_CHOSEN.value, time])),
        ],
        [
            InlineKeyboardButton(text="  -5 год  ",
                                 callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value,
                                                           include_minutes,
                                                           shift_time(time, -5)])),
            InlineKeyboardButton(text="  -1 год  ",
                                 callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value,
                                                           include_minutes,
                                                           shift_time(time, -1)])),
            InlineKeyboardButton(text="  +1 год  ",
                                 callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value,
                                                           include_minutes,
                                                           shift_time(time, 1)])),
            InlineKeyboardButton(text="  +5 год  ",
                                 callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value,
                                                           include_minutes,
                                                           shift_time(time, 5)])),
        ],
    ]

    if include_minutes:
        rows.extend(
            [
                [
                    InlineKeyboardButton(text="  -5 хв  ",
                                         callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value,
                                                                   include_minutes,
                                                                   shift_time(time, 0, -5)])),
                    InlineKeyboardButton(text="  -1 хв  ",
                                         callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value,
                                                                   include_minutes,
                                                                   shift_time(time, 0, -1)])),
                    InlineKeyboardButton(text="  +1 хв  ",
                                         callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value,
                                                                   include_minutes,
                                                                   shift_time(time, 0, 1)])),
                    InlineKeyboardButton(text="  +5 хв  ",
                                         callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value,
                                                                   include_minutes,
                                                                   shift_time(time, 0, 5)])),
                ],
                [
                    InlineKeyboardButton(text="  -15 хв  ",
                                         callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value,
                                                                   include_minutes,
                                                                   shift_time(time, 0, -15)])),
                    InlineKeyboardButton(text="  -10 хв  ",
                                         callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value,
                                                                   include_minutes,
                                                                   shift_time(time, 0, -10)])),
                    InlineKeyboardButton(text="  +10 хв  ",
                                         callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value,
                                                                   include_minutes,
                                                                   shift_time(time, 0, 10)])),
                    InlineKeyboardButton(text="  +15 хв  ",
                                         callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value,
                                                                   include_minutes,
                                                                   shift_time(time, 0, 15)])),
                ],
            ]
        )

    reply_markup = InlineKeyboardMarkup(inline_keyboard=rows)
    return reply_markup
