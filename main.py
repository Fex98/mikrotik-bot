import os
from flask import Flask, request
import telebot

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/update', methods=['POST'])
def webhook():
    try:
        data = request.json
        chat_id = data.get('chat_id')
        text = data.get('text')
        
        if chat_id and text:
            bot.send_message(chat_id, text)
            return "OK", 200
        else:
            return "Invalid data", 400
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
