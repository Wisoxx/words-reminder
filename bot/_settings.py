import database as db


def get_user_parameters(user):
    parameters = db.Users.get({"user_id": user}, include_column_names=True)
    del parameters["user_id"]  # user and user_id contains the same information, so it's redundant
    return parameters
