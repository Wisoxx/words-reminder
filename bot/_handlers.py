def handle_message(self, user, update):
    if "text" in update["message"]:
        text = update["message"]["text"]
        match text:
            case "/test":
                self.deliver_message(user, "Test Message", add_cancel_button=True, lang="en")

            case "/menu":
                self.menu(user)

            case _:
                self.deliver_message(user, "From the web: you said '{}'".format(text))

    else:
        self.deliver_message(user, "From the web: sorry, I didn't understand that kind of message")


def handle_callback_query(self, user,  update):
    callback_data = update["callback_query"]["data"]
    self.deliver_message(user, callback_data)


def handle_chat_member_status(self, user,  update):
    raise Exception("Blocked or unblocked")
