import os
import threading
from flask import Flask, request
import telebot

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# متغيرات مؤقتة لتخزين حالة المودمات
modems_data = {
    "active": [],
    "disconnected": []
}

@app.route('/')
def home():
    return "Bot is running!"

# الطريقة الجديدة النظيفة لإرسال الرسائل
@app.route('/send/<chat_id>/<text>')
def send_clean(chat_id, text):
    try:
        bot.send_message(chat_id, text)
        return "OK", 200
    except Exception as e:
        return str(e), 500

# مسار استقبال بيانات المودمات من المايكروتك
@app.route('/update_modems', methods=['POST'])
def update_modems():
    try:
        data = request.json
        if data:
            modems_data['active'] = data.get('active', [])
            modems_data['disconnected'] = data.get('disconnected', [])
            return "Updated successfully", 200
        return "No data", 400
    except Exception as e:
        return str(e), 500

@app.route('/update', methods=['GET', 'POST'])
def webhook():
    try:
        chat_id = request.args.get('chat_id') or (request.json and request.json.get('chat_id'))
        text = request.args.get('text') or (request.json and request.json.get('text'))
        
        if chat_id and text:
            bot.send_message(chat_id, text)
            return "OK", 200
        else:
            return "Missing chat_id or text", 400
    except Exception as e:
        return str(e), 500

# معالجة تفاعل الأزرار وأمر start
@bot.message_handler(func=lambda message: True)
def handle_buttons(message):
    text = message.text
    if text == "/start":
        # إرسال لوحة المفاتيح والأزرار عند البدء
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("حالة الشبكة العامة")
        markup.row("المودمات المنقطعة", "المودمات الشغالة")
        bot.send_message(message.chat.id, "🚀 أهلاً بك في لوحة تحكم شبكة SKY_NET\nاختر من الأزرار أدناه لعرض التقارير اللحظية:", reply_markup=markup)
        
    elif "المودمات المنقطعة" in text:
        disc = modems_data.get('disconnected', [])
        if not disc:
            bot.send_message(message.chat.id, "⚠️ لا توجد مودمات منقطعة حالياً في القائمة الحية.\nتأكد من إرسال البيانات من المايكروتك إلى السيرفر.")
        else:
            msg = "🔴 المودمات المنقطعة:\n" + "\n".join(disc)
            bot.send_message(message.chat.id, msg)
            
    elif "المودمات الشغالة" in text:
        act = modems_data.get('active', [])
        if not act:
            bot.send_message(message.chat.id, "⚠️️ لا توجد مودمات شغالة حالياً في القائمة.")
        else:
            msg = "🟢 المودمات الشغالة:\n" + "\n".join(act)
            bot.send_message(message.chat.id, msg)
            
    elif "حالة الشبكة العامة" in text:
        act_count = len(modems_data.get('active', []))
        disc_count = len(modems_data.get('disconnected', []))
        report = f"📊 تقرير حالة الشبكة العامة:\n🟢 الشغالة: {act_count}\n🔴 المنقطعة: {disc_count}"
        bot.send_message(message.chat.id, report)

# تشغيل البوت في خلفية مستقلة لكي يستمع لتليجرام ويترك Flask يعمل للسيرفر
def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    # تشغيل بوت تليجرام في خيط (Thread) منفصل
    t = threading.Thread(target=run_bot)
    t.daemon = True
    t.start()
    
    # تشغيل سيرفر Flask
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
