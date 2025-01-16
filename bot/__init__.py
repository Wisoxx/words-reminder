import json
import database as db
import telepot
from time import sleep
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from translations import translate, languages
from ._enums import QUERY_ACTIONS, TEMP_KEYS, USER_STATES
from .temp_manager import get_user, get_user_parameters, get_user_state, set_user_state, reset_user_state, get_temp, \
    check_missing_setup
import bot._commands
import bot._words
import bot._reminders
from ._vocabularies import create_vocabulary_start
from ._settings import change_language_start, change_timezone_start
from ._enums import QUERY_ACTIONS, TEMP_KEYS
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
        if text == "":
            return
        logger.debug(f"Sending message with parameters: {locals()}")  # Logs all parameters

        if reply_markup:
            final_reply_markup = reply_markup
        elif add_cancel_button:
            final_reply_markup = self.get_cancel_button(lang)
        else:
            final_reply_markup = {'remove_keyboard': True}

        response = self.sendMessage(user, text, reply_to_message_id=reply_to_msg_id, reply_markup=final_reply_markup,
                                    parse_mode=PARSE_MODE)

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
            sleep(34)  # Telegram allows 30 messages per second
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
            sleep(34)  # Telegram allows 30 messages per second
        logger.info(f"Sent to {len(users)} users")

    @staticmethod
    def is_allowed_update(missing, trigger, state, query_action, command):
        if any((
                missing is None,  # No missing setup
                missing == "user",  # allow user setup
                trigger == "text" and command == "/start",  # Always allow /start
                trigger == "chat_member",
                all((  # Allow language selection
                        missing == "lang",
                        trigger == "callback_query",
                        query_action == QUERY_ACTIONS.LANGUAGE_CHOSEN.value
                )),
                all((  # Allow vocabulary creation
                        missing == "vocabulary",
                        trigger == "text",
                        state == USER_STATES.CREATE_VOCABULARY.value
                )),
                all((  # Allow timezone setup
                        missing == "timezone",
                        trigger == "callback_query",
                        query_action in {QUERY_ACTIONS.PICK_TIME.value, QUERY_ACTIONS.SET_UP_TIMEZONE_FINALIZE.value}
                )),
        )):
            return True
        return False

    def set_up(self, missing, update):
        user = get_user(update)
        match missing:
            case "lang":
                text, reply_markup = change_language_start(update, return_to_menu=False)
                self.deliver_message(user, text, reply_markup=reply_markup)

            case "vocabulary":
                text, _ = create_vocabulary_start(update)
                self.deliver_message(user, text)

            case "timezone":
                text, reply_markup = change_timezone_start(
                    update, next_query_action=QUERY_ACTIONS.SET_UP_TIMEZONE_FINALIZE.value, back_button_action=None)
                self.deliver_message(user, text, reply_markup=reply_markup)

            case _:
                raise ValueError("Unrecognized missing setup stage")

    def execute_action(self, user, action, function=None, update=None, callback_query_id=None, msg_id=None, text=None,
                       reply_markup=None, lang=None, add_cancel_button=False, answer_callback_query=True, inner=False):
        """
        Executes an action based on the provided parameters. It handles different types of actions including sending,
        editing, and managing multiple actions. It also ensures callback queries are answered as necessary and
        prevents nested recursion in case of multi-action calls.

        Args:
            user (User): The user who the action is performed for.
            action (str): The action to be performed. Valid actions include:
                - "send": Sends a message.
                - "edit": Edits an existing message.
                - "edit_markup": Edits the reply markup of an existing message.
                - "multi_action": Executes multiple actions in sequence.
                - None: Executes the function passed in as the `function` argument.
            function (callable, optional): A function that returns the content (text, reply_markup, etc.) to be
            processed for the action.
            update (Update, optional): The update object containing information about the user interaction.
            callback_query_id (str, optional): The callback query ID for answering callback queries.
            msg_id (int, optional): The message ID of the message to be edited or whose reply markup is to be edited.
            text (str, optional): The text content to send or use in editing.
            reply_markup (dict, optional): The reply markup to attach to the message (keyboard, inline buttons).
            lang (str, optional): The language code to determine the language of the message.
            add_cancel_button (bool, optional): Whether to add a cancel button to the message.
            answer_callback_query (bool, optional): Whether to answer the callback query. Defaults to True.
            inner (bool, optional): Indicates whether the action is part of a nested `multi_action` call. Prevents
            further recursion.

        Raises:
            ValueError: If an unsupported action type is provided or if required parameters (e.g., msg_id) are missing.
            TypeError: If the result of a `multi_action` is not a list of dicts.
            RecursionError: If nested `multi_action` actions are attempted.

        Processes:
            - Sends a message if the action is "send" or "multi_action" with a send action.
            - Edits a message if the action is "edit" or "edit_markup".
            - Prevents nested `multi_action` calls to avoid deep recursion.
            - Executes the provided function if no specific action is required.
        """
        # not answering callback query leads to long waiting animation, but some actions don't require it
        if callback_query_id and answer_callback_query and action not in {"edit", "edit_markup",
                                                                          "popup",  # answers it later
                                                                          "multi_action"}:  # inner call will answer
            self.answerCallbackQuery(callback_query_id)

        logger.debug(f"Executing action: {action} for user: {user}")
        result = function(update) if function else None

        match action:
            case "send":
                if add_cancel_button:
                    text, lang = result if result else (text, lang)
                    self.deliver_message(user, text, add_cancel_button=True, lang=lang)
                else:
                    text, reply_markup = result if result else (text, reply_markup)
                    self.deliver_message(user, text, reply_markup=reply_markup)

            case "edit":
                if not msg_id:
                    raise ValueError("Missing parameter: msg_id for editing message")

                text, reply_markup = result if result else (text, reply_markup)
                self.editMessageText((user, msg_id), text, parse_mode="HTML", reply_markup=reply_markup)

            case "edit_markup":
                if not msg_id:
                    raise ValueError("Missing parameter: msg_id for editing reply markup")

                reply_markup = result if result else reply_markup
                self.editMessageReplyMarkup((user, msg_id), reply_markup=reply_markup)

            case "popup":
                if not callback_query_id:
                    raise ValueError("Missing parameter: callback_query_id for popup action")

                popup_text = result if result else text
                logger.debug(f"Showing popup: {popup_text} to user {user}")
                response = self.answerCallbackQuery(callback_query_id, text=popup_text, show_alert=True)
                logger.debug(f"Popup response: {response}")

            case "multi_action":
                if inner:
                    raise RecursionError("Nested multi_action calls are not allowed")
                if not isinstance(result, list):
                    raise TypeError(f"multi_action must return a list of dicts, got {type(result).__name__} instead.")
                logger.debug(f"Multiple actions: {result}")
                for item in result:
                    if not isinstance(item, dict):
                        raise TypeError(f"Each multi_action entry must be a dict, got {type(item).__name__}.")
                    # Recursively process each action
                    self.execute_action(user, callback_query_id=callback_query_id, msg_id=msg_id, inner=True, **item)

            case None:
                pass  # function has been executed at the beginning and no additional actions are required

            case _:
                raise ValueError(f"Unknown action {action}")

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
            msg_id = None
            if "message" in update:
                if "text" in update["message"]:
                    text = update["message"]["text"]
                    trigger = "text"

                    if text.startswith("/"):
                        command = text.split()[0].lower()
                        command = command if command in {"/start", "/menu", "/help"} else "default"
                        reset_user_state(user)
                    else:
                        state = get_user_state(user)
                else:
                    trigger = "other"
                    reset_user_state(user)

            elif "callback_query" in update:
                trigger = "callback_query"
                query_action = json.loads(update["callback_query"]["data"])[0]
                msg_id = update["callback_query"]["message"]["message_id"]
                callback_query_id = update["callback_query"]["id"]
                reset_user_state(user)

            elif "my_chat_member" in update:
                trigger = "chat_member"
                reset_user_state(user)

            was_missing = check_missing_setup(user)
            logger.debug(f"User {user} has missing setup before update: {was_missing}")
            allowed = self.is_allowed_update(was_missing, trigger, state, query_action, command)
            logger.debug("Update allowed" if allowed else "Update not allowed")

            if not allowed:
                params = get_user_parameters(user)
                if len(params) > 0:
                    lang = params.language
                    if lang in languages:
                        self.deliver_message(user, "Firstly you have to finish the setup!")
                self.set_up(was_missing, update)
                return

            function, action, cancel_button = get_route(trigger, state, query_action, command)
            self.execute_action(user, action, function, update, callback_query_id, msg_id,
                                add_cancel_button=cancel_button)

            if was_missing:
                is_missing = check_missing_setup(user)
                logger.debug(f"User {user} has missing setup after update: {is_missing}")
                if all((
                    is_missing in {"lang", "vocabulary", "timezone"},
                    query_action != QUERY_ACTIONS.PICK_TIME.value,  # picking time is not a finished action
                    trigger != "chat_member",  # texting a user who blocked bot is pointless
                )):
                    self.set_up(is_missing, update)
                elif is_missing is None:  # something was missing and now nothing is
                    lang = get_user_parameters(user).language
                    self.deliver_message(user, "You've finished the setup! To get more information type /help")

        except Exception as e:
            logger.critical(f"Couldn't process update: {e}", exc_info=True)
            logger.critical(f"Update that caused error: {json.dumps(update, indent=4, ensure_ascii=False)}")

            if user:
                try:
                    params = get_user_parameters(user)
                    if len(params) > 0:
                        lang = params.language
                        self.deliver_message(user, translate(lang, "error"))
                except Exception as e_:
                    logger.critical(f"Couldn't notify user {user} about error: {e_}")
                else:
                    logger.info(f"User {user} has been notified about error")
