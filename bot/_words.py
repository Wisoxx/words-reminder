import json
import database as db
from ._settings import get_user_parameters
from ._vocabularies import get_vocabulary_name
from ._utils import html_wrapper, escape_html, get_timestamp
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from ._enums import TaskStatus, QUERY_ACTIONS, TEMP_KEYS, USER_STATES
from ._response_format import Response


class WordManager:
    ####################################################################################################################
    #                                                DATABASE INTERACTIONS
    ####################################################################################################################
    @staticmethod
    def _add_word(user, vocabulary_id, word, meaning=None, timestamp=None):
        timestamp = timestamp or get_timestamp()
        status = db.Words.add({"user_id": user, "vocabulary_id": vocabulary_id, "word": word, "meaning": meaning,
                               "timestamp": timestamp})[0]
        if status:
            return TaskStatus.SUCCESS
        return TaskStatus.DUPLICATE

    @staticmethod
    def _delete_word(word_id=None, user=None, vocabulary_id=None, word=None):
        """
        Deletes a word based on the given conditions. word_id or user and vocabulary_id and word are required.

        :param word_id: Unique identifier of the word (optional)
        :param user: The ID of the user (required if word_id is not given)
        :param vocabulary_id: The vocabulary the word belongs to (required if word_id is not given)
        :param word: The word to delete (required if word_id is not given)
        :return: bool indicating success
        """
        if word_id:
            conditions = {"word_id": word_id}
        elif user and vocabulary_id and word:
            conditions = {"user_id": user, "vocabulary_id": vocabulary_id, "word": word}
        else:
            raise ValueError("You must provide either word_id, or user_id, vocabulary_id, and word.")

        return db.Words.delete(conditions)

    @staticmethod
    def _get_word_meaning(word_id=None, user=None, vocabulary_id=None, word=None):
        """
        Returns the meaning of the given word based on the given conditions. word_id or user and vocabulary_id and word
        are required.

        :param word_id: Unique identifier of the word (optional)
        :param user: The ID of the user (required if word_id is not given)
        :param vocabulary_id: The vocabulary the word belongs to (required if word_id is not given)
        :param word: The word to delete (required if word_id is not given)
        :return: str meaning of the given word
        """
        if word_id:
            conditions = {"word_id": word_id}
        elif user and vocabulary_id and word:
            conditions = {"user_id": user, "vocabulary_id": vocabulary_id, "word": word}
        else:
            raise ValueError("You must provide either word_id, or user_id, vocabulary_id, and word.")

        word_info = db.Words.get(conditions, include_column_names=True)

        if word_info:
            return word_info.meaning
        return None

    @staticmethod
    def _get_user_words(user, vocabulary_id, include_timestamp=False, reverse=False):
        select = "SELECT word, meaning, timestamp FROM words" if include_timestamp else "SELECT word, meaning FROM words"
        order = "DESC" if reverse else "ASC"
        return db.Words.get({"user_id": user, "vocabulary_id": vocabulary_id}, custom_select=select,
                            order_by="word_id", sort_direction=order)

    @staticmethod
    def _get_old_words(user, vocabulary_id, limit):
        pass

    ####################################################################################################################
    #                                                BOT ACTIONS
    ####################################################################################################################
    @classmethod
    def add_word(cls, user, text):
        parameters = get_user_parameters(user)
        lang = parameters.language
        current_vocabulary_id = parameters.current_vocabulary_id
        current_vocabulary_name = get_vocabulary_name(current_vocabulary_id)

        word, meaning = text.split(" - ")

        match cls._add_word(user, current_vocabulary_id, word, meaning):
            case TaskStatus.DUPLICATE:
                text = f"You already have {escape_html(word)} in {escape_html(current_vocabulary_name)}"
                reply_markup = None

            case TaskStatus.SUCCESS:
                text = f"Successfully added {escape_html(word)} to {escape_html(current_vocabulary_name)}"
                reply_markup = None  # TODO add cancel button

            case _:
                raise ValueError("Unsupported status")
        return Response(text, reply_markup)

    @staticmethod
    def construct_word_page(user, vocabulary_id, page):
        parameters = get_user_parameters(user)
        lang = parameters.language
        current_vocabulary_name = get_vocabulary_name(vocabulary_id)

        if not current_vocabulary_name:
            raise ValueError("Couldn't retrieve current vocabulary name")

        heading = html_wrapper(
            "==================================\n" +
            escape_html(current_vocabulary_name) + "\n" +
            "==================================\n\n"
            , "b")

        buttons = []

        menu_buttons = [
            [
                InlineKeyboardButton(text='      📙      ',
                                     callback_data=json.dumps([QUERY_ACTIONS.CHANGE_VOCABULARY.value,
                                                               QUERY_ACTIONS.MENU_WORDS.value])),
                InlineKeyboardButton(text='      ━     ', callback_data=json.dumps([QUERY_ACTIONS.DELETE_WORD.value])),
            ],
            [
                InlineKeyboardButton(text='      ↩️      ', callback_data=json.dumps([QUERY_ACTIONS.MENU.value])),
                InlineKeyboardButton(text='      ℹ️      ',
                                     callback_data=json.dumps([QUERY_ACTIONS.SHOW_INFO.value, "info_words"])),
            ]
        ]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        # TODO finish
