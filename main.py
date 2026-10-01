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
    data = request.json
    # معالجة بيانات المايكروتك وإرسالها عبر البوت #
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
