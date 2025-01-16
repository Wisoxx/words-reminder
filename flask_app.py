from flask import Flask, request, jsonify
from bot import Bot, telepot
import urllib3
from urllib3.util.retry import Retry
from time import sleep
from bot._words import recall
from bot._reminders import _get_reminders_list_at
from bot.utils import get_hh_mm
from logger import setup_logger, process_logs
import os
from dotenv import load_dotenv


logger = setup_logger(__name__)


class LoggingRetry(Retry):  # overriding class to have logs when connection errors occur
    def __init__(self, *args, **kwargs):
        self.retry_count = 0
        super().__init__(*args, **kwargs)

    def increment(self, *args, **kwargs):
        self.retry_count += 1
        logger.warning(f"Retrying request {self.retry_count}")
        return super().increment(*args, **kwargs)


project_folder = os.path.expanduser('~/mysite')
load_dotenv(os.path.join(project_folder, '.env'))

proxy_url = "http://proxy.server:3128"
retry_strategy = Retry(
    total=5,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
)
telepot.api._pools = {
    'default': urllib3.ProxyManager(proxy_url=proxy_url, num_pools=3, maxsize=10, retries=retry_strategy, timeout=30),
}
telepot.api._onetime_pool_spec = (urllib3.ProxyManager, dict(proxy_url=proxy_url, num_pools=1, maxsize=1, retries=retry_strategy, timeout=30))

TOKEN = os.getenv("TELEGRAM_TOKEN")
SECRET = os.getenv("SECRET")
SITE = os.getenv("SITE_URL")

bot = Bot(TOKEN)
bot.setWebhook(SITE + SECRET, max_connections=1)

app = Flask(__name__)


@app.route(f'/{SECRET}', methods=["POST"])
def telegram_webhook():
    update = request.get_json()
    bot.handle_update(update)
    return "OK"


@app.route(f'/{SECRET}/logs', methods=["GET"])
def view_logs():
    return process_logs()


@app.route(f'/{SECRET}/remind_all', methods=["POST"])
def remind_all():
    logger.debug("Received remind request")
    try:
        reminders = _get_reminders_list_at(get_hh_mm())
        if len(reminders) > 0:
            for _, user, vocabulary_id, _, number_of_words in reminders:
                text, reply_markup = recall(user=user, vocabulary_id=vocabulary_id, limit=number_of_words)
                bot.deliver_message(user, text, reply_markup=reply_markup)
                sleep(34)  # Telegram allows 30 messages per second
            return jsonify({"status": "success", "message": "Reminders sent successfully!"}), 200
        else:
            return jsonify({"status": "success", "message": "No reminders found"}), 200

    except Exception as e:
        logger.critical(f"Error broadcasting reminders: {e}", exc_info=True)
        return jsonify({"status": "error", "message": "Failed to send reminders."}), 500
