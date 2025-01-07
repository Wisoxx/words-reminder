import json
import database as db
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from ._settings import get_user, get_user_parameters, set_user_state, reset_user_state
from .temp_manager import *
from ._enums import TaskStatus, QUERY_ACTIONS, TEMP_KEYS, USER_STATES
from .utils import html_wrapper, escape_html
from router import route, get_route
from translations import translate
from ._vocabularies import _get_vocabulary_list
import bot._time_picker
from logger import setup_logger

logger = setup_logger(__name__)


####################################################################################################################
#                                                DATABASE INTERACTIONS
####################################################################################################################


def _add_reminder(user, vocabulary_id, time, number_of_words):
    reminder_id = db.Reminders.add({"user_id": user, "vocabulary_id": vocabulary_id, "time": time,
                                    "number_of_words": number_of_words})[1]
    if reminder_id > 0:
        logger.info(f'User {user} added reminder #{reminder_id} to vocabulary #{vocabulary_id}')
    return reminder_id


def _delete_reminder(user, reminder_id=None, vocabulary_id=None, time=None):
    """
    Deletes a word based on the given conditions. word_id or user and vocabulary_id and word are required.

    :param user: The ID of the user
    :param reminder_id: Unique identifier of the reminder (optional)
    :param vocabulary_id: The vocabulary the word belongs to (required if reminder_id is not given)
    :param time: The word to delete (required if reminder_id is not given)
    :return: bool indicating success
    """
    if reminder_id:
        conditions = {"reminder_id": reminder_id}
    elif user and vocabulary_id and time:
        conditions = {"user_id": user, "vocabulary_id": vocabulary_id, "time": time}
    else:
        raise ValueError("You must provide either reminder_id, or user_id, vocabulary_id, and time.")

    status = db.Reminders.delete(conditions)
    if status:
        logger.info(f'User {user} deleted reminder word_id={reminder_id}, vocabulary_id={vocabulary_id}, time="{time}"')
        return TaskStatus.SUCCESS
    return TaskStatus.FAILURE


def _get_reminder_list(user, vocabulary_id):
    """
    Fetches reminders for a user and returns a dictionary mapping time to number_of_words.

    :param user: The user ID to fetch vocabularies for.
    :param vocabulary_id: The vocabulary ID to fetch reminders for.
    :return: A dictionary {time: number_of_words}.
    """
    reminders = db.Reminders.get({"user_id": user, "vocabulary_id": vocabulary_id}, force_2d=True,
                                 include_column_names=True)

    if reminders:
        return {reminder.time: reminder.number_of_words for reminder in reminders}
    else:
        return {}


####################################################################################################################
#                                                     OTHER
####################################################################################################################


def _reminder_list_to_text(reminders: dict) -> str:
    """
    Converts a dictionary of reminders into a formatted text representation.

    :param reminders: A dictionary where keys are times and values are the number of words.
    :return: A formatted string representing the reminders.
    """
    text = ""
    for time, words_number in reminders.items():
        text += f"{time}  —  {words_number} words\n"
    return text


####################################################################################################################
#                                                  BOT ACTIONS
####################################################################################################################


@route(trigger="callback_query", query_action=QUERY_ACTIONS.MENU_REMINDERS.value, action="edit")
def construct_reminder_page(update):
    user = get_user(update)
    parameters = get_user_parameters(user)
    lang = parameters.language
    vocabularies = _get_vocabulary_list(user)

    heading = html_wrapper(
        escape_html(
            "<><><><><><><><>\n" +
            f"      Reminders \n" +
            "<><><><><><><><>"
        ),
        'b')
    text = ""

    for vocabulary_id in vocabularies:
        reminders = _get_reminder_list(user, vocabulary_id)
        vocabulary_name = vocabularies[vocabulary_id]

        if len(reminders) > 0:
            reminders_text = _reminder_list_to_text(reminders)
            text += ("\n================\n"
                     f"{html_wrapper(escape_html(vocabulary_name), 'b')}\n"
                     "-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-\n"
                     f"{reminders_text}"
                     )
        else:
            continue

    if text == "":
        text = "\n\nYou don't have any\n reminders"

    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="      ━      ", callback_data=json.dumps([QUERY_ACTIONS.DELETE_REMINDER.value])),
                InlineKeyboardButton(text="      ✚      ", callback_data=json.dumps([QUERY_ACTIONS.ADD_REMINDER.value]))
            ],
            [
                InlineKeyboardButton(text="      ↩️      ", callback_data=json.dumps([QUERY_ACTIONS.MENU.value])),
                InlineKeyboardButton(text="      ℹ️      ",
                                     callback_data=json.dumps([QUERY_ACTIONS.SHOW_INFO.value, "info_reminders"]))
            ],
        ]
    )
    return heading + text, reply_markup
