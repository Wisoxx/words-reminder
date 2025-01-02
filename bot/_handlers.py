import json
import database as db
from ._enums import TaskStatus, QUERY_ACTIONS, TEMP_KEYS, USER_STATES
from ._vocabularies import *
from ._menu import *
from ._words import WordManager
from collections import namedtuple
from logger import setup_logger


logger = setup_logger(__name__)


def handle_message(self, user, update):
    if "text" in update["message"]:
        text = update["message"]["text"]
        # commands have bigger priority than other input
        if text.startswith("/start") or text.startswith("/help"):
            username = update.get("message", {}).get("from", {}).get("username", None)
            if not username:
                first_name = update.get("message", {}).get("from", {}).get("first_name", "")
                last_name = update.get("message", {}).get("from", {}).get("last_name", "")
                username = ':' + first_name.lower() + ":" + last_name.lower() + ':'

            if db.Users.add({"user_id": user, "username": username})[0]:
                logger.info(f"New user added: {username}")
            self.deliver_message(user, "start")

        elif text.startswith("/menu"):
            text, reply_markup = construct_menu_page(user)
            self.deliver_message(user, text, reply_markup=reply_markup)

        elif text.startswith("/recall"):
            self.deliver_message(user, "recall")

        elif text.startswith("/test"):
            self.deliver_message(user, "Test Message", add_cancel_button=True, lang="en")

        else:
            self.process_user_action(user, text)

    else:
        self.deliver_message(user, "From the web: sorry, I didn't understand that kind of message")


def process_user_action(self, user, text):
    text, reply_markup = WordManager.add_word(user, text)
    self.deliver_message(user, text, reply_markup=reply_markup)


def handle_callback_query(self, user,  update):
    callback_data = json.loads(update["callback_query"]["data"])
    action = callback_data[0]
    msg_id = update["callback_query"]["message"]["message_id"]

    match action:
        case QUERY_ACTIONS.MENU.value:
            text, reply_markup = construct_menu_page(user)
            self.editMessageText((user, msg_id), text, parse_mode="HTML", reply_markup=reply_markup)
        case QUERY_ACTIONS.MENU_VOCABULARIES.value:
            text, reply_markup = construct_vocabulary_page(user).values()
            self.editMessageText((user, msg_id), text, parse_mode="HTML", reply_markup=reply_markup)
        case QUERY_ACTIONS.MENU_WORDS.value | QUERY_ACTIONS.CHANGE_WORDS_PAGE.value:
            PageData = namedtuple('PageData', ['vocabulary_id', 'page'], defaults=[None, None])
            data = PageData(*callback_data[1:])
            text, reply_markup = WordManager.construct_word_page(user, data.vocabulary_id, data.page)
            self.editMessageText((user, msg_id), text, parse_mode="HTML", reply_markup=reply_markup)
        case _:
            self.deliver_message(user, callback_data)


def handle_chat_member_status(self, user,  update):
    old_status = update["my_chat_member"]["old_chat_member"]["status"]
    new_status = update["my_chat_member"]["new_chat_member"]["status"]

    if old_status == "member" and new_status == "kicked":
        logger.info(f"User {user} has blocked the bot")
        db.Users.delete({"user_id": user})  # all data is linked to user_id and will be deleted too
        logger.info(f"All records of {user} have been deleted")
    elif old_status == "kicked" and new_status == "member":
        logger.info(f"User {user} has unblocked the bot")
