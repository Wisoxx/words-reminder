import database as db
from ._settings import get_user_parameters
from ._enums import TaskStatus


def create_vocabulary(user, vocabulary_name):
    if db.Vocabularies.add({"vocabulary_name": vocabulary_name, "user_id": user})[0]:
        return TaskStatus.SUCCESS
    return TaskStatus.FAILURE


def set_current_vocabulary(user, vocabulary_id):
    if db.Users.set({"user_id": user}, {"current_vocabulary_id": vocabulary_id}):
        return TaskStatus.SUCCESS
    return TaskStatus.FAILURE


def delete_vocabulary(user, vocabulary_id=None, vocabulary_name=None):
    """
    Deletes a vocabulary based on the given conditions. vocabulary_id or user and vocabulary_name are required.

    :param vocabulary_id: Unique identifier of the vocabulary (optional)
    :param user: The ID of the user
    :param vocabulary_name: The name of the vocabulary to delete (required if vocabulary_id is not given)
    :return: bool indicating success
    """
    if vocabulary_id:
        conditions = {"vocabulary_id": vocabulary_id}
    elif user and vocabulary_name:
        conditions = {"user_id": user, "vocabulary_name": vocabulary_name}
    else:
        raise ValueError("You must provide either vocabulary_id, or user_id and vocabulary_name.")

    result = db.Vocabularies.delete(conditions)

    if get_user_parameters(user)["current_vocabulary_id"] is None:
        return TaskStatus.NO_VOCABULARY

    if result:
        return TaskStatus.SUCCESS
    return TaskStatus.FAILURE
