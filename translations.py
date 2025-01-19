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
            'select_vocabulary_to_delete': 'Send what vocabulary you want to delete?',
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
            # Misc
            'flag': '🇺🇦',
            'choose_category': 'Вибери категорію:',
            'cancel': 'Скасувати',
            'cancelled': 'Успішно скасовано',
            'add_back': 'Повернути',
            'delete': 'Видалити',
            'error': 'Щось пішло не так',
            'short_hours': 'год',
            'short_minutes': 'хв',
            'finish_setup': 'Спочатку потрібно завершити налаштування!',
            'setup_finished': 'Ви завершили налаштування! Щоб отримати більше інформації, введіть /help. Для доступу до'
                              ' меню введіть /menu. Якщо у вас виникли труднощі з навігацією меню, натисніть ℹ️ внизу '
                              'кожного меню, щоб отримати короткий огляд',
            'help': 'Я Word Recall, твій особистий зберігач слів! Надішли мені слова, які ти хочеш вивчити. Ти можеш'
                    ' додати значення, надіславши його у форматі "слово - значення". Без " - " увесь текст буде '
                    'розглядатися як одне слово. Ти можеш зберігати слова у різні словники (скільки завгодно створиш!)'
                    '. До кожного словника можна додати будь-яку кількість нагадувань на вибраний час, і я нагадаю тобі'
                    ' у встановлений час.\n\n'
                    'Введіть /menu, щоб відкрити меню. Якщо у вас виникли труднощі з навігацією меню, натисніть ℹ️ '
                    'внизу кожного меню, щоб отримати короткий огляд.',
            'unrecognized_message': 'Вибач, я не зрозумів це повідомлення. Спробуй щось інше',
            'unrecognized_command': 'Вибач, я не зрозумів цю команду. Спробуй /help або /menu',

            # Reminders
            'reminders': 'Нагадування',
            'reminders_heading': '      Нагадування',
            'adding_reminder': 'Додавання нагадування',
            'deleting_reminder': 'Видалення нагадування',
            'vocabulary_name': 'Назва словника',
            'time': 'Час',
            'number_of_words': 'Кількість слів',
            'reminder_duplicate': 'У тебе вже є нагадування для "{vocabulary_name}" о {time}',
            'reminder_set': 'Побачимося о {time}! Я нагадаю тобі {number_of_words} {conjugated_word} із '
                            '"{vocabulary_name}" :)',
            'reminder_deleted': 'Нагадування о {time} із "{vocabulary_name}" успішно видалено',
            'no_reminders': 'У тебе немає\n нагадувань',
            'info_reminders': 'Тут ти можеш переглянути нагадування, пов’язані з усіма твоїми словниками. Вони '
                              'згруповані за словниками та відсортовані за часом. Поруч з кожним з них ти побачиш, '
                              'скільки слів вони показуватимуть, якщо твій словник буде мати достатньо слів\n\n'
                              'Щоб внести зміни, натисни:\n'
                              '━ щоб видалити нагадування\n'
                              '✚ щоб встановити нагадування\n\n'
                              'Додатково натисни:\n'
                              '↩️ щоб повернутися в головне меню\n'
                              'ℹ️ щоб відкрити цей інформаційний центр',

            # Settings
            'settings': 'Налаштування',
            'settings_heading': '                              Налаштування',
            'language': 'Мова',
            'hide_meaning': 'Приховувати значення',
            'timezone': 'Часовий пояс',
            'choose_lang': '🇺🇦 Виберіть свою мову',
            'lang_set': 'Налаштування мови оновлено',
            'setup_timezone': 'Зрівняй час нижче з твоїм поточним часом. Після цього натисни на час, щоб зберегти '
                              'твій часовий пояс',
            'timezone_set': 'Часовий пояс встановлено на UTC{timezone:+} ({time})',
            'info_settings': 'Тут ти можеш переглянути свої поточні налаштування\n\n'
                             'Щоб внести зміни, натисни:\n'
                             '🌎 для зміни мови інтерфейсу\n'
                             '👁 для перемикання приховування значень слів\n'
                             '🕓 для зміни часового поясу\n\n'
                             'Додатково натисни:\n'
                             '↩️ щоб повернутися в головне меню\n'
                             'ℹ️ щоб відкрити цей інформаційний центр',

            # Vocabularies
            'vocabularies': 'Словники',
            'vocabularies_heading': '                              Словники',
            'change_vocabulary': 'Вибери словник, з яким хочеш працювати',
            'name_vocabulary': 'Як ти хочеш назвати свій новий словник?',
            'vocabulary_duplicate': 'У тебе вже є словник із назвою "{vocabulary_name}". Спробуй щось інше',
            'vocabulary_created': 'Успішно створено словник "{vocabulary_name}"',
            'select_vocabulary_to_delete': 'Напиши який словник ти хочеш видалити',
            'confirm_vocabulary_deletion': 'Ти впевнений, що хочеш назавжди видалити "{vocabulary_name}" і все, що з '
                                           'ним пов’язано, включаючи слова та нагадування?',
            'vocabulary_not_found': 'У тебе немає словника з назвою "{vocabulary_name}"',
            'vocabulary_deleted': 'Успішно видалено словник "{vocabulary_name}"',
            'no_vocabularies': 'Ой-ой, це був тівй останній словник! Щоб продовжити користуватися моїми послугами, тобі'
                               ' потрібно створити новий!',
            'vocabulary_deletion_cancelled': 'Успішно скасовано видалення словника',
            'info_vocabularies': 'Тут ти можеш переглянути всі свої словники та кількість слів у них. Твій поточний '
                                 'словник підкреслений\n\n'
                                 'Щоб внести зміни, натисни:\n'
                                 '━   щоб видалити словник\n'
                                 '📙 щоб вибрати інший поточний словник\n'
                                 '✚   щоб створити ще один словник\n\n'
                                 'Додатково натисни:\n'
                                 '↩️ щоб повернутися в головне меню\n'
                                 'ℹ️ щоб відкрити цей інформаційний центр',

            # Words
            'words': 'Слова',
            'word_duplicate': 'У тебе вже є "{word}" у "{vocabulary_name}"',
            'word_added': 'Успішно додано "{word}" у "{vocabulary_name}"',
            'choose_word_to_delete': 'Надішли слово, яке ти хочеш видалити',
            'word_deleted': 'Успішно видалено "{word}" із "{vocabulary_name}"',
            'no_words_to_delete': 'Словник порожній. Немає чого видаляти',
            'word_not_found': '"{word}" не знайдено у "{vocabulary_name}"',
            'word_info_expired': 'Інформація про це слово більше недоступна. Ти все ще можеш додати його вручну',
            'no_words': '*🦗 звуки цвіркунів🦗*',
            'recall_no_words': 'На жаль, у цьому словнику немає слів для практики',
            'practice_time': 'Час для практики!',
            'oldest_words': 'Ось {to_be} {word_count} {conjugated_oldest} {conjugated_word} із "{vocabulary_name}" '
                            'для повторення',
            'info_words': 'Тут ти можеш переглянути слова, додані до твого поточного словника\n\n'
                          'Щоб переміщатися по словнику, натисни:\n'
                          '⏮️ щоб перейти на першу сторінку\n'
                          '◀️️ щоб перейти на попередню сторінку\n'
                          '▶️ щоб перейти на наступну сторінку\n'
                          '⏩ щоб перейти на останню сторінку\n'
                          'Примітка: деякі з них можуть бути недоступні (наприклад, неможливо перейти до останньої '
                          'сторінки, якщо ти вже там)\n\n'
                          'Додатково натисни:\n'
                          '💭 щоб переглянути до 15 слів, з якими ти не взаємодіяв найдовше\n'
                          '📙 щоб змінити поточний словник\n'
                          '━   щоб видалити слово\n'
                          '↩️ щоб повернутися в головне меню\n'
                          'ℹ️ щоб відкрити цей інформаційний центр',
            'info_recall': 'Тут ти можеш переглянути до 15 слів, з якими ти не взаємодіяв найдовше\n\n'
                           'Щоб отримати інший набір слів, натисни:\n'
                           '🔄 для оновлення\n'
                           'Примітка: ваш словник має містити щонайменше 15 слів, щоб можна було оновити\n\n'
                           'Додатково натисни:\n'
                           '↩️ щоб повернутися до меню слів\n'
                           'ℹ️ щоб відкрити цей інформаційний центр',
        },
        'pl': {
            # Misc
            'flag': '🇵🇱',
            'choose_category': 'Wybierz kategorię:',
            'cancel': 'Anuluj',
            'cancelled': 'Pomyślnie anulowano',
            'add_back': 'Przywróć',
            'delete': 'Usuń',
            'error': "Coś poszło nie tak",
            'short_hours': 'h',
            'short_minutes': 'min',
            'finish_setup': 'Najpierw musisz zakończyć konfigurację!',
            'setup_finished': 'Zakończyłeś konfigurację! Aby uzyskać więcej informacji, wpisz /help. Aby uzyskać dostęp'
                              ' do menu, wpisz /menu. Jeśli masz trudności z nawigacją w menu, naciśnij ℹ️ na dole '
                              'każdego menu, aby uzyskać szybki przegląd',
            'help': 'Jestem Word Recall, twoim osobistym pomocnikiem w nauce słów! Wyślij mi słowa, których chcesz się '
                    'nauczyć. Możesz opcjonalnie dodać znaczenie, wysyłając je w formacie "słowo - znaczenie". Bez '
                    '" - " cały tekst zostanie potraktowany jako jedno słowo. Możesz zapisywać słowa w różnych '
                    'słownikach (tworząc dowolną ich liczbę!). Do każdego słownika możesz przypisać dowolną liczbę '
                    'przypomnień w dowolnym czasie, a ja przypomnę ci w wybranym czasie\n\n'
                    'Wpisz /menu, aby otworzyć menu. Jeśli masz trudności z nawigacją w menu, naciśnij ℹ️ na dole '
                    'każdego menu, aby uzyskać szybki przegląd',
            'unrecognized_message': 'Przepraszam, nie rozumiem tej wiadomości. Spróbuj czegoś innego',
            'unrecognized_command': 'Przepraszam, nie rozumiem tej komendy. Spróbuj /help lub /menu',
            # Reminders
            'reminders': 'Przypomnienia',
            'reminders_heading': '    Przypomnienia',
            'adding_reminder': 'Dodawanie przypomnienia',
            'deleting_reminder': 'Usuwanie przypomnienia',
            'vocabulary_name': 'Nazwa słownika',
            'time': 'Czas',
            'number_of_words': 'Liczba słów',
            'reminder_duplicate': 'Masz już przypomnienie dla "{vocabulary_name}" o {time}',
            'reminder_set': 'Do zobaczenia o {time}! Przypomnę ci {number_of_words} {conjugated_word} z '
                            '"{vocabulary_name}" :)',
            'reminder_deleted': 'Pomyślnie usunięto przypomnienie o {time} z "{vocabulary_name}"',
            'no_reminders': 'Nie masz żadnych przypomnień',
            'info_reminders': 'Tutaj możesz przeglądać przypomnienia powiązane ze wszystkimi Twoimi słownikami. Są one '
                              'pogrupowane według słowników i posortowane według czasu. Obok każdego zobaczysz, ile '
                              'słów pokażą, jeśli Twój słownik będzie wystarczająco długi\n\n'
                              'Aby wprowadzić zmiany, naciśnij:\n'
                              '━  aby usunąć przypomnienie\n'
                              '✚  aby ustawić przypomnienie\n\n'
                              'Dodatkowo naciśnij:\n'
                              '↩️ aby wrócić do menu głównego\n'
                              'ℹ️ aby otworzyć to centrum informacyjne',
            # Settings
            'settings': 'Ustawienia',
            'settings_heading': '                            Ustawienia',
            'language': 'Język',
            'hide_meaning': 'Ukryj znaczenia',
            'timezone': 'Strefa czasowa',
            'choose_lang': '🇵🇱 Wybierz swój język',
            'lang_set': 'Preferencje językowe zostały zaktualizowane',
            'setup_timezone': 'Dopasuj czas poniżej do swojego aktualnego czasu. Po tym naciśnij czas, aby zapisać '
                              'swoją strefę czasową',
            'timezone_set': 'Strefa czasowa ustawiona na UTC{timezone:+} ({time})',
            'info_settings': 'Tutaj możesz przeglądać swoje aktualne ustawienia\n\n'
                             'Aby wprowadzić zmiany, naciśnij:\n'
                             '🌎 aby zmienić język interfejsu\n'
                             '👁 aby przełączyć ukrywanie znaczeń słów\n'
                             '🕓 aby zmienić swoją strefę czasową\n\n'
                             'Dodatkowo naciśnij:\n'
                             '↩️ aby wrócić do menu głównego\n'
                             'ℹ️ aby otworzyć to centrum informacyjne',
            # Vocabularies
            'vocabularies': 'Słowniki',
            'vocabularies_heading': '                                Słowniki',
            'change_vocabulary': 'Wybierz który słownik ustawić jako bieżący',
            'name_vocabulary': 'Jak chcesz nazwać swój nowy słownik?',
            'vocabulary_duplicate': 'Masz już słownik o nazwie "{vocabulary_name}". Spróbuj czegoś innego',
            'vocabulary_created': 'Pomyślnie utworzono słownik "{vocabulary_name}"',
            'select_vocabulary_to_delete': 'Napisz który słownik chcesz usunąć',
            'confirm_vocabulary_deletion': 'Czy na pewno chcesz trwale usunąć "{vocabulary_name}" i wszystko z nim '
                                           'związane, w tym słowa i przypomnienia?',
            'vocabulary_not_found': 'Nie masz słownika o nazwie "{vocabulary_name}"',
            'vocabulary_deleted': 'Pomyślnie usunięto słownik "{vocabulary_name}"',
            'no_vocabularies': 'Ups, to był Twój ostatni słownik! Aby dalej korzystać z moich usług, musisz utworzyć '
                               'nowy!',
            'vocabulary_deletion_cancelled': 'Pomyślnie anulowano usunięcie słownika',
            'info_vocabularies': 'Tutaj możesz przeglądać wszystkie swoje słowniki i ich liczbę słów. Twój aktualny '
                                 'słownik jest podkreślony\n\n'
                                 'Aby wprowadzić zmiany, naciśnij:\n'
                                 '━  aby usunąć słownik\n'
                                 '📙 aby zmienić bieżący słownik\n'
                                 '✚  aby utworzyć nowy słownik\n\n'
                                 'Dodatkowo naciśnij:\n'
                                 '↩️ aby wrócić do menu głównego\n'
                                 'ℹ️ aby otworzyć to centrum informacyjne',
            # Words
            'words': 'Słowa',
            'word_duplicate': 'Masz już "{word}" w "{vocabulary_name}"',
            'word_added': 'Pomyślnie dodano "{word}" do "{vocabulary_name}"',
            'choose_word_to_delete': 'Wyślij mi słowo, które chcesz usunąć',
            'word_deleted': 'Pomyślnie usunięto "{word}" z "{vocabulary_name}"',
            'no_words_to_delete': 'Słownik jest pusty. Nie ma nic do usunięcia',
            'word_not_found': '"{word}" nie znaleziono w "{vocabulary_name}"',
            'word_info_expired': 'Informacje o tym słowie nie są już dostępne. Możesz go nadal dodać ręcznie',
            'no_words': '*🦗dźwięki świerszczy🦗*',
            'recall_no_words': 'Niestety, w tym słowniku nie ma słów do ćwiczenia',
            'practice_time': 'Czas na ćwiczenia!',
            'oldest_words': 'Oto {to_be} {word_count} {conjugated_oldest} {conjugated_word} z "{vocabulary_name}" do '
                            'przypomnienia',
            'info_words': 'Tutaj możesz przeglądać słowa dodane do swojego aktualnego słownika\n\n'
                          'Aby poruszać się po swoim słowniku, naciśnij:\n'
                          '⏮️ aby przejść do pierwszej strony\n'
                          '◀️️ aby przejść do poprzedniej strony\n'
                          '▶️ aby przejść do następnej strony\n'
                          '⏩ aby przejść do ostatniej strony\n'
                          'Uwaga: niektóre z nich mogą być niedostępne (np. nie można przejść do ostatniej strony, '
                          'jeśli już tam jesteś)\n\n'
                          'Dodatkowo naciśnij:\n'
                          '💭 aby zobaczyć do 15 słów, które nie były używane najdłużej\n'
                          '📙 aby zmienić aktualny słownik\n'
                          '━  aby usunąć słowo\n'
                          '↩️ aby wrócić do menu głównego\n'
                          'ℹ️ aby otworzyć to centrum informacyjne',
            'info_recall': 'Tutaj możesz zobaczyć do 15 słów, które nie były używane najdłużej\n\n'
                           'Aby uzyskać kolejny zestaw słów, naciśnij:\n'
                           '🔄 aby odświeżyć\n'
                           'Uwaga: Twój słownik musi zawierać co najmniej 15 słów, żeby można było odświeżyć\n\n'
                           'Dodatkowo naciśnij:\n'
                           '↩️ aby wrócić do menu słów\n'
                           'ℹ️ aby otworzyć to centrum informacyjne',

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
