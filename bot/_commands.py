from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import database as db
from translations import translate
from .temp_manager import get_user, get_user_parameters, reset_user_state, set_temp, invalidate_cached_parameters
import json
from ._enums import QUERY_ACTIONS, TEMP_KEYS
from router import route
from logger import setup_logger


logger = setup_logger(__name__)


@route(trigger="text", command="/help", action="send")
def help_(update):
    user = get_user(update)
    parameters = get_user_parameters(user)
    lang = parameters.language

    text = "help"
    reply_markup = None
    return text, reply_markup


@route(trigger="text", command="/start", action="send")
def start(update):
    user = get_user(update)
    username = update.get("message", {}).get("from", {}).get("username", None)
    if not username:
        first_name = update.get("message", {}).get("from", {}).get("first_name", "")
        last_name = update.get("message", {}).get("from", {}).get("last_name", "")
        username = ':' + first_name.lower() + ":" + last_name.lower() + ':'

    if db.Users.add({"user_id": user, "username": username})[0]:
        logger.info(f"New user added: {username} - {user}")
        set_temp(user, TEMP_KEYS.TIMEZONE_NOT_SET.value, 1)

    if len(get_user_parameters(user)) > 0:
        return help_(update)
    text = ""
    reply_markup = None
    return text, reply_markup


@route(trigger="text", command="/menu", action="send")
@route(trigger="callback_query", query_action=QUERY_ACTIONS.MENU.value, action="edit")
def menu(update):
    user = get_user(update)
    logger.debug(f'Constructing menu page for user: {user}')
    parameters = get_user_parameters(user)
    lang = parameters.language

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='      📃      ', callback_data=json.dumps([QUERY_ACTIONS.MENU_WORDS.value])),
            InlineKeyboardButton(text='      ⏰      ', callback_data=json.dumps([QUERY_ACTIONS.MENU_REMINDERS.value])),
            InlineKeyboardButton(text='      📙      ', callback_data=json.dumps([QUERY_ACTIONS.MENU_VOCABULARIES.value])),
            InlineKeyboardButton(text='      ⚙️      ', callback_data=json.dumps([QUERY_ACTIONS.MENU_SETTINGS.value])),
        ]
    ])

    text = (
        f"{translate(lang, 'choose_category')}\n"
        f"📃 {translate(lang, 'words')}\n"
        f"⏰ {translate(lang, 'reminders')}\n"
        f"📙 {translate(lang, 'vocabulary')}\n"
        f"⚙️ {translate(lang, 'settings')}"
    )

    return text, keyboard


@route(trigger="callback_query", query_action=QUERY_ACTIONS.CANCEL.value, action="send")
def cancel(update):
    user = get_user(update)
    reset_user_state(user)
    text = "Successfully cancelled"
    reply_markup = None
    return text, reply_markup


@route(trigger="other", action="send")
def unrecognized_message_handler(update):
    user = get_user(update)
    parameters = get_user_parameters(user)
    lang = parameters.language

    text = "Sorry, I didn't understand that kind of message. Try something else."
    reply_markup = None
    return text, reply_markup


@route(trigger="text", command="default", action="send")  # other commands will contain /
def default_command_handler(update):
    user = get_user(update)
    parameters = get_user_parameters(user)
    lang = parameters.language

    text = "Sorry, I didn't understand that command. Try /help or /menu."
    reply_markup = None
    return text, reply_markup


@route(trigger="callback_query", query_action=None, action=None)
def noop_query_handler(update):
    pass


@route(trigger="chat_member", action=None)
def handle_chat_member_status(update):
    user = get_user(update)
    old_status = update["my_chat_member"]["old_chat_member"]["status"]
    new_status = update["my_chat_member"]["new_chat_member"]["status"]

    if old_status == "member" and new_status == "kicked":
        logger.info(f"User {user} has blocked the bot")
        db.Users.delete({"user_id": user})  # all data is linked to user_id and will be deleted too
        invalidate_cached_parameters(user)
        logger.info(f"All records of {user} have been deleted")
    elif old_status == "kicked" and new_status == "member":
        logger.info(f"User {user} has unblocked the bot")
