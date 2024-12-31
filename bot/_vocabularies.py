import json
import database as db
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from ._settings import get_user_parameters
from ._enums import TaskStatus, QUERY_ACTIONS, TEMP_KEYS, USER_STATES
from ._utils import html_wrapper, escape_html


def set_current_vocabulary(user, vocabulary_id):
    if db.Users.set({"user_id": user}, {"current_vocabulary_id": vocabulary_id}):
        return TaskStatus.SUCCESS
    return TaskStatus.FAILURE


def create_vocabulary(user, vocabulary_name):
    # Note: db sets new vocabulary as current
    if db.Vocabularies.add({"vocabulary_name": vocabulary_name, "user_id": user})[0]:
        return TaskStatus.SUCCESS
    return TaskStatus.FAILURE


def delete_vocabulary(user, vocabulary_id=None, vocabulary_name=None):
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

    if get_user_parameters(user)["current_vocabulary_id"] is None:
        return TaskStatus.NO_VOCABULARY

    if result:
        return TaskStatus.SUCCESS
    return TaskStatus.FAILURE


def get_vocabulary_list(user):
    """
    Fetches vocabularies for a user and returns a dictionary mapping vocabulary_id to vocabulary_name.

    :param user: The user ID to fetch vocabularies for.
    :return: A dictionary {vocabulary_id: vocabulary_name}.
    """
    vocabularies = db.Vocabularies.get({"user_id": user})

    # db.Database.get returns not nested row if it's single i.e. row instead of (row)
    if isinstance(vocabularies, tuple):
        vocabularies = [vocabularies]

    if vocabularies:
        return {vocabulary[0]: vocabulary[2] for vocabulary in vocabularies}
    else:
        return {}


def vocabulary_list_to_text(values, current_vocabulary, lang):
    text = ""
    for vocabulary, words_number in values:
        vocabulary = escape_html(vocabulary)

        if vocabulary == current_vocabulary:
            vocabulary = html_wrapper(vocabulary, "u")  # Underline the current vocabulary
        text += f'"{vocabulary}"  —  {words_number} words\n'
    return text


def construct_vocabulary_page(user):
    parameters = get_user_parameters(user)
    lang = parameters["language"]
    current_vocabulary_id = parameters["current_vocabulary_id"]
    vocabularies = get_vocabulary_list(user)
    current_vocabulary_name = vocabularies[current_vocabulary_id]

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text='      ━      ', callback_data=json.dumps([QUERY_ACTIONS.DELETE_VOCABULARY.value])),
            InlineKeyboardButton(text='      📙     ', callback_data=json.dumps([QUERY_ACTIONS.CHANGE_VOCABULARY.value, QUERY_ACTIONS.MENU_VOCABULARIES.value])),
            InlineKeyboardButton(text='      ✚      ', callback_data=json.dumps([QUERY_ACTIONS.ADD_VOCABULARY.value])),
        ],
        [
            InlineKeyboardButton(text='      ↩️      ', callback_data=json.dumps([QUERY_ACTIONS.MENU.value])),
            InlineKeyboardButton(text='      ℹ️      ', callback_data=json.dumps([QUERY_ACTIONS.SHOW_INFO.value])),
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
        text += vocabulary_list_to_text(values, current_vocabulary_name, lang)

    return {"text": heading + '\n' + text, "reply_markup": keyboard}
