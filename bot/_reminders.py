import json
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from .temp_manager import *
from ._enums import TaskStatus, QUERY_ACTIONS, TEMP_KEYS
from .utils import html_wrapper, escape_html, suggest_reminder_time, shift_time
from router import route
from translations import translate, conjugate_word
from ._vocabularies import _get_vocabulary_list, _get_vocabulary_name, _get_inline_vocabulary_list
from bot._input_picker import pick_time, generate_number_keyboard
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


def _adjust_reminders_to_new_timezone(user, old_timezone, new_timezone):
    """
    Adjusts reminders for a user to a new timezone by updating UTC times in the database. Local time stays the same.

    :param user: The user ID to adjust reminders for.
    :param old_timezone: The user's old timezone offset in hours (e.g., +2 for UTC+2).
    :param new_timezone: The user's new timezone offset in hours (e.g., +3 for UTC+3).
    """
    offset_difference = old_timezone - new_timezone
    vocabularies = _get_vocabulary_list(user)

    for vocabulary_id in vocabularies:
        reminders = _get_reminder_list(user, vocabulary_id)

        for time, number_of_words in reminders.items():
            new_time = shift_time(time, hour_offset=offset_difference)

            db.Reminders.set(
                conditions={
                    "user_id": user,
                    "vocabulary_id": vocabulary_id,
                    "time": time,
                },
                new_values={
                    "time": new_time,
                }
            )


def _get_reminders_list_at(time: str) -> list[tuple[int, int, int, str, int]]:
    """
    Fetches a list of reminders scheduled for the specified time.

    :param time: The time for which to retrieve reminders. It should match the format used in the database.
    :return: A list of reminders, where each reminder is represented as a named tuple containing column names as keys
    and their corresponding values.
    """
    return db.Reminders.get({"time": time}, force_2d=True, include_column_names=True)


####################################################################################################################
#                                                     OTHER
####################################################################################################################


def _reminder_list_to_text(reminders: dict, lang: str, hour_offset=0) -> str:
    """
    Converts a dictionary of reminders into a formatted text representation,
    ensuring they are displayed in chronological order after applying a time shift.

    :param reminders: A dictionary where keys are times and values are the number of words.
    :param lang: The language code of the user.
    :param hour_offset: Timezone offset in hours.
    :return: A formatted string representing the reminders.
    """
    shifted_reminders = []

    # Adjust time and store the original data
    for time, words_number in reminders.items():
        adjusted_time = shift_time(time, hour_offset=hour_offset)
        shifted_reminders.append((adjusted_time, words_number))

    # Sort by the adjusted time
    shifted_reminders.sort(key=lambda x: x[0])

    text = ""
    for adjusted_time, words_number in shifted_reminders:
        text += f"{adjusted_time}  —  {words_number} {conjugate_word(lang, words_number)}\n"

    return text


def _generate_vocabulary_reminders_text(user, vocabulary_id, vocabulary_name, timezone, lang,
                                        include_no_reminders_text=False):
    """
    Generates reminder text for a specific vocabulary.

    :param user: The user object.
    :param vocabulary_id: The ID of the vocabulary to generate reminders for.
    :param vocabulary_name: The name of the vocabulary.
    :param timezone: The user's timezone.
    :param lang: The language code of the user.
    :param include_no_reminders_text: Whether to include text indicating no reminders. Default is False.
    :return: A string containing the formatted reminders text or an empty string if no reminders are found.
    """
    reminders = _get_reminder_list(user, vocabulary_id)
    heading = ("\n================\n"
               f"{html_wrapper(escape_html(vocabulary_name), 'b')}\n"
               "-.-.-.-.-.-.-.-.-.-.-.-.-.-.-.-\n")

    if len(reminders) > 0:
        reminders_text = _reminder_list_to_text(reminders, lang, timezone)
        return heading + reminders_text
    elif include_no_reminders_text:
        return heading + translate(lang, "no_reminders") + "\n"
    else:
        return ""


def _get_inline_reminder_list(user, vocabulary_id, timezone, lang, next_query_action, back_button_action):
    """
    Creates an inline keyboard with a list of reminders for a given vocabulary, including a back button.

    :param user: The user ID to fetch reminders for.
    :param vocabulary_id: The vocabulary ID to fetch reminders for.
    :param timezone: Timezone offset of user.
    :param lang: The language code of the user.
    :param next_query_action: The action identifier to execute when the user clicks on a reminder.
    :param back_button_action: The callback action for the back button.
    :return: An InlineKeyboardMarkup object with the reminder list and a back button.
    """
    reminders = _get_reminder_list(user, vocabulary_id)

    buttons = []

    for time, words_number in reminders.items():
        button_text = f"{shift_time(time, timezone)}  —  {words_number} {conjugate_word(lang, words_number)}"
        buttons.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=json.dumps([next_query_action, vocabulary_id, time])
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text='      ↩️      ',
            callback_data=json.dumps([back_button_action])
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


