import json
import database as db
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from ._settings import get_user_parameters, set_user_state, reset_user_state
from .temp_manager import *
from ._enums import TaskStatus, QUERY_ACTIONS, TEMP_KEYS, USER_STATES
from .utils import html_wrapper, escape_html
from ._response_format import Response
from translations import translate
from logger import setup_logger


logger = setup_logger(__name__)


class VocabularyManager:
    ####################################################################################################################
    #                                                DATABASE INTERACTIONS
    ####################################################################################################################
    @staticmethod
    def _set_current_vocabulary(user, vocabulary_id):
        if db.Users.set({"user_id": user}, {"current_vocabulary_id": vocabulary_id}):
            logger.info(f"User {user} changed vocabulary to #{vocabulary_id}")
            return TaskStatus.SUCCESS
        return TaskStatus.FAILURE

    @staticmethod
    def _create_vocabulary(user, vocabulary_name):
        # Note: db sets new vocabulary as current
        status, vocabulary_id = db.Vocabularies.add({"vocabulary_name": vocabulary_name, "user_id": user})
        if status:
            logger.info(f"User {user} created vocabulary #{vocabulary_id}")
        return vocabulary_id

    @staticmethod
    def _delete_vocabulary(user, vocabulary_id=None, vocabulary_name=None):
        """
        Deletes a vocabulary based on the given conditions. vocabulary_id or user and vocabulary_name are required.

        :param vocabulary_id: Unique identifier of the vocabulary (optional)
        :param user: The ID of the user
        :param vocabulary_name: The name of the vocabulary to delete (required if vocabulary_id is not given)
        :return: bool indicating success
        """
        # Note: when deleting current vocabulary, db will try to change vocabulary to another one
        if vocabulary_id:
            conditions = {"vocabulary_id": vocabulary_id}
        elif vocabulary_name:
            conditions = {"user_id": user, "vocabulary_name": vocabulary_name}
        else:
            raise ValueError("You must provide either vocabulary_id, or user_id and vocabulary_name.")

        result = db.Vocabularies.delete(conditions)
        if result:
            logger.info(f"User {user} deleted vocabulary #{vocabulary_id}")

        if get_user_parameters(user).current_vocabulary_id is None:
            logger.info(f"User {user} has no vocabularies")
            return TaskStatus.NO_VOCABULARY

        if result:
            return TaskStatus.SUCCESS
        return TaskStatus.FAILURE

    @staticmethod
    def _get_vocabulary_list(user):
        """
        Fetches vocabularies for a user and returns a dictionary mapping vocabulary_id to vocabulary_name.

        :param user: The user ID to fetch vocabularies for.
        :return: A dictionary {vocabulary_id: vocabulary_name}.
        """
        vocabularies = db.Vocabularies.get({"user_id": user}, force_2d=True, include_column_names=True)

        if vocabularies:
            return {vocabulary.vocabulary_id: vocabulary.vocabulary_name for vocabulary in vocabularies}
        else:
            return {}

    @staticmethod
    def _get_vocabulary_name(vocabulary_id):
        name = db.Vocabularies.get({"vocabulary_id": vocabulary_id}, include_column_names=True)
        if name:
            return name.vocabulary_name
        return None

    @staticmethod
    def _get_vocabulary_id(user, vocabulary_name):
        entry = db.Vocabularies.get({"user_id": user, "vocabulary_name": vocabulary_name},
                                   include_column_names=True)
        if entry:
            return entry.vocabulary_id
        return None

    ####################################################################################################################
    #                                                     OTHER
    ####################################################################################################################

    @staticmethod
    def _vocabulary_list_to_text(values, current_vocabulary, lang):
        text = ""
        for vocabulary, words_number in values:
            vocabulary = escape_html(vocabulary)

            if vocabulary == current_vocabulary:
                vocabulary = html_wrapper(vocabulary, "u")  # Underline the current vocabulary
            text += f'"{vocabulary}"  —  {words_number} words\n'
        return text

    ####################################################################################################################
    #                                                  BOT ACTIONS
    ####################################################################################################################

    @classmethod
    def create_vocabulary_start(cls, user):
        """
        Enables required state to create vocabulary from next user's text input. Is activated by callback query.
        :param user:
        :return: text to be sent to user and language of cancel button. Should be sent with cancel button
        """
        logger.debug(f"User {user} initiated vocabulary creation")
        parameters = get_user_parameters(user)
        lang = parameters.language

        text = "How do you want to name your vocabulary?"
        set_user_state(user, USER_STATES.CREATE_VOCABULARY.value)
        return text, lang

    @classmethod
    def create_vocabulary_finalize(cls, user, text):
        """
        Creates a new vocabulary belonging to user. Is activated by a text message while a specific user state.
        :param user: user_id to whom vocabulary will belong to
        :param text: user inputted vocabulary_name
        :return: Response(text, reply_markup) - named tuple containing text and reply_markup to be sent to user
        """
        logger.debug(f"User {user} is trying to create vocabulary '{text}'")
        parameters = get_user_parameters(user)
        lang = parameters.language
        vocabulary_name = text

        vocabulary_id = cls._create_vocabulary(user, vocabulary_name)
        if vocabulary_id == 0:
            text = f'You already have vocabulary named "{escape_html(vocabulary_name)}". Try something else'
            reply_markup = None
        else:
            text = f'Successfully create vocabulary "{escape_html(vocabulary_name)}"'
            reply_markup = None
            reset_user_state(user)

        return Response(text, reply_markup)

    @classmethod
    def delete_vocabulary_start(cls, user):
        """
        Enables required state to delete vocabulary which name is next user's text input. Is activated by callback query
        :param user: user_id of user who wants to delete a vocabulary
        :return: text to be sent to user and language of cancel button. Should be sent with cancel button
        """
        logger.debug(f"User {user} initiated word deletion")
        parameters = get_user_parameters(user)
        lang = parameters.language

        text = "Send me the word you want to delete"
        set_user_state(user, USER_STATES.DELETE_VOCABULARY_INPUT.value)
        return text, lang

    @classmethod
    def delete_vocabulary_input(cls, user, text):
        """
        Saves vocabulary_name and asks to confirm deletion. Is activated by a text message while a specific user state.
        :param user: user_id of user who wants to delete a vocabulary
        :return: text to be sent to user and language of cancel button. Should be sent with cancel button
        """
        logger.debug(f"User {user} provided a word for deletion")
        parameters = get_user_parameters(user)
        lang = parameters.language
        vocabulary_name = text
        vocabulary_id = cls._get_vocabulary_id(user, vocabulary_name)

        if vocabulary_id:
            set_temp(user, TEMP_KEYS.VOCABULARY.value, vocabulary_id)

            text = (f"Are you sure you want to permanently delete \"{vocabulary_name}\" and everything associated with"
                    f" it including words and reminders?")
            reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text=f'      ✅      ',
                                         callback_data=json.dumps([QUERY_ACTIONS.CONFIRM.value,], ensure_ascii=False)),
                    InlineKeyboardButton(text=f'      ❌      ',
                                         callback_data=json.dumps([QUERY_ACTIONS.DECLINE.value, ], ensure_ascii=False)),
                ]
            ])
            set_user_state(user, USER_STATES.DELETE_VOCABULARY_CONFIRMATION.value)
        else:
            text = f'You don\'t have a vocabulary named "{escape_html(vocabulary_name)}"'
            reply_markup = None
            reset_user_state(user)
        return Response(text, reply_markup)

    @classmethod
    def delete_vocabulary_confirmed(cls, user):
        """
        Deletes text input from current user's vocabulary. Is activated by callback query
        :param user: user_id from whose vocabulary is being deleted
        :return: Response(text, reply_markup) - named tuple containing text and reply_markup to be sent to user
        """
        logger.debug(f"User {user} confirmed vocabulary deletion")
        parameters = get_user_parameters(user)
        lang = parameters.language
        vocabulary_id = pop_temp(user, TEMP_KEYS.VOCABULARY.value)
        vocabulary_name = cls._get_vocabulary_name(vocabulary_id)

        match cls._delete_vocabulary(user, vocabulary_id=vocabulary_id):
            case TaskStatus.SUCCESS:
                text = f'Successfully deleted vocabulary "{escape_html(vocabulary_name)}"'
                reply_markup = None
            case TaskStatus.FAILURE:
                raise FileNotFoundError(f'Failed to delete vocabulary #{vocabulary_id} "{escape_html(vocabulary_name)}"')

            case _:
                raise ValueError("Unsupported status")
        reset_user_state(user)
        return Response(text, reply_markup)

    @classmethod
    def delete_word_declined(cls, user, text):
        pass

    @classmethod
    def construct_vocabulary_page(cls, user):
        parameters = get_user_parameters(user)
        lang = parameters.language
        current_vocabulary_id = parameters.current_vocabulary_id
        vocabularies = cls._get_vocabulary_list(user)
        current_vocabulary_name = vocabularies[current_vocabulary_id]

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='      ━      ', callback_data=json.dumps([QUERY_ACTIONS.DELETE_VOCABULARY.value])),
                InlineKeyboardButton(text='      📙     ', callback_data=json.dumps([QUERY_ACTIONS.CHANGE_VOCABULARY.value, QUERY_ACTIONS.MENU_VOCABULARIES.value])),
                InlineKeyboardButton(text='      ✚      ', callback_data=json.dumps([QUERY_ACTIONS.CREATE_VOCABULARY.value])),
            ],
            [
                InlineKeyboardButton(text='      ↩️      ', callback_data=json.dumps([QUERY_ACTIONS.MENU.value])),
                InlineKeyboardButton(text='      ℹ️      ', callback_data=json.dumps([QUERY_ACTIONS.SHOW_INFO.value, "info_vocabularies"])),
            ]
        ])

        heading = html_wrapper(
            escape_html(
                "<><><><><><><><><><><><><><><><><><><>\n" +
                f"{' ' * 30}Vocabularies\n" +
                "<><><><><><><><><><><><><><><><><><><>"
            ),
            'b')
        text = ""

        values = []
        for vocabulary_id in vocabularies:
            word_count = db.Words.count_where({"vocabulary_id": vocabulary_id})
            vocabulary_name = vocabularies[vocabulary_id]
            values.append((vocabulary_name, word_count))

        if not values:
            text += "You have no vocabularies."
        else:
            text += cls._vocabulary_list_to_text(values, current_vocabulary_name, lang)

        return Response(heading + '\n' + text, keyboard)
