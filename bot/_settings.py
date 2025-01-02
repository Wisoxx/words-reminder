import database as db


def get_user_parameters(user):
    parameters = db.Users.get({"user_id": user}, include_column_names=True)
    return parameters