####################################################################################################################
#                                                  BOT ACTIONS
####################################################################################################################


def _add_reminder_menu_text(update, vocabulary_id=None, time=None, number_of_words=0):
    user = get_user(update)
    parameters = get_user_parameters(user)
    timezone = parameters.timezone
    lang = parameters.language

    vocabulary_name = _get_vocabulary_name(vocabulary_id) if vocabulary_id else '—'
    display_time = shift_time(time, timezone) if time else "--:--"

    text = (f"{translate(lang, 'adding_reminder')}:\n\n"
            f"{translate(lang, 'vocabulary_name')}: {vocabulary_name}\n"
            f"{translate(lang, 'time')}: {display_time}\n"
            f"{translate(lang, 'number_of_words')}: {number_of_words}")
    return text


@route(trigger="callback_query", query_action=QUERY_ACTIONS.ADD_REMINDER.value, action="edit")
def add_reminder_start(update):
    user = get_user(update)
    text, _ = construct_reminder_page(update)
    text += "\n" + _add_reminder_menu_text(update)
    reply_markup = _get_inline_vocabulary_list(user,
                                               next_query_action=QUERY_ACTIONS.ADD_REMINDER_VOCABULARY_CHOSEN.value,
                                               back_button_action=QUERY_ACTIONS.MENU_REMINDERS.value)
    return text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.ADD_REMINDER_VOCABULARY_CHOSEN.value, action="edit")
def add_reminder_vocabulary_chosen(update):
    user = get_user(update)
    parameters = get_user_parameters(user)
    lang = parameters.language
    timezone = parameters.timezone
    callback_data = json.loads(update["callback_query"]["data"])
    vocabulary_id = callback_data[1]
    vocabulary_name = _get_vocabulary_name(vocabulary_id)
    set_temp(user, TEMP_KEYS.VOCABULARY.value, vocabulary_id)

    text = _generate_vocabulary_reminders_text(user, vocabulary_id, vocabulary_name, timezone, lang,
                                               include_no_reminders_text=True)
    text += '\n' + _add_reminder_menu_text(update, vocabulary_id)
    time = suggest_reminder_time()
    reply_markup = pick_time(update, time, include_minutes=True,
                             next_query_action=QUERY_ACTIONS.ADD_REMINDER_TIME_CHOSEN.value,
                             back_button_action=QUERY_ACTIONS.MENU_REMINDERS.value,
                             real_time_mins=False,
                             adjust_to_timezone=True)
    return text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.ADD_REMINDER_TIME_CHOSEN.value, action="edit")
def add_reminder_time_chosen(update):
    user = get_user(update)
    callback_data = json.loads(update["callback_query"]["data"])
    time = callback_data[1]
    set_temp(user, TEMP_KEYS.TIME.value, time)

    vocabulary_id = get_temp(user, TEMP_KEYS.VOCABULARY.value)

    text = _add_reminder_menu_text(update, vocabulary_id, time)
    reply_markup = generate_number_keyboard(QUERY_ACTIONS.ADD_REMINDER_FINALIZE.value,
                                            QUERY_ACTIONS.MENU_REMINDERS.value)
    return text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.ADD_REMINDER_FINALIZE.value, action="edit")
def add_reminder_finalize(update):
    user = get_user(update)
    parameters = get_user_parameters(user)
    lang = parameters.language
    timezone = parameters.timezone

    time = pop_temp(user, TEMP_KEYS.TIME.value)
    vocabulary_id = pop_temp(user, TEMP_KEYS.VOCABULARY.value)
    vocabulary_name = _get_vocabulary_name(vocabulary_id)

    callback_data = json.loads(update["callback_query"]["data"])
    number_of_words = callback_data[1]

    reminder_id = _add_reminder(user, vocabulary_id, time, number_of_words)
    if reminder_id == 0:
        text = translate(lang, "reminder_duplicate", {"vocabulary_name": escape_html(vocabulary_name),
                                                      "time": shift_time(time, timezone)})
    else:
        text = translate(lang, "reminder_set", {"time": shift_time(time, timezone),
                                                "number_of_words": number_of_words,
                                                "conjugated_word": conjugate_word(lang, number_of_words),
                                                "vocabulary_name": escape_html(vocabulary_name)})

    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="      ↩️      ",
                                     callback_data=json.dumps([QUERY_ACTIONS.MENU_REMINDERS.value])),
            ]
        ]
    )

    return text, reply_markup


