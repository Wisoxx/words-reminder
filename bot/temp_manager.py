import database as db
from . import TEMP_KEYS
from ._enums import TaskStatus, QUERY_ACTIONS, TEMP_KEYS, USER_STATES
from logger import setup_logger


logger = setup_logger(__name__)


user_parameters = {}


def set_temp(user, key, value):
    if db.Temp.add({"user_id": user, "key": key, "value": value}):
        logger.debug(f"Temp set for user {user} key={key} value={value}")
        return TaskStatus.SUCCESS
    return TaskStatus.FAILURE


def get_temp(user, key):
    entry = db.Temp.get({"user_id": user, "key": key}, include_column_names=True)
    if entry:
        return entry.value
    return None


def remove_temp(user, key):
    if db.Temp.delete({"user_id": user, "key": key}):
        logger.debug(f"Temp removed for user {user} key={key}")
        return TaskStatus.SUCCESS
    return TaskStatus.FAILURE


def pop_temp(user, key):
    value = get_temp(user, key)
    remove_temp(user, key)
    return value


def get_user(update):
    if "message" in update:
        user = update["message"]["chat"]["id"]
    elif "callback_query" in update:
        user = update["callback_query"]["from"]["id"]
    elif "my_chat_member" in update:
        user = update["my_chat_member"]["from"]["id"]
    else:
        raise KeyError("Couldn't find user")

    return user


def check_missing_setup(user):
    parameters = get_user_parameters(user)
    if not parameters:
        return "user"

    lang = parameters.language
    if not lang:
        return "lang"

    vocabulary_id = parameters.current_vocabulary_id
    if not vocabulary_id:
        return "vocabulary"

    timezone_not_set = get_temp(user, TEMP_KEYS.TIMEZONE_NOT_SET.value)
    if timezone_not_set:
        return "timezone"

    return None


def get_user_parameters(user):
    if user in user_parameters:
        return user_parameters[user]

    parameters = db.Users.get({"user_id": user}, include_column_names=True)
    if len(parameters) > 0:
        user_parameters[user] = parameters
    return parameters


def invalidate_cached_parameters(user):
    if user in user_parameters:
        del user_parameters[user]


def get_user_state(user):
    state = get_temp(user, TEMP_KEYS.STATE.value)
    logger.debug(f"User state: {state}")
    return int(state) if state is not None else None


def set_user_state(user, state):
    status = set_temp(user, TEMP_KEYS.STATE.value, state)
    if status:
        logger.debug(f"User state was set to: {state}")
    return status


def reset_user_state(user):
    status = remove_temp(user, TEMP_KEYS.STATE.value)
    if status:
        logger.debug(f"User state was reset")
    return status
