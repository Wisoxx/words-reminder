import json
import database as db
from ._enums import QUERY_ACTIONS, USER_STATES
from ._vocabularies import *
from ._settings import get_user_state, reset_user_state
from ._commands import *
from collections import namedtuple
from router import get_route
from logger import setup_logger


logger = setup_logger(__name__)


def handle_message(self, user, update):
    if "text" in update["message"]:
        text = update["message"]["text"]
        # trigger = "text"
        # command = None
        # state = None
        # query_action = None
        #
        # if text.startswith("/"):
        #     command = text.split()[0]
        # else:
        #     state = get_user_state(user)
        #
        # function, action, cancel_button = get_route(trigger, state, query_action, command)
        # match action:
        #     case "send":
        #         if cancel_button:
        #             text, lang = function(user, update)
        #             self.deliver_message(user, text, add_cancel_button=True, lang=lang)
        #         else:
        #             text, reply_markup = function(user, update)
        #             self.deliver_message(user, text, reply_markup=reply_markup)
        #
        #     case "edit":
        #         text, reply_markup = function(user, update)
        #         self.editMessageText((user, msg_id), text, parse_mode="HTML", reply_markup=reply_markup)
        #
        #     case "popup":
        #         function.call(user, update)
        #
        #     case _:
        #         raise ValueError(f"Unknown action {action}")
        # # self.process_user_action(user, text)

    else:
        self.deliver_message(user, "From the web: sorry, I didn't understand that kind of message")


def process_user_action(self, user, text):
    match get_user_state(user):
        # case USER_STATES.NO_STATE.value:
        #     text, reply_markup = WordManager.add_word(user, text)
        #     self.deliver_message(user, text, reply_markup=reply_markup)
        #
        # case USER_STATES.DELETE_WORD.value:
        #     text, reply_markup = WordManager.delete_word_finalize(user, text)
        #     self.deliver_message(user, text, reply_markup=reply_markup)
        #
        # case USER_STATES.CREATE_VOCABULARY.value:
        #     text, reply_markup = VocabularyManager.create_vocabulary_finalize(user, text)
        #     self.deliver_message(user, text, reply_markup=reply_markup)
        #
        # case USER_STATES.DELETE_VOCABULARY_INPUT.value:
        #     text, reply_markup = VocabularyManager.delete_vocabulary_input(user, text)
        #     self.deliver_message(user, text, reply_markup=reply_markup)

        case _:
            raise ValueError(f"Unknown user state: {user}")


def handle_callback_query(self, user,  update):
    callback_data = json.loads(update["callback_query"]["data"])
    action = callback_data[0]
    msg_id = update["callback_query"]["message"]["message_id"]

    match action:
        case QUERY_ACTIONS.CANCEL.value:
            reset_user_state(user)
            self.deliver_message(user, "Successfully cancelled")
        # case QUERY_ACTIONS.MENU.value:
        #     text, reply_markup = construct_menu_page(user)
        #     self.editMessageText((user, msg_id), text, parse_mode="HTML", reply_markup=reply_markup)
        # case QUERY_ACTIONS.MENU_VOCABULARIES.value:
        #     text, reply_markup = VocabularyManager.construct_vocabulary_page(user)
        #     self.editMessageText((user, msg_id), text, parse_mode="HTML", reply_markup=reply_markup)
        # case QUERY_ACTIONS.MENU_WORDS.value | QUERY_ACTIONS.CHANGE_WORDS_PAGE.value:
        #     PageData = namedtuple('PageData', ['vocabulary_id', 'page'], defaults=[None, 0])
        #     data = PageData(*callback_data[1:])
        #     text, reply_markup = WordManager.construct_word_page(user, data.vocabulary_id, data.page)
        #     self.editMessageText((user, msg_id), text, parse_mode="HTML", reply_markup=reply_markup)
        # case QUERY_ACTIONS.DELETE_WORD.value:
        #     # when message stays the same, callback_query needs to be answered, because it will keep showing as loading
        #     self.answerCallbackQuery(update["callback_query"]["id"])
        #     text, lang = WordManager.delete_word_start(user)
        #     self.deliver_message(user, text, add_cancel_button=True, lang=lang)
        # case QUERY_ACTIONS.CREATE_VOCABULARY.value:
        #     self.answerCallbackQuery(update["callback_query"]["id"])
        #     text, lang = VocabularyManager.create_vocabulary_start(user)
        #     self.deliver_message(user, text, add_cancel_button=True, lang=lang)
        # case QUERY_ACTIONS.DELETE_VOCABULARY.value:
        #     self.answerCallbackQuery(update["callback_query"]["id"])
        #     text, lang = VocabularyManager.delete_vocabulary_start(user)
        #     self.deliver_message(user, text, add_cancel_button=True, lang=lang)
        # case QUERY_ACTIONS.DELETE_VOCABULARY_CONFIRM.value:
        #     text, reply_markup = VocabularyManager.delete_vocabulary_confirmed(user)
        #     self.editMessageText((user, msg_id), text, parse_mode="HTML", reply_markup=reply_markup)
        # case QUERY_ACTIONS.DELETE_VOCABULARY_DECLINE.value:
        #     text, reply_markup = VocabularyManager.delete_vocabulary_declined(user)
        #     self.editMessageText((user, msg_id), text, parse_mode="HTML", reply_markup=reply_markup)
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
