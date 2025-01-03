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
    ADD_WORD = auto()
    DELETE_WORD = auto()
    ADD_REMINDER = auto()
    DELETE_REMINDER = auto()
    ADD_VOCABULARY = auto()
    DELETE_VOCABULARY = auto()
    CHANGE_LANGUAGE = auto()
    TOGGLE_HIDE_MEANING = auto()


class TEMP_KEYS(Enum):
    STATE = auto()
    VOCABULARY = auto()
    TIME = auto()
    CANCEL_BUTTON_ID = auto()
    CALL_MENU = auto()


class USER_STATES(Enum):
    NO_STATE = None
    DELETEWORD_WORD = auto()
    ADDVOCABULARY_VOCABULARY = auto()
    CHANGEVOCABULARY_VOCABULARY = auto()
    DELETEVOCABULARY_VOCABULARY = auto()
    DELETEVOCABULARY_CONFIRMATION = auto()
    ADDREMINDER_VOCABULARY = auto()
    ADDREMINDER_TIME = auto()
    ADDREMINDER_WORDSNUMBER = auto()
    DELETEREMINDER_VOCABULARY = auto()
    DELETEREMINDER_TIME = auto()
    WORDLIST_VOCABULARY = auto()


class TaskStatus(Enum):
    SUCCESS = auto()
    FAILURE = auto()
    NO_VOCABULARY = auto()
    DUPLICATE = auto()