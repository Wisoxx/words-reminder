import database as db
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json
from .temp_manager import get_user, get_user_parameters, invalidate_cached_parameters, remove_temp
from ._enums import QUERY_ACTIONS, TEMP_KEYS
from .utils import html_wrapper, escape_html, get_hh_mm, calculate_timezone_offset
from ._input_picker import pick_time
from ._reminders import _adjust_reminders_to_new_timezone
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
        invalidate_cached_parameters(user)
        logger.info(f"User {user} toggled hide_meaning")
    return status


def _set_language(user, language: str):
    status = db.Users.set({"user_id": user}, {"language": language})
    if status:
        invalidate_cached_parameters(user)
        logger.info(f"User {user} changed language to {language}")
    return status


def _set_timezone(user, timezone: int):
    status = db.Users.set({"user_id": user}, {"timezone": timezone})
    if status:
        invalidate_cached_parameters(user)
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
            f"{translate(lang, 'settings_heading')}\n" +
            "<><><><><><><><><><><><><><><><><><><>"
        ),
        'b')
    text = (f"🌎 {translate(lang, 'language')}: {translate(lang, 'flag')}\n"
            f"👁 {translate(lang, 'hide_meaning')}: {'✅' if hide_meaning else '❌'}\n"
            f"🕓 {translate(lang, 'timezone')}: UTC{'+' if timezone >= 0 else ''}{timezone} ({get_hh_mm(timezone)})")

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
def change_language_start(update, return_to_menu=True):
    text = "\n".join(translate(lang, "choose_lang") for lang in languages)
    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=f'      {translate(lang, "flag")}      ',
                callback_data=json.dumps([QUERY_ACTIONS.LANGUAGE_CHOSEN.value, lang, return_to_menu])
            )
            for lang in languages
        ]
    ])
    return text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.LANGUAGE_CHOSEN.value, action="edit")
def change_language_finalize(update):
    user = get_user(update)
    callback_data = json.loads(update["callback_query"]["data"])
    lang, return_to_menu = callback_data[1:]

    if lang not in languages:
        raise ValueError("Unsupported language")

    _set_language(user, lang)

    if return_to_menu:
        return settings(update)

    text = translate(lang, "lang_set")
    reply_markup = None
    return text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.CHANGE_TIMEZONE.value, action="edit")
def change_timezone_start(update, next_query_action=QUERY_ACTIONS.CHANGE_TIMEZONE_FINALIZE.value,
                          back_button_action=QUERY_ACTIONS.MENU_SETTINGS.value):
    user = get_user(update)
    parameters = get_user_parameters(user)
    lang = parameters.language
    timezone = parameters.timezone
    time = get_hh_mm(timezone)

    text = translate(lang, "setup_timezone")
    reply_markup = pick_time(update, time, include_minutes=False,
                             next_query_action=next_query_action,
                             back_button_action=back_button_action,
                             real_time_mins=True,
                             adjust_to_timezone=False)
    return text, reply_markup


@route(trigger="callback_query", query_action=QUERY_ACTIONS.CHANGE_TIMEZONE_FINALIZE.value, action="edit")
def change_timezone_finalize(update):
    user = get_user(update)
    parameters = get_user_parameters(user)
    old_timezone = parameters.timezone
    callback_data = json.loads(update["callback_query"]["data"])
    time = callback_data[1]
    logger.info(f"User {user} chose their local time as: {time}")
    new_timezone = calculate_timezone_offset(time)
    _set_timezone(user, new_timezone)
    _adjust_reminders_to_new_timezone(user, old_timezone, new_timezone)
    return settings(update)


@route(trigger="callback_query", query_action=QUERY_ACTIONS.SET_UP_TIMEZONE_FINALIZE.value, action="edit")
def set_up_timezone_finalize(update):
    user = get_user(update)
    parameters = get_user_parameters(user)
    old_timezone = parameters.timezone
    lang = parameters.language

    callback_data = json.loads(update["callback_query"]["data"])
    time = callback_data[1]
    logger.info(f"User {user} set up their local time as: {time}")
    new_timezone = calculate_timezone_offset(time)
    _set_timezone(user, new_timezone)
    _adjust_reminders_to_new_timezone(user, old_timezone, new_timezone)
    remove_temp(user, TEMP_KEYS.TIMEZONE_NOT_SET.value)

    text = translate(lang, "timezone_set", {"timezone": new_timezone, "time": get_hh_mm(new_timezone)})
    reply_markup = None
    return text, reply_markup
