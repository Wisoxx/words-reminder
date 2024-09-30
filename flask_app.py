from flask import Flask, request
import telepot
import urllib3
from dotenv import load_dotenv
import os

proxy_url = "http://proxy.server:3128"
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
}
telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
SECRET = os.getenv("SECRET")
SITE = os.getenv("SITE_URL")

bot = telepot.Bot(TOKEN)
bot.setWebhook(SITE + SECRET, max_connections=1)

app = Flask(__name__)


@app.route('/{}'.format(SECRET), methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    if "message" in update:
        chat_id = update["message"]["chat"]["id"]
        if "text" in update["message"]:
            text = update["message"]["text"]
            bot.sendMessage(chat_id, "From the web: you said '{}'".format(text))
        else:
            bot.sendMessage(chat_id, "From the web: sorry, I didn't understand that kind of message")
    return "OK"
