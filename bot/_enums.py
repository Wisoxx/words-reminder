from enum import Enum, auto


class QUERY_ACTIONS(Enum):
    CANCEL = auto()
    SET_LANGUAGE = auto()
    CHANGE_WORDS_PAGE = auto()
    ADD_SPECIFIC_WORD = auto()
    DELETE_SPECIFIC_WORD = auto()
    ADD_SPECIFIC_REMINDER = auto()
    DELETE_SPECIFIC_REMINDER = auto()
    MENU = auto()
    MENU_WORDS = auto()
    MENU_REMINDERS = auto()
    MENU_VOCABULARIES = auto()
    MENU_SETTINGS = auto()
    SHOW_INFO = auto()
    CHANGE_VOCABULARY = auto()
    VOCABULARY_CHOSEN = auto()
    ADD_WORD = auto()
    DELETE_WORD = auto()
    WORDS_CHANGE_VOCABULARY = auto()
    WORDS_VOCABULARY_CHOSEN = auto()
    ADD_REMINDER = auto()
    ADD_REMINDER_VOCABULARY_CHOSEN = auto()
    ADD_REMINDER_TIME_CHOSEN = auto()
    ADD_REMINDER_NUMBER_OF_WORDS = auto()
    ADD_REMINDER_FINALIZE = auto()
    DELETE_REMINDER = auto()
    DELETE_REMINDER_VOCABULARY_CHOSEN = auto()
    DELETE_REMINDER_FINALIZE = auto()
    CREATE_VOCABULARY = auto()
    DELETE_VOCABULARY = auto()
    DELETE_VOCABULARY_CONFIRM = auto()
    DELETE_VOCABULARY_DECLINE = auto()
    CHANGE_LANGUAGE = auto()
    LANGUAGE_CHOSEN = auto()
    TOGGLE_HIDE_MEANING = auto()
    CHANGE_TIMEZONE = auto()
    PICK_TIME = auto()
    TIME_CHOSEN = auto()


class TEMP_KEYS(Enum):
    STATE = auto()
    VOCABULARY = auto()
    TIME = auto()
    CANCEL_BUTTON_ID = auto()
    CALL_MENU = auto()


class USER_STATES(Enum):
    NO_STATE = None
    DELETE_WORD = auto()
    CREATE_VOCABULARY = auto()
    CHANGE_VOCABULARY = auto()
    DELETE_VOCABULARY_INPUT = auto()
    DELETE_VOCABULARY_CONFIRMATION = auto()
    ADD_REMINDER_VOCABULARY = auto()
    ADD_REMINDER_TIME = auto()
    ADD_REMINDER_WORDSNUMBER = auto()
    DELETE_REMINDER_VOCABULARY = auto()
    DELETE_REMINDER_TIME = auto()
    WORDLIST_VOCABULARY = auto()


class TaskStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    NO_VOCABULARY = auto()
    DUPLICATE = auto()
