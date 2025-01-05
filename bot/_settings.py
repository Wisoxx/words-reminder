import database as db
from ._enums import TaskStatus, QUERY_ACTIONS, TEMP_KEYS, USER_STATES
from .temp_manager import set_temp, get_temp, remove_temp, pop_temp
from logger import setup_logger


logger = setup_logger(__name__)


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


def get_user_parameters(user):
    return db.Users.get({"user_id": user}, include_column_names=True)


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
