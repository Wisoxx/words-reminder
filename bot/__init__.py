import json
import database as db
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from translations import translate
from ._enums import QUERY_ACTIONS, TEMP_KEYS, USER_STATES
from logger import setup_logger


logger = setup_logger(__name__)


class Bot:
    from ._handlers import handle_message, handle_callback_query
    from ._menu import menu
    # from ._utils import TODO

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
                self.editMessageReplyMarkup((user, old_cancel_button_id["value"]), reply_markup=None)

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

        response = self.sendMessage(user, text, reply_to_message_id=reply_to_msg_id, reply_markup=final_reply_markup)

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


    def get_user_parameters(self, user):
        if user in self.users_data:
            return self.users_data[user]

        parameters = db.Users.get({"user_id": user}, include_column_names=True)
        self.users_data[user] = parameters
        return parameters

    def get_user(self, update):
        if "message" in update:
            user = update["message"]["chat"]["id"]
            lang = update["message"]["from"]["language_code"]
        elif "inline_query" in update:
            user = update["inline_query"]["from"]["id"]
            lang = update["inline_query"]["from"]["language_code"]
        elif "my_chat_member" in update:
            user = update["my_chat_member"]["from"]["id"]
            lang = update["my_chat_member"]["from"]["language_code"]
        else:
            raise KeyError("Couldn't find user")

        if user not in self.users_data:
            self.get_user_parameters(user)

        self.manage_cancel_buttons(user)
        return user, lang

    def handle_update(self, update):
        user = None
        lang = None
        try:
            logger.debug('Received update: {}'.format(json.dumps(update, indent=4)))  # pretty print logs

            user, lang = self.get_user(update)

            if "message" in update:
                self.handle_message(user, lang, update)

            elif "callback_query" in update:
                self.handle_callback_query(user, lang, update)

            elif "my_chat_member" in update:
                self.handle_chat_member_status(user, lang, update)

        except Exception as e:
            logger.critical(f"Couldn't process update: {e}", exc_info=True)
            logger.critical(f"Update that caused error: {json.dumps(update, indent=4)}")

            if user and lang:
                try:
                    self.deliver_message(user, translate(lang, "error"))
                except Exception as e_:
                    logger.critical(f"Couldn't notify user {user} about error: {e_}")
                else:
                    logger.info(f"User {user} has been notified about error")
