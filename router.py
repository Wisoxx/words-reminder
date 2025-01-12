from collections import namedtuple
from logger import setup_logger


logger = setup_logger(__name__)


TRIGGERS = ("text", "callback_query", "chat_member", "other")
ACTIONS = ("send", "edit", "edit_markup", "popup", None)
routes = {}


def route(trigger, action, state=None, query_action=None, command=None, cancel_button=False):
    def decorator(func):
        if trigger in TRIGGERS and action in ACTIONS:  # assuming only correct states are passed
            FuncInfo = namedtuple('FuncInfo', ['call', 'required_action', 'cancel_button'])
            key = trigger, state, query_action, command
            routes[key] = FuncInfo(func, action, cancel_button)
            logger.debug(f"Added route {func.__name__} by key: {key}")
            return func
        else:
            raise ValueError("Invalid arguments")
    return decorator


def get_route(trigger, state=None, query_action=None, command=None):
    """
    Get function route for given conditions
    :param trigger: Trigger to activate function. "text" or "callback_query"
    :param state: User state during which function will be called
    :param query_action: Callback query data that carries action number
    :param command: Text command like /test
    :return: named tuple with callable function, required action and whether to add cancel button.
    FuncInfo(func, action, cancel_button)
    """
    key = trigger, state, query_action, command
    return routes[key]
