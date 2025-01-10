import database as db
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
from .temp_manager import get_user, get_user_parameters
from ._enums import QUERY_ACTIONS
from .utils import html_wrapper, escape_html, get_hh_mm, calculate_timezone_offset
from ._input_picker import pick_time
from translations import translate, languages
from router import route
from logger import setup_logger


logger = setup_logger(__name__)


####################################################################################################################
#                                                DATABASE INTERACTIONS
####################################################################################################################


def _toggle_hide_meaning(user):
    status = db.Users.execute_query("""
    UPDATE users
    SET hide_meaning = NOT hide_meaning
    WHERE user_id = ?;
    """, (user, )).rowcount > 0
    if status:
        logger.info(f"User {user} toggled hide_meaning")
    return status


def _set_language(user, language: str):
    status = db.Users.set({"user_id": user}, {"language": language})
    if status:
        logger.info(f"User {user} changed language to {language}")
    return status


def _set_timezone(user, timezone: int):
    status = db.Users.set({"user_id": user}, {"timezone": timezone})
    if status:
        logger.info(f"User {user} changed timezone to {timezone}")
    return status


####################################################################################################################
#                                                     OTHER
####################################################################################################################


####################################################################################################################
#                                                  BOT ACTIONS
####################################################################################################################


@route(trigger="callback_query", query_action=QUERY_ACTIONS.MENU_SETTINGS.value, action="edit")
def settings(update):
    user = get_user(update)
    parameters = get_user_parameters(user)
    lang = parameters.language
    hide_meaning = parameters.hide_meaning
    timezone = parameters.timezone
    heading = html_wrapper(
        escape_html(
            "<><><><><><><><><><><><><><><><><><><>\n" +
            f"{' ' * 30}Settings\n" +
            "<><><><><><><><><><><><><><><><><><><>"
        ),
        'b')
    text = (f"🌎 Language: {translate(lang, 'flag')}\n"
            f"👁 Hide meaning: {'✅' if hide_meaning else '❌'}\n"
            f"🕓 Timezone: UTC{'+' if timezone >= 0 else ''}{timezone} ({get_hh_mm(timezone)})")

    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=f'      🌎      ',
                                 callback_data=json.dumps([QUERY_ACTIONS.CHANGE_LANGUAGE.value])),
            InlineKeyboardButton(text=f'      👁      ',
                                 callback_data=json.dumps([QUERY_ACTIONS.TOGGLE_HIDE_MEANING.value])),
            InlineKeyboardButton(text=f'      🕓      ',
                                 callback_data=json.dumps([QUERY_ACTIONS.CHANGE_TIMEZONE.value])),
        ],
        [
            InlineKeyboardButton(text='      ↩️      ', callback_data=json.dumps([QUERY_ACTIONS.MENU.value])),
            InlineKeyboardButton(text='      ℹ️      ',
                                 callback_data=json.dumps([QUERY_ACTIONS.SHOW_INFO.value, "info_settings"])),
        ]
    ])
    return heading + '\n' + text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.TOGGLE_HIDE_MEANING.value, action="edit")
def toggle_hide_meaning(update):
    user = get_user(update)
    _toggle_hide_meaning(user)
    return settings(update)


@route(trigger="callback_query", query_action=QUERY_ACTIONS.CHANGE_LANGUAGE.value, action="edit")
def change_language_start(update):
    text = "\n".join(translate(lang, "choose_lang") for lang in languages)
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f'      {translate(lang, "flag")}      ',
                callback_data=json.dumps([QUERY_ACTIONS.LANGUAGE_CHOSEN.value, lang])
            )
            for lang in languages
        ]
    ])
    return text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.LANGUAGE_CHOSEN.value, action="edit")
def change_language_finalize(update):
    user = get_user(update)
    callback_data = json.loads(update["callback_query"]["data"])
    lang = callback_data[1]

    if lang not in languages:
        raise ValueError("Unsupported language")

    _set_language(user, lang)
    return settings(update)


@route(trigger="callback_query", query_action=QUERY_ACTIONS.CHANGE_TIMEZONE.value, action="edit")
def change_timezone_start(update):
    user = get_user(update)
    parameters = get_user_parameters(user)
    timezone = parameters.timezone
    time = get_hh_mm()

    text = "Match the time below with your current time. Once you do it, press on the time to save your timezone."
    reply_markup = pick_time(update, time, include_minutes=False,
                             next_query_action=QUERY_ACTIONS.CHANGE_TIMEZONE_FINALIZE.value,
                             back_button_action=QUERY_ACTIONS.MENU_SETTINGS.value,
                             real_time_mins=True, adjust_to_timezone=False)
    return text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.CHANGE_TIMEZONE_FINALIZE.value, action="edit")
def change_timezone_finalize(update):
    user = get_user(update)
    parameters = get_user_parameters(user)
    old_timezone = parameters.timezone
    callback_data = json.loads(update["callback_query"]["data"])
    time = callback_data[1]
    logger.info(f"User chose time: {time}")
    new_timezone = calculate_timezone_offset(time)
    _set_timezone(user, new_timezone)
    return settings(update)