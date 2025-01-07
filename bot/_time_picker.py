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
                                     callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value])),
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
    time = callback_data[1] if len(callback_data) > 1 else suggest_reminder_time()
    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=shift_time(time, offset=timezone),
                                     callback_data=json.dumps([QUERY_ACTIONS.TIME_CHOSEN.value, time])),
            ],
            [
                InlineKeyboardButton(text="      -1      ",
                                     callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value, shift_time(time, -1)])),
                InlineKeyboardButton(text="      -5      ",
                                     callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value, shift_time(time, -5)])),
                InlineKeyboardButton(text="      +1      ",
                                     callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value, shift_time(time, 1)])),
                InlineKeyboardButton(text="      +5      ",
                                     callback_data=json.dumps([QUERY_ACTIONS.PICK_TIME.value, shift_time(time, 5)])),
            ],
        ]
    )
    return reply_markup
