import json
import database as db
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from translations import translate
from ._enums import QUERY_ACTIONS, TEMP_KEYS, USER_STATES
from .temp_manager import get_user, get_user_parameters, get_user_state, set_user_state, reset_user_state
import bot._commands
import bot._words
import bot._vocabularies
import bot._reminders
import bot._settings
from router import get_route
from logger import setup_logger


logger = setup_logger(__name__)
PARSE_MODE = "HTML"


class Bot:
    def __init__(self, token):
        logger.info('Initializing bot...')
        self.bot = telepot.Bot(token)
        self.users_data = {}

    def __del__(self):
        logger.info('Deleting bot...')

    def __getattr__(self, name):
        return getattr(self.bot, name)

    @staticmethod
    def get_cancel_button(lang):
        """Create cancel button with inline keyboard."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"❌ {translate(lang, 'cancel')}",
                                  callback_data=json.dumps([QUERY_ACTIONS.CANCEL.value]))],
        ])

    def manage_cancel_buttons(self, user, new_cancel_button_id=None, delete_old=True):
        """Manage the removal of old cancel buttons when a new one is sent."""
        old_cancel_button_id = None
        if delete_old:
            old_cancel_button_id = db.Temp.get({'user_id': user, "key": TEMP_KEYS.CANCEL_BUTTON_ID.value},
                                               include_column_names=True)
            if old_cancel_button_id:
                self.editMessageReplyMarkup((user, old_cancel_button_id.value), reply_markup=None)

        if new_cancel_button_id:
            db.Temp.add({"user_id": user, "key": TEMP_KEYS.CANCEL_BUTTON_ID.value, "value": new_cancel_button_id})
        elif old_cancel_button_id:
            db.Temp.delete({"user_id": user, "key": TEMP_KEYS.CANCEL_BUTTON_ID.value})

    def deliver_message(self, user, text, add_cancel_button=False, lang="", reply_to_msg_id=None, reply_markup=None):
        """Deliver a message to a user with optional cancel button and reply markup."""
        if reply_markup:
            final_reply_markup = reply_markup
        elif add_cancel_button:
            final_reply_markup = self.get_cancel_button(lang)
        else:
            final_reply_markup = {'remove_keyboard': True}

        response = self.sendMessage(user, text, reply_to_message_id=reply_to_msg_id, reply_markup=final_reply_markup, parse_mode=PARSE_MODE)

        logger.debug("Sent message: {}".format(response))

        if add_cancel_button:
            self.manage_cancel_buttons(user, response.get('message_id'), delete_old=False)  # old deleted in get_user

    def broadcast(self, text: str, reply_markup=None, exceptions=None):
        logger.info("Broadcasting message: {}".format(text))
        exceptions = exceptions or []
        logger.info(f"Found {len(exceptions)} exceptions")
        users = db.Users.execute_query("SELECT user_id FROM users;")
        for user in users:
            if user[0] in exceptions:
                continue
            self.deliver_message(user[0], text, reply_markup=reply_markup)
        logger.info(f"Sent to {len(users)} users")

    def broadcast_multilang(self, text: dict, reply_markup=None, exceptions=None):
        logger.info("Broadcasting message: {}".format(text))
        exceptions = exceptions or []
        logger.info(f"Found {len(exceptions)} exceptions")
        users = db.Users.execute_query("SELECT user_id, language FROM users;")
        for user, lang in users:
            if user[0] in exceptions:
                continue
            self.deliver_message(user, text[lang], reply_markup=reply_markup)
        logger.info(f"Sent to {len(users)} users")

    def handle_update(self, update):
        user = None
        try:
            # pretty print logs
            logger.debug('Received update: {}'.format(json.dumps(update, indent=4, ensure_ascii=False)))

            user = get_user(update)
            self.manage_cancel_buttons(user)
            callback_query_id = None

            trigger = None
            command = None
            state = None
            query_action = None
            if "message" in update:
                if "text" in update["message"]:
                    text = update["message"]["text"]
                    trigger = "text"

                    if text.startswith("/"):
                        command = text.split()[0]
                    else:
                        state = get_user_state(user)
                else:
                    self.deliver_message(user, "From the web: sorry, I didn't understand that kind of message")
                    return

            elif "callback_query" in update:
                trigger = "callback_query"
                query_action = json.loads(update["callback_query"]["data"])[0]
                msg_id = update["callback_query"]["message"]["message_id"]
                callback_query_id = update["callback_query"]["id"]

            elif "my_chat_member" in update:
                trigger = "chat_member"

            function, action, cancel_button = get_route(trigger, state, query_action, command)
            match action:
                case "send":
                    if callback_query_id:
                        self.answerCallbackQuery(callback_query_id)

                    if cancel_button:
                        text, lang = function(update)
                        self.deliver_message(user, text, add_cancel_button=True, lang=lang)
                    else:
                        text, reply_markup = function(update)
                        self.deliver_message(user, text, reply_markup=reply_markup)

                case "edit":  # editing message doesn't require answering callback_query
                    if trigger == "callback_query":
                        text, reply_markup = function(update)
                        self.editMessageText((user, msg_id), text, parse_mode="HTML", reply_markup=reply_markup)
                    else:
                        raise ValueError("Action is set to edit, but not triggered by callback query, so no msg_id")

                case "edit_markup":  # editing message reply markup doesn't require answering callback_query
                    if trigger == "callback_query":
                        reply_markup = function(update)
                        self.editMessageReplyMarkup((user, msg_id), reply_markup=reply_markup)
                    else:
                        raise ValueError("Action is set to edit, but not triggered by callback query, so no msg_id")

                case "popup":
                    if callback_query_id:
                        self.answerCallbackQuery(callback_query_id)
                    raise NotImplemented

                case None:
                    if callback_query_id:
                        self.answerCallbackQuery(callback_query_id)
                    function(update)

                case _:
                    raise ValueError(f"Unknown action {action}")

        except Exception as e:
            logger.critical(f"Couldn't process update: {e}", exc_info=True)
            logger.critical(f"Update that caused error: {json.dumps(update, indent=4, ensure_ascii=False)}")

            if user:
                try:
                    lang = get_user_parameters(user).language
                    self.deliver_message(user, translate(lang, "error"))
                except Exception as e_:
                    logger.critical(f"Couldn't notify user {user} about error: {e_}")
                else:
                    logger.info(f"User {user} has been notified about error")
