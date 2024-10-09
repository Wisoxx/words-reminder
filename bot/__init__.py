import json
import database as db
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from translations import translate
from ._enums import QUERY_ACTIONS, TEMP_KEYS, USER_STATES
from logger import setup_logger


logger = setup_logger(__name__)


class Bot:
    from ._menu import menu

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

    def manage_cancel_buttons(self, user, new_cancel_button_id=None):
        """Manage the removal of old cancel buttons when a new one is sent."""
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
            self.manage_cancel_buttons(user, response.get('message_id'))

    def broadcast(self, text, reply_markup=None):
        users = db.Users.execute_query("SELECT user_id FROM users;")
        for user in users:
            self.deliver_message(user[0], text, reply_markup=reply_markup)

    def get_user_parameters(self, user):
        if user in self.users_data:
            return self.users_data[user]["parameters"]

        parameters = db.Users.get({"user_id": user}, include_column_names=True)
        self.users_data[user] = parameters
        return parameters

    def get_user(self, update):
        if "message" in update:
            user = update["message"]["chat"]["id"]
        elif "callback_query" in update:
            user = update["callback_query"]["message"]["chat"]["id"]
        else:
            raise KeyError("Couldn't find user")

        if user not in self.users_data:
            self.users_data[user] = {"parameters": self.get_user_parameters(user), "update": update}
        else:
            self.users_data[user]["update"] = update

        self.manage_cancel_buttons(user)
        return user

    def handle_update(self, update):
        user = None
        try:
            logger.debug('Received update: {}'.format(update))

            user = self.get_user(update)

            if "message" in update:
                if "text" in update["message"]:
                    text = update["message"]["text"]
                    if text == "/test":
                        self.deliver_message(user, "Test Message", add_cancel_button=True, lang="en")
                    elif text == "/menu":
                        self.menu(user)
                    else:
                        self.deliver_message(user, "From the web: you said '{}'".format(text))
                else:
                    self.deliver_message(user, "From the web: sorry, I didn't understand that kind of message")

            elif "callback_query" in update:
                callback_data = update["callback_query"]["data"]
                self.deliver_message(user, callback_data)

        except Exception as e:
            logger.critical(f"Couldn't process update: {e}", exc_info=True)

            if user:
                self.deliver_message(user, "Something went wrong")
