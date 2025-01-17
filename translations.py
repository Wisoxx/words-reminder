languages = ("en", "ua", "pl")


def translate(lang: str, key: str, values: dict = None):
    translations = {
        'en': {
            'flag': '🇬🇧',
            'choose_lang': '🇬🇧 Choose your language',
            'lang_set': 'Language preferences have been updated',
            'choose_category': 'Choose category:',
            'words': 'Words',
            'reminders': 'Reminders',
            'reminders_heading': '      Reminders',
            'vocabulary': 'Vocabulary',
            'settings': 'Settings',
            'cancel': 'Cancel',
            'cancelled': 'Successfully cancelled',
            'add_back': 'Add back',
            'delete': 'Delete',
            'error': "Something went wrong",
            'short_hours': 'h',
            'short_minutes': 'min',
            'finish_setup': 'Firstly you have to finish the setup!',
            'setup_finished': 'You\'ve finished the setup! To get more information type /help. To access menu type /menu',
            'help': 'help',
            'unrecognized_message': 'Sorry, I didn\'t understand that kind of message. Try something else',
            'unrecognized_command': 'Sorry, I didn\'t understand that command. Try /help or /menu',
            'adding_reminder': 'Adding a reminder',
            'deleting_reminder': 'Deleting a reminder',
            'vocabulary_name': 'Vocabulary name',
            'time': 'Time',
            'number_of_words': 'Number of words',
            'reminder_duplicate': 'You already have a reminder from "{vocabulary_name}" at {time}',
            'reminder_set': 'See you at {time} with {number_of_words} {conjugated_word} from "{vocabulary_name}" :)',
            'reminder_deleted': 'Successfully deleted reminder at {time} from "{vocabulary_name}"',
            'no_reminders': 'You don\'t have any\n reminders',


            'info_words': 'info_words',
            'info_recall': 'info_recall',
            'info_reminders': 'info_reminders',
            'info_vocabularies': 'info_vocabularies',
            'info_settings': 'info_settings',
        },
        'ua': {
            'flag': '🇺🇦',
            'choose_lang': '🇺🇦 Вибери свою мову',
            'lang_set': 'Налаштування мови оновлено',
            'choose_category': 'Вибери категорію:',
            'short_hours': 'год',
            'short_minutes': 'хв',
        },
        'pl': {
            'flag': '🇵🇱',
            'choose_lang': '🇵🇱 Wybierz swój język',
            'lang_set': 'Ustawienia językowe zostały zmienione',
            'choose_category': 'Wybierz kategorię:',
            'short_hours': 'h',
            'short_minutes': 'min',

        }
    }
    lang = "uk" if lang == "ru" else lang  # change russian to ukrainian
    lang = lang if lang in languages else "en"  # default lang is english
    translation = translations[lang][key]
    if values:
        return translation.format(**values)
    return translation


def conjugate_word(lang, number):
    last_digit = number % 10
    last_two_digits = number % 100

    match lang:
        case 'en':
            return 'word' if number == 1 else 'words'

        case 'ua':
            if last_digit == 1 and last_two_digits != 11:
                return 'слово'
            elif last_digit in [2, 3, 4] and last_two_digits not in [12, 13, 14]:
                return 'слова'
            else:
                return 'слів'

        case 'pl':
            if number == 1:
                return 'słowo'
            elif last_digit in [2, 3, 4] and last_two_digits not in [12, 13, 14]:
                return 'słowa'
            else:
                return 'słów'

        case _:
            raise ValueError('Invalid language')
