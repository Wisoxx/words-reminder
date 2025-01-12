from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import database as db
from translations import translate
from ._vocabularies import _get_vocabulary_name
from .temp_manager import get_user, get_user_parameters, reset_user_state
from ._words import _get_old_words, _word_list_to_pages
import json
from ._enums import QUERY_ACTIONS
from router import route
from logger import setup_logger


logger = setup_logger(__name__)


@route(trigger="text", command="/start", action="send")
def start(update):
    user = get_user(update)
    username = update.get("message", {}).get("from", {}).get("username", None)
    if not username:
        first_name = update.get("message", {}).get("from", {}).get("first_name", "")
        last_name = update.get("message", {}).get("from", {}).get("last_name", "")
        username = ':' + first_name.lower() + ":" + last_name.lower() + ':'

    if db.Users.add({"user_id": user, "username": username})[0]:
        logger.info(f"New user added: {username}")
    text = "start"
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


@route(trigger="callback_query", query_action=QUERY_ACTIONS.RECALL.value, action="edit")
@route(trigger="text", command="/recall", action="send")
def recall(update=None, user=None, vocabulary_id=None, limit=15):
    user = user or get_user(update)
    parameters = get_user_parameters(user)
    vocabulary_id = vocabulary_id or parameters.current_vocabulary_id
    lang = parameters.language
    hide_meaning = parameters.hide_meaning

    # if possible, get vocabulary_id and limit from callback query to refresh with the same values
    if isinstance(update, dict):
        callback_data = update.get("callback_query", {}).get("data", "[]")
        callback_data = json.loads(callback_data)
        vocabulary_id, limit = callback_data[1:]
    vocabulary_name = _get_vocabulary_name(vocabulary_id)

    logger.info(f"Reminding user {user} {limit} words from vocabulary #{vocabulary_id}")

    words = _get_old_words(user, vocabulary_id, limit)
    page = _word_list_to_pages(words, hide_meaning)[0]
    text = f"Here are {limit} oldest words from {vocabulary_name}:\n\n" + page
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='      🔄      ', callback_data=json.dumps([QUERY_ACTIONS.RECALL.value,
                                                                                 vocabulary_id,
                                                                                 limit])),
        ],
        [
            InlineKeyboardButton(text='      ↩️      ', callback_data=json.dumps([QUERY_ACTIONS.MENU_WORDS.value])),
            InlineKeyboardButton(text='      ℹ️      ',
                                 callback_data=json.dumps([QUERY_ACTIONS.SHOW_INFO.value, "info_recall"])),
        ]
    ])
    return text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.CANCEL.value, action="send")
def cancel(update):
    user = get_user(update)
    reset_user_state(user)
    text = "Successfully cancelled"
    reply_markup = None
    return text, reply_markup


@route(trigger="chat_member", action=None)
def handle_chat_member_status(update):
    user = get_user(update)
    old_status = update["my_chat_member"]["old_chat_member"]["status"]
    new_status = update["my_chat_member"]["new_chat_member"]["status"]

    if old_status == "member" and new_status == "kicked":
        logger.info(f"User {user} has blocked the bot")
        db.Users.delete({"user_id": user})  # all data is linked to user_id and will be deleted too
        logger.info(f"All records of {user} have been deleted")
    elif old_status == "kicked" and new_status == "member":
        logger.info(f"User {user} has unblocked the bot")
