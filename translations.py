languages = ("en", "ua", "pl")


def translate(lang: str, key: str, values: dict = None):
    translations = {
        'en': {
            # Misc
            'flag': '🇬🇧',
            'choose_category': 'Choose category:',
            'cancel': 'Cancel',
            'cancelled': 'Successfully cancelled',
            'add_back': 'Add back',
            'delete': 'Delete',
            'error': "Something went wrong",
            'short_hours': 'h',
            'short_minutes': 'min',
            'finish_setup': 'Firstly you have to finish the setup!',
            'setup_finished': 'You\'ve finished the setup! To get more information type /help. To access menu type '
                              '/menu. If you are having troubles navigating a menu, press ℹ️ at the bottom of each menu'
                              ' to get a quick tour',
            'help': 'I\'m Word Recall, your personal word keeper! Send me the words you want to learn. You can '
                    'optionally include meaning too! You just have to send it in the from "word - meaning". Without '
                    'the " - " the whole text will be treated as one word. You can save words to different vocabularies'
                    ' (however many you create!). To each vocabulary you can assign any number of reminders at any '
                    'given minute and then I will remind you at the selected time.\n\n'
                    'Type /menu to open menu. If you are having troubles navigating a menu, press ℹ️ at the bottom of'
                    ' each menu to get a quick tour.',
            'unrecognized_message': 'Sorry, I didn\'t understand that kind of message. Try something else',
            'unrecognized_command': 'Sorry, I didn\'t understand that command. Try /help or /menu',
            # Reminders
            'reminders': 'Reminders',
            'reminders_heading': '      Reminders',
            'adding_reminder': 'Adding a reminder',
            'deleting_reminder': 'Deleting a reminder',
            'vocabulary_name': 'Vocabulary name',
            'time': 'Time',
            'number_of_words': 'Number of words',
            'reminder_duplicate': 'You already have a reminder from "{vocabulary_name}" at {time}',
            'reminder_set': 'See you at {time} with {number_of_words} {conjugated_word} from "{vocabulary_name}" :)',
            'reminder_deleted': 'Successfully deleted reminder at {time} from "{vocabulary_name}"',
            'no_reminders': 'You don\'t have any\n reminders',
            'info_reminders': 'Here you can view reminders associated with all of your vocabularies. They are grouped '
                              'by vocabularies and sorted by time. Next to each one you will see how many words they '
                              'will show if your vocabulary is long enough\n\n'
                              'To make some changes press:\n'
                              '━  to delete a reminder\n'
                              '✚  to set a reminder\n\n'
                              'Additionally press:\n'
                              '↩️ to go back to the main menu\n'
                              'ℹ️ to open this informational center',
            # Settings
            'settings': 'Settings',
            'settings_heading': '                              Settings',
            'language': 'Language',
            'hide_meaning': 'Hide meaning',
            'timezone': 'Timezone',
            'choose_lang': '🇬🇧 Choose your language',
            'lang_set': 'Language preferences have been updated',
            'setup_timezone': 'Match the time below with your current time. Once you do it, press on the time to save '
                              'your timezone',
            'timezone_set': 'Timezone set to UTC{timezone:+} ({time})',
            'info_settings': 'Here you can view your current settings\n\n'
                             'To make some changes press:\n'
                             '🌎 to change interface language\n'
                             '👁 to toggle hiding word meanings when showing word list or reminding old words\n'
                             '🕓 to change your timezone. It affects when you will get reminders\n\n'
                             'Additionally press:\n'
                             '↩️ to go back to the main menu\n'
                             'ℹ️ to open this informational center',
            # Vocabularies
            'vocabularies': 'Vocabularies',
            'vocabularies_heading': '                              Vocabularies',
            'change_vocabulary': 'Select vocabulary to work with',
            'name_vocabulary': 'How do you want to name your new vocabulary?',
            'vocabulary_duplicate': 'You already have vocabulary named "{vocabulary_name}". Try something else',
            'vocabulary_created': 'Successfully create vocabulary "{vocabulary_name}"',
            'select_vocabulary_to_delete': 'What vocabulary do you want to delete?',
            'confirm_vocabulary_deletion': 'Are you sure you want to permanently delete "{vocabulary_name}" and '
                                           'everything associated with it including words and reminders?',
            'vocabulary_not_found': 'You don\'t have a vocabulary named "{vocabulary_name}"',
            'vocabulary_deleted': 'Successfully deleted vocabulary "{vocabulary_name}"',
            'no_vocabularies': 'Oh-oh, that was your last vocabulary! To continue using my services, you should create'
                               ' a new one!',
            'vocabulary_deletion_cancelled': 'Successfully cancelled vocabulary deletion',
            'info_vocabularies': 'Here you can view all your vocabularies and their word count. Your current vocabulary'
                                 ' is underlined\n\n'
                                 'To make some changes press:\n'
                                 '━  to delete a vocabulary\n'
                                 '📙 to change current vocabulary\n'
                                 '✚  to create another vocabulary\n\n'
                                 'Additionally press:\n'
                                 '↩️ to go back to the main menu\n'
                                 'ℹ️ to open this informational center',
            # Words
            'words': 'Words',
            'word_duplicate': 'You already have "{word}" in "{vocabulary_name}"',
            'word_added': 'Successfully added "{word}" to "{vocabulary_name}"',
            'choose_word_to_delete': 'Send me the word you want to delete',
            'word_deleted': 'Successfully deleted "{word}" from "{vocabulary_name}"',
            'no_words_to_delete': 'Vocabulary is empty. Nothing to delete',
            'word_not_found': '"{word}" was not found in "{vocabulary_name}"',
            'word_info_expired': 'Information about that word isn\'t available anymore. You can still add it by hand',
            'no_words': '*🦗crickets noises🦗*',
            'recall_no_words': 'Unfortunately, there aren\'t any words to practise in this vocabulary',
            'practice_time': 'It\'s practice time!',
            'oldest_words': 'Here {to_be} {word_count} {conjugated_oldest} {conjugated_word} from "{vocabulary_name}" '
                            'to recall',
            'info_words': 'Here you can view words added to your current vocabulary\n\n'
                          'To move through your vocabulary press:\n'
                          '⏮️ to go to the first page\n'
                          '◀️️ to go to the previous page\n'
                          '▶️ to go to the next page\n'
                          '⏩ to go to the last page\n'
                          'Note: some of them may not be available (e.g. can\'t go to the last page when you\'re '
                          'already there)\n\n'
                          'Additionally press:\n'
                          '💭 to see up to 15 words that haven\'t been interacted with for the longest time\n'
                          '📙 to change current vocabulary\n'
                          '━  to delete a word\n'
                          '↩️ to go back to the main menu\n'
                          'ℹ️ to open this informational center',
            'info_recall': 'Here you can see up to 15 words that haven\'t been interacted with for the longest time\n\n'
                           'To get another set of words press:\n'
                           '🔄 to refresh\n'
                           'Note: your vocabulary has to have at least 15 words to be able to refresh\n\n'
                           'Additionally press:\n'
                           '↩️ to go back to the word menu\n'
                           'ℹ️ to open this informational center',
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


def conjugate_oldest(lang, number):
    last_digit = number % 10
    last_two_digits = number % 100

    match lang:
        case 'en':
            return 'oldest'  # No change in English

        case 'ua':
            if last_digit == 1 and last_two_digits != 11:
                return 'найстаріше'
            elif last_digit in [2, 3, 4] and last_two_digits not in [12, 13, 14]:
                return 'найстаріші'
            else:
                return 'найстаріших'

        case 'pl':
            if number == 1:
                return 'najstarsze'
            elif last_digit in [2, 3, 4] and last_two_digits not in [12, 13, 14]:
                return 'najstarsze'
            else:
                return 'najstarszych'

        case _:
            raise ValueError('Invalid language')
