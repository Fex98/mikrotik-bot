import os
from flask import Flask, request
import telebot

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# الطريقة الجديدة النظيفة (بدون رموز وعلامات استفهام - متوافقة تماماً مع جوالك)
@app.route('/send/<chat_id>/<text>')
def send_clean(chat_id, text):
    try:
        bot.send_message(chat_id, text)
        return "OK", 200
    except Exception as e:
        return str(e), 500

@app.route('/update', methods=['GET', 'POST'])
def webhook():
    try:
        # استقبال البيانات سواء عبر الرابط القديم أو الـ JSON
        chat_id = request.args.get('chat_id') or (request.json and request.json.get('chat_id'))
        text = request.args.get('text') or (request.json and request.json.get('text'))
        
        if chat_id and text:
            bot.send_message(chat_id, text)
            return "OK", 200
        else:
            return "Missing chat_id or text", 400
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
