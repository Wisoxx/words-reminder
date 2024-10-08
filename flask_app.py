from flask import Flask, request
from bot import Bot, telepot
import urllib3
import os

proxy_url = "http://proxy.server:3128"
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=False, timeout=30),
}
telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=False, timeout=30))

TOKEN = os.getenv("TELEGRAM_TOKEN")
SECRET = os.getenv("SECRET")
SITE = os.getenv("SITE_URL")

bot = Bot(TOKEN)
bot.setWebhook(SITE + SECRET, max_connections=1)

app = Flask(__name__)


@app.route('/{}'.format(SECRET), methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    bot.handle_update(update)
    return "OK"
