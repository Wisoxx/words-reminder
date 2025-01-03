import database as db
from ._enums import TaskStatus, QUERY_ACTIONS, TEMP_KEYS, USER_STATES
from logger import setup_logger


logger = setup_logger(__name__)


def get_user_parameters(user):
    return db.Users.get({"user_id": user}, include_column_names=True)


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


def get_user_state(user):
    state = get_temp(user, TEMP_KEYS.STATE.value)
    logger.debug(f"User state: {state}")
    return int(state)


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
