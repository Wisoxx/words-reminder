from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import database as db
from translations import translate
from ._settings import get_user_parameters
from ._response_format import Response
import json
from ._enums import QUERY_ACTIONS
from router import route
from logger import setup_logger

logger = setup_logger(__name__)


@route(trigger="text", command="/start", action="send")
def start(user, update):
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
def menu(user, update):
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

    return Response(text, keyboard)


def recall(user, update):
    text = "recall"
    reply_markup = None
    return text, reply_markup
