import database as db
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
from ._enums import TaskStatus, QUERY_ACTIONS, TEMP_KEYS, USER_STATES
from .temp_manager import set_temp, get_temp, remove_temp, pop_temp
from .utils import html_wrapper, escape_html
from translations import translate
from router import route
from logger import setup_logger


logger = setup_logger(__name__)


####################################################################################################################
#                                                DATABASE INTERACTIONS
####################################################################################################################
def get_user(update):
    if "message" in update:
        user = update["message"]["chat"]["id"]
    elif "callback_query" in update:
        user = update["callback_query"]["from"]["id"]
    elif "my_chat_member" in update:
        user = update["my_chat_member"]["from"]["id"]
    else:
        raise KeyError("Couldn't find user")

    return user


def get_user_parameters(user):
    return db.Users.get({"user_id": user}, include_column_names=True)


def get_user_state(user):
    state = get_temp(user, TEMP_KEYS.STATE.value)
    logger.debug(f"User state: {state}")
    return int(state) if state is not None else None


def set_user_state(user, state):
    status = set_temp(user, TEMP_KEYS.STATE.value, state)
    if status:
        logger.debug(f"User state was set to: {state}")
    return status


def reset_user_state(user):
    status = remove_temp(user, TEMP_KEYS.STATE.value)
    if status:
        logger.debug(f"User state was reset")
    return status

####################################################################################################################
#                                                DATABASE INTERACTIONS
####################################################################################################################


def _toggle_hide_meaning(user):
    status = db.Users.execute_query("""
    UPDATE users
    SET hide_meaning = NOT hide_meaning
    WHERE user_id = ?;
    """, (user, )).rowcount > 0
    if status:
        logger.debug(f"User {user} toggled hide_meaning")
    return status


####################################################################################################################
#                                                     OTHER
####################################################################################################################


####################################################################################################################
#                                                  BOT ACTIONS
####################################################################################################################


@route(trigger="callback_query", query_action=QUERY_ACTIONS.MENU_SETTINGS.value, action="edit")
def settings(update):
    user = get_user(update)
    parameters = get_user_parameters(user)
    lang = parameters.language
    hide_meaning = parameters.hide_meaning
    timezone = parameters.timezone
    heading = html_wrapper(
        escape_html(
            "<><><><><><><><><><><><><><><><><><><>\n" +
            f"{' ' * 30}Settings\n" +
            "<><><><><><><><><><><><><><><><><><><>"
        ),
        'b')
    text = (f"🌎 Language: {translate(lang, 'flag')}\n"
            f"👁 Hide meaning: {'✅' if hide_meaning else '❌'}\n"
            f"🕓 Timezone: {timezone}")

    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f'      🌎      ',
                                 callback_data=json.dumps([QUERY_ACTIONS.CHANGE_LANGUAGE.value])),
            InlineKeyboardButton(text=f'      👁      ',
                                 callback_data=json.dumps([QUERY_ACTIONS.TOGGLE_HIDE_MEANING.value])),
            InlineKeyboardButton(text=f'      🕓      ',
                                 callback_data=json.dumps([QUERY_ACTIONS.CHANGE_TIMEZONE.value])),
        ],
        [
            InlineKeyboardButton(text='      ↩️      ', callback_data=json.dumps([QUERY_ACTIONS.MENU.value])),
            InlineKeyboardButton(text='      ℹ️      ',
                                 callback_data=json.dumps([QUERY_ACTIONS.SHOW_INFO.value, "info_settings"])),
        ]
    ])
    return heading + '\n' + text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.TOGGLE_HIDE_MEANING.value, action="edit")
def toggle_hide_meaning(update):
    user = get_user(update)
    _toggle_hide_meaning(user)
    return settings(update)
