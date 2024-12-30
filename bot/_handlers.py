import database as db
from logger import setup_logger


logger = setup_logger(__name__)


def handle_message(self, user, update):
    if "text" in update["message"]:
        text = update["message"]["text"]
        match text:
            case "/test":
                self.deliver_message(user, "Test Message", add_cancel_button=True, lang="en")

            case "/menu":
                self.menu(user)

            case "/recall":
                pass  # TODO

            case _:
                self.deliver_message(user, "From the web: you said '{}'".format(text))

    else:
        self.deliver_message(user, "From the web: sorry, I didn't understand that kind of message")


def handle_callback_query(self, user,  update):
    callback_data = update["callback_query"]["data"]
    self.deliver_message(user, callback_data)


def handle_chat_member_status(self, user,  update):
    old_status = update["my_chat_member"]["old_chat_member"]["status"]
    new_status = update["my_chat_member"]["new_chat_member"]["status"]

    if old_status == "member" and new_status == "kicked":
        logger.info(f"User {user} has blocked the bot")
        db.Users.delete({"user_id": user})  # all data is linked to user_id and will be deleted too
        logger.info(f"All records of {user} have been deleted")
    elif old_status == "kicked" and new_status == "member":
        logger.info(f"User {user} has unblocked the bot")