def _delete_reminder_menu_text(update, vocabulary_id=None, time=None):
    user = get_user(update)
    parameters = get_user_parameters(user)
    timezone = parameters.timezone
    lang = parameters.language

    vocabulary_name = _get_vocabulary_name(vocabulary_id) if vocabulary_id else '—'
    display_time = shift_time(time, timezone) if time else "--:--"

    text = (f"{translate(lang, 'deleting_reminder')}:\n\n"
            f"{translate(lang, 'vocabulary_name')}: {vocabulary_name}\n"
            f"{translate(lang, 'time')}: {display_time}\n")
    return text


@route(trigger="callback_query", query_action=QUERY_ACTIONS.DELETE_REMINDER.value, action="edit")
def delete_reminder_start(update):
    user = get_user(update)
    text, _ = construct_reminder_page(update)
    text += "\n" + _delete_reminder_menu_text(update)
    reply_markup = _get_inline_vocabulary_list(user,
                                               next_query_action=QUERY_ACTIONS.DELETE_REMINDER_VOCABULARY_CHOSEN.value,
                                               back_button_action=QUERY_ACTIONS.MENU_REMINDERS.value)
    return text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.DELETE_REMINDER_VOCABULARY_CHOSEN.value, action="edit")
def delete_reminder_vocabulary_chosen(update):
    user = get_user(update)
    parameters = get_user_parameters(user)
    lang = parameters.language
    timezone = parameters.timezone
    callback_data = json.loads(update["callback_query"]["data"])
    vocabulary_id = callback_data[1]
    vocabulary_name = _get_vocabulary_name(vocabulary_id)

    text = _generate_vocabulary_reminders_text(user, vocabulary_id, vocabulary_name, timezone, lang,
                                               include_no_reminders_text=True)
    text += '\n' + _delete_reminder_menu_text(update, vocabulary_id)
    reply_markup = _get_inline_reminder_list(user, vocabulary_id, timezone, lang,
                                             next_query_action=QUERY_ACTIONS.DELETE_REMINDER_FINALIZE.value,
                                             back_button_action=QUERY_ACTIONS.MENU_REMINDERS.value)
    return text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.DELETE_REMINDER_FINALIZE.value, action="edit")
def delete_reminder_finalize(update):
    user = get_user(update)
    parameters = get_user_parameters(user)
    lang = parameters.language
    timezone = parameters.timezone
    callback_data = json.loads(update["callback_query"]["data"])
    vocabulary_id, time = callback_data[1:]
    vocabulary_name = _get_vocabulary_name(vocabulary_id)
    match _delete_reminder(user, vocabulary_id=vocabulary_id, time=time):
        case TaskStatus.SUCCESS:
            text = translate(lang, "reminder_deleted", {"time": shift_time(time, timezone),
                                                        "vocabulary_name": escape_html(vocabulary_name)})
            reply_markup = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(text="      ↩️      ",
                                             callback_data=json.dumps([QUERY_ACTIONS.MENU_REMINDERS.value])),
                    ]
                ]
            )
        case TaskStatus.FAILURE:
            raise FileNotFoundError(
                f'Failed to delete a reminder at time from vocabulary #{vocabulary_id}')

        case _:
            raise ValueError("Unsupported status")
    return text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.MENU_REMINDERS.value, action="edit")
def construct_reminder_page(update):
    user = get_user(update)
    parameters = get_user_parameters(user)
    timezone = parameters.timezone
    lang = parameters.language
    vocabularies = _get_vocabulary_list(user)

    heading = html_wrapper(
        escape_html(
            "<><><><><><><><>\n" +
            translate(lang, "reminders_heading") + "\n" +
            "<><><><><><><><>"
        ),
        'b')
    text = ""

    for vocabulary_id in vocabularies:
        vocabulary_name = vocabularies[vocabulary_id]
        text += _generate_vocabulary_reminders_text(user, vocabulary_id, vocabulary_name, timezone, lang)

    if text == "":
        text = "\n\n" + translate(lang, "no_reminders")

    reply_markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="      ━      ",
                                     callback_data=json.dumps([QUERY_ACTIONS.DELETE_REMINDER.value])),
                InlineKeyboardButton(text="      ✚      ", callback_data=json.dumps([QUERY_ACTIONS.ADD_REMINDER.value]))
            ],
            [
                InlineKeyboardButton(text="      ↩️      ", callback_data=json.dumps([QUERY_ACTIONS.MENU.value])),
                InlineKeyboardButton(text="      ℹ️      ",
                                     callback_data=json.dumps([QUERY_ACTIONS.SHOW_INFO.value, "info_reminders",
                                                               QUERY_ACTIONS.MENU_REMINDERS.value]))
            ],
        ]
    )
    return heading + text, reply_markup
