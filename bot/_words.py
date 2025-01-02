import json
import database as db
from ._settings import get_user_parameters
from ._vocabularies import get_vocabulary_name
from ._utils import html_wrapper, escape_html, get_timestamp, pad
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from ._enums import TaskStatus, QUERY_ACTIONS, TEMP_KEYS, USER_STATES
from ._response_format import Response


MAX_MESSAGE_LENGTH = 4096
WORDS_PER_PAGE = 15


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
    #                                                     OTHER
    ####################################################################################################################

    @staticmethod
    def _word_list_to_pages(values, hide_meaning, max_length, words_limit):
        """
        Splits a list of word-definition pairs into pages based on max length and word limits.

        :param values: List of tuples containing word and definition.
        :param hide_meaning: Boolean indicating whether to hide the meaning with a spoiler format.
        :param max_length: Maximum character length for each page.
        :param words_limit: Maximum number of words per page.
        :return: List of pages as strings.
        """
        meaning_wrapper = "tg-spoiler" if hide_meaning else ""
        pages = []
        current_page = ""
        current_words_count = 0

        for index, (word, definition) in enumerate(values):
            if definition:
                word_line = (
                    f"{html_wrapper(escape_html(word), 'code')}  —  "
                    f"{html_wrapper(escape_html(definition), meaning_wrapper)}\n"
                )
            else:
                word_line = f"{html_wrapper(escape_html(word), 'code')}\n"

            word_line += '-------------------------------------------------------------\n'

            # Check if adding this word will exceed max_length or words_limit
            if len(current_page) + len(word_line) > max_length or current_words_count + 1 > words_limit:
                # Start a new page if limits are exceeded
                pages.append(current_page)
                current_page = ""
                current_words_count = 0

            # Add word_line to current_page and increment word count
            current_page += word_line
            current_words_count += 1

            # Handle the last page case
            if index == len(values) - 1 and current_page:
                pages.append(current_page)

        return pages

    ####################################################################################################################
    #                                                  BOT ACTIONS
    ####################################################################################################################
    @classmethod
    def add_word(cls, user, text):
        parameters = get_user_parameters(user)
        lang = parameters.language
        current_vocabulary_id = parameters.current_vocabulary_id
        current_vocabulary_name = get_vocabulary_name(current_vocabulary_id)

        if " - " in text:
            word, meaning = text.split(" - ", 1)
        else:
            word = text
            meaning = None

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

    @classmethod
    def construct_word_page(cls, user, vocabulary_id=None, page=0):
        parameters = get_user_parameters(user)
        lang = parameters.language
        vocabulary_id = vocabulary_id or parameters.current_vocabulary_id
        vocabulary_name = get_vocabulary_name(vocabulary_id)
        hide_meaning = parameters.hide_meaning

        if not vocabulary_name:
            raise ValueError("Couldn't retrieve current vocabulary name")

        heading = html_wrapper(
            "==================================\n" +
            escape_html(vocabulary_name) + "\n" +
            "==================================\n\n"
            , "b")

        page_buttons = []
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

        words = cls._get_user_words(user, vocabulary_id, reverse=True)

        if len(words) == 0:
            text = "*🦗crickets noises🦗*"
        else:
            pages = cls._word_list_to_pages(words, hide_meaning, max_length=MAX_MESSAGE_LENGTH - 50,
                                            words_limit=WORDS_PER_PAGE)
            if len(pages) != 1:
                if page > 1:
                    page_buttons.append(InlineKeyboardButton(text='      ⏮️      ',
                                                             callback_data=json.dumps([
                                                                 QUERY_ACTIONS.CHANGE_WORDS_PAGE.value,
                                                                 vocabulary_id,
                                                                 0  # destination
                                                             ])))
                if page > 0:
                    page_buttons.append(InlineKeyboardButton(text='      ◀️️      ',
                                                             callback_data=json.dumps([
                                                                 QUERY_ACTIONS.CHANGE_WORDS_PAGE.value,
                                                                 vocabulary_id,
                                                                 page - 1  # destination
                                                             ])))
                if page < len(pages) - 1:
                    page_buttons.append(InlineKeyboardButton(text='      ▶️      ',
                                                             callback_data=json.dumps([
                                                                 QUERY_ACTIONS.CHANGE_WORDS_PAGE.value,
                                                                 vocabulary_id,
                                                                 page + 1  # destination
                                                             ])))
                if page < len(pages) - 2:
                    page_buttons.append(InlineKeyboardButton(text='      ⏭      ',
                                                             callback_data=json.dumps([
                                                                 QUERY_ACTIONS.CHANGE_WORDS_PAGE.value,
                                                                 vocabulary_id,
                                                                 len(pages) - 1  # destination
                                                             ])))

            footer = f"\n{pad(' '*36, str(page + 1), True)}/{len(pages)}"
            text = heading + pages[page] + footer
        keyboard = InlineKeyboardMarkup(inline_keyboard=page_buttons+menu_buttons)
        return Response(text, keyboard)
