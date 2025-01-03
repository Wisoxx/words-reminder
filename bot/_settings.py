import database as db
from ._enums import TaskStatus, QUERY_ACTIONS, TEMP_KEYS, USER_STATES


def get_user_parameters(user):
    return db.Users.get({"user_id": user}, include_column_names=True)


def set_temp(user, key, value):
    if db.Temp.add({"user_id": user, "key": key, "value": value}):
        return TaskStatus.SUCCESS
    return TaskStatus.FAILURE


def get_temp(user, key):
    entry = db.Temp.get({"user_id": user, "key": key}, include_column_names=True)
    if entry:
        return entry.value
    return None


def remove_temp(user, key):
    if db.Temp.delete({"user_id": user, "key": key}):
        return TaskStatus.SUCCESS
    return TaskStatus.FAILURE


def pop_temp(user, key):
    value = get_temp(user, key)
    remove_temp(user, key)
    return value


def get_user_state(user):
    return get_temp(user, TEMP_KEYS.STATE.value)


def set_user_state(user, state):
    return set_temp(user, TEMP_KEYS.STATE.value, state)


def reset_user_state(user):
    return remove_temp(user, TEMP_KEYS.STATE.value)
