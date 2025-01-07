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
            'vocabulary': 'Vocabulary',
            'settings': 'Settings',
            'cancel': 'Cancel',
            'add_back': 'Add back',
            'delete': 'Delete',
            'replace': 'Replace',
            'info_words': 'info_words',
            'info_reminders': 'info_reminders',
            'info_vocabularies': 'info_vocabularies',
            'info_settings': 'info_settings',
            'test': "Hi {name}",
            'error': "Something went wrong",
        },
        'ua': {
            'flag': '🇺🇦',
            'choose_lang': '🇺🇦 Вибери свою мову',
            'lang_set': 'Налаштування мови оновлено',
            'choose_category': 'Вибери категорію:',
        },
        'pl': {
            'flag': '🇵🇱',
            'choose_lang': '🇵🇱 Wybierz swój język',
            'lang_set': 'Ustawienia językowe zostały zmienione',
            'choose_category': 'Wybierz kategorię:',

        }
    }
    lang = "uk" if lang == "ru" else lang  # change russian to ukrainian
    lang = lang if lang in languages else "en"  # default lang is english
    translation = translations[lang][key]
    if values:
        return translation.format(**values)
    return translation
