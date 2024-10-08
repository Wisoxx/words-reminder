import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from translations import translate
from ._query_actions import QUERY_ACTIONS
import json
from logger import logging

logger = logging.getLogger(__name__)


class Bot:
    def __init__(self, token):
        self.bot = telepot.Bot(token)
        self.update = None

    def __getattr__(self, name):
        return getattr(self.bot, name)

    @staticmethod
    def get_cancel_button(lang):
        """Create cancel button with inline keyboard."""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"❌ {translate(lang, 'cancel')}", callback_data=json.dumps([QUERY_ACTIONS.CANCEL]))],
        ])

    def manage_cancel_buttons(self, user, new_cancel_button_id):
        """Manage the removal of old cancel buttons when a new one is sent."""
        pass

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

    def handle_update(self, update):
        logger.debug('Received update: {}'.format(update))
        self.update = update

        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            if "text" in update["message"]:
                text = update["message"]["text"]
                self.deliver_message(chat_id, "From the web: you said '{}'".format(text))
            else:
                self.deliver_message(chat_id, "From the web: sorry, I didn't understand that kind of message")

        elif "callback_query" in update:
            chat_id = update["callback_query"]["message"]["chat"]["id"]
            callback_data = update["callback_query"]["data"]
            self.deliver_message(chat_id, callback_data)