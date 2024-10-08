import telepot


class Bot:
    def __init__(self, token):
        self.bot = telepot.Bot(token)

    def __getattr__(self, name):
        return getattr(self.bot, name)

    def handle_update(self, update):
        if "message" in update:
            chat_id = update["message"]["chat"]["id"]
            if "text" in update["message"]:
                text = update["message"]["text"]
                self.sendMessage(chat_id, "From the web: you said '{}'".format(text))
            else:
                self.sendMessage(chat_id, "From the web: sorry, I didn't understand that kind of message")