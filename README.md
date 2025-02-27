# Word Recall Bot

[![Telegram](https://img.shields.io/badge/Telegram-Word_Recall_Bot-blue)](https://t.me/word_recall_bot)

**Word Recall Bot** is a personal word-learning assistant that helps you store and recall words at scheduled intervals. It supports multiple vocabularies, reminders, and a recall system that prevents repetitive words from appearing too frequently.

## Features

- 📚 **Multiple Vocabularies**: Organize words into different vocabularies.
- ⏰ **Reminders**: Set custom reminders to practice words at specific times.
- 📝 **Word Storage**: Add words with or without meanings.
- 🔄 **Recall System**: Prioritizes older words while introducing new ones gradually.
- 🌍 **Multi-language Support**: Interface available in English, Ukrainian, and Polish.
- ⚙️ **Customizable Settings**: Change language, toggle meaning visibility, and set time zones.
- 📈 **Smart Recall Algorithm**: Ensures a balanced mix of new and old words.

## Installation

This bot is hosted on **PythonAnywhere** and built with **Flask** and **Telepot**.
To set up a local development environment:

```sh
# Clone the repository
git clone https://github.com/Wisoxx/words-reminder.git
cd words-reminder

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## Configuration

1. **Set up Telegram bot**
   - Create a bot via [BotFather](https://t.me/BotFather) and obtain the API token.
2. **Set environment variables**
   - Create a `.env` file with the following:
     ```env
     TELEGRAM_TOKEN=your_telegram_bot_token
     SITE_URL=your_site_url
     SECRET=your_webhook_secret
     ```

## Usage

Start a conversation with the bot: [@word_recall_bot](https://t.me/word_recall_bot)

### Commands

- `/start` – Begin interaction and setup.
- `/menu` – Open main menu.
- `/help` – Show instructions.

## Smart Recall System

The recall system prevents the same words from appearing repeatedly. It uses:

- **Timestamps** 📅 to track when words were last recalled.
- **Recall Score** 📊 which increases each time a word is recalled.
- **Weighted Random Selection** 🎯 to balance new and old words.
- **Decay Factor** ⏳ to lower recall scores over time, preventing stagnation.

## Database Structure

The bot uses **SQLite** with the following tables:

- **Users**: Stores user preferences.
- **Vocabularies**: Manages user-created vocabularies.
- **Words**: Stores words and meanings.
- **Reminders**: Keeps track of scheduled word recalls.
- **Temp**: Temporary storage for ongoing user actions.

## Logging

- Logs are stored in `logs/app.log` using **RotatingFileHandler**.
- Flask provides an endpoint to view logs in a web browser at the `{SITE_URL}/{SECRET}/remind_all` endpoint.

## Deployment

1. **Set up on PythonAnywhere**
   - Create an account
   - Create and configure a **Flask web app**. For a detailed guide, refer to [Building a simple Telegram bot using PythonAnywhere](https://blog.pythonanywhere.com/148/).
   - Change WSGI file configuration to:
   ```python
   # This file contains the WSGI configuration required to serve up your
   # web application at http://<your-username>.pythonanywhere.com/
   # It works by setting the variable 'application' to a WSGI handler of some
   # description.
   
   import sys
   import os
   from dotenv import load_dotenv
   
   # add your project directory to the sys.path
   project_home = '/home/YOUR-USERNAME/mysite'
   if project_home not in sys.path:
       sys.path = [project_home] + sys.path
   
   project_folder = os.path.expanduser('~/mysite')
   load_dotenv(os.path.join(project_folder, '.env'))
   
   # import flask app but need to call it "application" for WSGI to work
   from flask_app import app as application  # noqa
   ```
   - Run commands mentioned in **Installation** in `/mysite` folder (`cd /mysite` first).

2. **Set up a scheduled task to call the `{SITE_URL}/{SECRET}/remind_all` endpoint.**

## Contributing

Feel free to submit issues or create pull requests. Contributions are welcome!

## License

MIT License © 2025 Bohdan Tavanov
