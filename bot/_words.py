import database as db


def add_word(self, user, vocabulary_id, word, meaning=None):
    return db.Words.add({"user_id": user, "vocabulary_id": vocabulary_id, "word": word, "meaning": meaning})


def delete_word(word_id=None, user=None, vocabulary_id=None, word=None):
    """
    Deletes a word based on the given conditions. word_id or user and vocabulary_id and word are required.

    :param word_id: Unique identifier of the word (optional)
    :param user: The ID of the user (required if word_id is not given)
    :param vocabulary_id: The vocabulary the word belongs to (required if word_id is not given)
    :param word: The word to delete (required if word_id is not given)
    :return: bool indicating success
    """
    if word_id:
        conditions = {"word_id": word_id}
    elif user and vocabulary_id and word:
        conditions = {"user_id": user, "vocabulary_id": vocabulary_id, "word": word}
    else:
        raise ValueError("You must provide either word_id, or user_id, vocabulary_id, and word.")

    return db.Words.delete(conditions)


def get_word_meaning(word_id=None, user=None, vocabulary_id=None, word=None):
    """
    Returns the meaning of the given word based on the given conditions. word_id or user and vocabulary_id and word
    are required.

    :param word_id: Unique identifier of the word (optional)
    :param user: The ID of the user (required if word_id is not given)
    :param vocabulary_id: The vocabulary the word belongs to (required if word_id is not given)
    :param word: The word to delete (required if word_id is not given)
    :return: str meaning of the given word
    """
    if word_id:
        conditions = {"word_id": word_id}
    elif user and vocabulary_id and word:
        conditions = {"user_id": user, "vocabulary_id": vocabulary_id, "word": word}
    else:
        raise ValueError("You must provide either word_id, or user_id, vocabulary_id, and word.")

    word_info = db.Words.get(conditions, include_column_names=True)

    if word_info:
        return word_info["meaning"]
    return None


def get_user_words(user, vocabulary_id):
    return db.Words.get({"user_id": user, "vocabulary_id": vocabulary_id})


def get_old_words(user, vocabulary_id, limit):
    pass
