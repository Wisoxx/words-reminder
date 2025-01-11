import json
import database as db
from .temp_manager import get_user, get_user_parameters, set_user_state, reset_user_state
from ._vocabularies import _get_vocabulary_name, change_vocabulary_start, _set_current_vocabulary
from .utils import html_wrapper, escape_html, get_timestamp, pad
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from ._enums import TaskStatus, QUERY_ACTIONS, TEMP_KEYS, USER_STATES
from translations import translate
from router import route
from logger import setup_logger

logger = setup_logger(__name__)

MAX_MESSAGE_LENGTH = 4096
WORDS_PER_PAGE = 15


####################################################################################################################
#                                                DATABASE INTERACTIONS
####################################################################################################################
def _add_word(user, vocabulary_id, word, meaning=None, timestamp=None):
    timestamp = timestamp or get_timestamp()
    word_id = db.Words.add({"user_id": user, "vocabulary_id": vocabulary_id, "word": word, "meaning": meaning,
                            "timestamp": timestamp})[1]
    if word_id > 0:
        logger.info(f'User {user} added word #{word_id} to vocabulary #{vocabulary_id}')
    return word_id


def _delete_word(user, word_id=None, vocabulary_id=None, word=None):
    """
    Deletes a word based on the given conditions. word_id or user and vocabulary_id and word are required.

    :param user: The ID of the user
    :param word_id: Unique identifier of the word (optional)
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

    status = db.Words.delete(conditions)
    if status:
        logger.info(f'User {user} deleted word word_id={word_id}, vocabulary_id={vocabulary_id}, word="{word}"')
        return TaskStatus.SUCCESS
    return TaskStatus.FAILURE


def _get_word_info(word_id):
    return db.Words.get({"word_id": word_id}, include_column_names=True)


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


def _get_user_words(user, vocabulary_id, include_timestamp=False, reverse=False):
    select = "SELECT word, meaning, timestamp FROM words" if include_timestamp else "SELECT word, meaning FROM words"
    order = "DESC" if reverse else "ASC"
    return db.Words.get({"user_id": user, "vocabulary_id": vocabulary_id}, custom_select=select,
                        order_by="word_id", sort_direction=order, force_2d=True)


def _get_old_words(user: int, vocabulary_id: int, limit: int) -> list[tuple[str, str]]:
    """
    Fetches the oldest words (up to the specified limit) from the specified vocabulary for a given user,
    and updates their timestamp to the current time.

    :param user: The ID of the user for whom the words are being retrieved.
    :param vocabulary_id: The ID of the vocabulary from which the words will be fetched.
    :param limit: The maximum number of oldest words to retrieve.
    :return:  A list of tuples where each tuple contains a word and its corresponding meaning.
    """
    current_timestamp = get_timestamp()

    words = db.Words.get(
        conditions={
            "user_id": user,
            "vocabulary_id": vocabulary_id
        },
        limit=limit,
        order_by="timestamp",
        sort_direction="ASC",
        custom_select="SELECT word, meaning FROM words",
        force_2d=True,
        include_column_names=True
    )

    word_list = [(word.word, word.meaning) for word in words]

    for word in words:
        db.Words.set(
            conditions={
                "user_id": user,
                "vocabulary_id": vocabulary_id,
                "word": word.word
            },
            new_values={
                "timestamp": current_timestamp
            }
        )

    return word_list


####################################################################################################################
#                                                     OTHER
####################################################################################################################


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


@route(trigger="text", state=USER_STATES.NO_STATE.value, action="send")
def add_word(update):
    """
    Adds a new word to the current vocabulary
    :param update: update containing user input in form "{word} - {meaning}". If " - " is absent, then the whole text
    is treated as one word
    :return: text, reply_markup to be sent to user
    """
    user = get_user(update)
    text = update["message"]["text"]
    logger.debug(f"Adding user {user} word '{text}'")
    parameters = get_user_parameters(user)
    lang = parameters.language
    current_vocabulary_id = parameters.current_vocabulary_id
    current_vocabulary_name = _get_vocabulary_name(current_vocabulary_id)

    if " - " in text:
        word, meaning = text.split(" - ", 1)
    else:
        word = text
        meaning = None

    word_id = _add_word(user, current_vocabulary_id, word, meaning)
    if word_id == 0:
        text = f'You already have "{escape_html(word)}" in "{escape_html(current_vocabulary_name)}"'
        reply_markup = None
    else:
        text = f'Successfully added "{escape_html(word)}" to "{escape_html(current_vocabulary_name)}"'
        reply_markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=f'      🗑 {translate(lang, "delete")}      ',
                                     callback_data=json.dumps([QUERY_ACTIONS.DELETE_SPECIFIC_WORD.value, word_id])),
            ]
        ])

    return text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.DELETE_WORD.value, action="send", cancel_button=True)
def delete_word_start(update):
    """
    Enables required state to delete word which is next user's text input.
    :param update: update from user who wants to delete a word
    :return: text to be sent to user and language of cancel button. Should be sent with cancel button
    """
    user = get_user(update)
    logger.debug(f"User {user} initiated word deletion")
    parameters = get_user_parameters(user)
    lang = parameters.language

    text = "Send me the word you want to delete"
    set_user_state(user, USER_STATES.DELETE_WORD.value)
    return text, lang


@route(trigger="text", state=USER_STATES.DELETE_WORD.value, action="send")
def delete_word_finalize(update):
    """
    Deletes text input from current user's vocabulary. Is activated by a text message while a specific user state.
    :param update: update from user whose vocabulary is being deleted
    :return: text, reply_markup to be sent to user
    """
    user = get_user(update)
    text = update["message"]["text"]
    logger.debug(f"User {user} provided a word for deletion")
    parameters = get_user_parameters(user)
    lang = parameters.language
    vocabulary_id = parameters.current_vocabulary_id
    vocabulary_name = _get_vocabulary_name(vocabulary_id)
    word = text
    meaning = _get_word_meaning(user=user, vocabulary_id=vocabulary_id, word=word)

    match _delete_word(user=user, vocabulary_id=vocabulary_id, word=word):
        case TaskStatus.SUCCESS:
            text = f'Successfully deleted "{escape_html(word)}" from "{escape_html(vocabulary_name)}"'
            reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text=f'      ↪️ {translate(lang, "add_back")}      ',
                                         callback_data=json.dumps([QUERY_ACTIONS.ADD_SPECIFIC_WORD.value,
                                                                   vocabulary_id,
                                                                   word,
                                                                   meaning], ensure_ascii=False)),
                ]
            ])
        case TaskStatus.FAILURE:
            text = f'"{escape_html(word)}" was not found in "{escape_html(vocabulary_name)}"'
            reply_markup = None

        case _:
            raise ValueError("Unsupported status")
    reset_user_state(user)
    return text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.WORDS_CHANGE_VOCABULARY.value, action="edit")
def words_change_vocabulary(update):
    return change_vocabulary_start(update, next_query_action=QUERY_ACTIONS.WORDS_VOCABULARY_CHOSEN.value,
                                   back_button_action=QUERY_ACTIONS.MENU_WORDS.value)


@route(trigger="callback_query", query_action=QUERY_ACTIONS.WORDS_VOCABULARY_CHOSEN.value, action="edit")
def words_vocabulary_chosen(update):
    user = get_user(update)
    callback_data = json.loads(update["callback_query"]["data"])
    vocabulary_id = callback_data[1]
    _set_current_vocabulary(user, vocabulary_id)
    return construct_word_page(update)


@route(trigger="callback_query", query_action=QUERY_ACTIONS.CHANGE_WORDS_PAGE.value, action="edit")
@route(trigger="callback_query", query_action=QUERY_ACTIONS.MENU_WORDS.value, action="edit")
def construct_word_page(update, vocabulary_id=None, page=None):
    user = get_user(update)
    callback_data = json.loads(update["callback_query"]["data"])
    parameters = get_user_parameters(user)

    if not vocabulary_id and not page:
        if len(callback_data) == 3:
            vocabulary_id = callback_data[1]
            page = callback_data[2]
        else:
            vocabulary_id = vocabulary_id or parameters.current_vocabulary_id
            page = page or 0
    elif not vocabulary_id:
        vocabulary_id = parameters.current_vocabulary_id
    elif not page:
        page = 0

    lang = parameters.language

    vocabulary_name = _get_vocabulary_name(vocabulary_id)
    hide_meaning = parameters.hide_meaning
    logger.debug(f"User {user} opened word page #{page} of a vocabulary #{vocabulary_id}")

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
                                 callback_data=json.dumps([QUERY_ACTIONS.WORDS_CHANGE_VOCABULARY.value])),
            InlineKeyboardButton(text='      ━     ', callback_data=json.dumps([QUERY_ACTIONS.DELETE_WORD.value])),
        ],
        [
            InlineKeyboardButton(text='      ↩️      ', callback_data=json.dumps([QUERY_ACTIONS.MENU.value])),
            InlineKeyboardButton(text='      ℹ️      ',
                                 callback_data=json.dumps([QUERY_ACTIONS.SHOW_INFO.value, "info_words"])),
        ]
    ]

    words = _get_user_words(user, vocabulary_id, reverse=True)

    if len(words) == 0:
        text = heading + "*🦗crickets noises🦗*"
    else:
        pages = _word_list_to_pages(words, hide_meaning, max_length=MAX_MESSAGE_LENGTH - 50,
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

        footer = f"\n{pad(' ' * 36, str(page + 1), True)}/{len(pages)}"
        text = heading + pages[page] + footer
    keyboard = InlineKeyboardMarkup(inline_keyboard=[page_buttons] + menu_buttons)
    return text, keyboard
